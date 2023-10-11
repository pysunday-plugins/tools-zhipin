# coding: utf-8
import time
import random
import json
import os
import argparse
from copy import deepcopy
from sunday.tools.zhipin.zhipin import ZhipinWeb, Zhipin
from sunday.tools.zhipin.message import chatProtocolDecode
from sunday.tools.zhipin.handler import presenceHandler, textHandler, iqHandler, readHandler
from sunday.core import Logger, getParser, getParserDefault
from pydash import get
from sunday.tools.zhipin.initialize import robotInit
from sunday.tools.zhipin.meta_class import Mqtt
from sunday.tools.zhipin.error import ZhipinError

CMDINFO = {
    "version": '0.0.1',
    "description": "zhipin聊天工具",
    "epilog": """
使用案例:
    %(prog)s --robot --config
    %(prog)s --robot --config /path/to/name.json --message-out /path/to/message.log
    %(prog)s --robot --config /path/to/name.json --playback --messsage-in /path/to/message.log
    """,
    'params': {
        'DEFAULT': [
            {
                'name': ['--config'],
                'dest': 'msgConfigFile',
                'metavar': 'FILE',
                'help': '消息映射的json文件',
                'nargs': 1,
                'type': argparse.FileType('r')
            },
            {
                'name': ['--message-in'],
                'dest': 'msgCacheFileIn',
                'metavar': 'FILE',
                'help': '读取消息文件用于回放使用，默认为执行目录下的message.cache.log文件',
                'const': './message.cache.log',
                'nargs': '?',
                'type': argparse.FileType('r')
            },
            {
                'name': ['--message-out'],
                'dest': 'msgCacheFileOut',
                'metavar': 'FILE',
                'help': '消息保存文件，用于之后回放使用，默认为执行目录下的message.cache.log文件',
                'const': './message.cache.log',
                'nargs': '?',
                'type': argparse.FileType('w')
            },
            {
                'name': ['--robot'],
                'dest': 'isRobot',
                'help': '是否使用机器人回复消息',
                'default': False,
                'action': 'store_true'
            },
            {
                'name': ['--robot-open'],
                'dest': 'isRobotDefaultOpen',
                'help': '是否默认开启智能回复',
                'default': False,
                'action': 'store_true'
            },
            {
                'name': ['-t', '--test-name'],
                'help': '测试标签名称, 取examples目录下的文件名',
                'dest': 'testName',
            },
        ]
    }
}

selfFlagKey = '@selfflag'

defaultTip = {
    'rebotTip': '回复数字启用对应聊天机器人\n[1000] ChatGPT\n[1001] 小i\n[1002] 茉莉\n[1003] 青云客\n[1004] 关闭聊天机器人',
    'rebotMoli': '已开启聊天机器人，回复信息由茉莉提供',
    'rebotQingyunke': '已开启聊天机器人，回复信息由青云客提供',
    'rebotXiaoi': '已开启聊天机器人，回复信息由小i提供',
    'rebotChatGPT': '已开启聊天机器人，回复信息由ChatGPT提供',
    'rebotClose': '已关闭聊天机器人',
    'applicationResume': '这得主人自己决策，稍等哈',
    'notText': '机器人暂时只看得懂文字哦',
    'firstTip': '尊敬的Boss %s 您好!\n本人积极找工作中，您可回复对应数字自助获取我的信息，也可开启聊天机器人体验，注：可使用ChatGPT！\n\n%s\n\n[100] 选择机器人\n[101] 重发导览信息\n\n请先自助了解后再索要简历!'
}

class ZhipinClient(Mqtt):
    def __init__(self, session=None, msgConfigJson=None, **params):
        self.__dict__.update(getParserDefault(CMDINFO))
        self.__dict__.update(params)
        Mqtt.__init__(self)
        self.session = session
        self.msgConfigJson = msgConfigJson

        # zhipin登录交互
        self.zhipin = None
        # 即时通讯客户端
        self.client = None
        # 回复模版对象
        self.selfMessageObj = {}
        # 传入机器人类型及消息文本，请求对应机器人答复
        self.robotAsk = None
        self.cache_data = {}

    def bossConfig(self, uid, key=None, val=None):
        if key is None or uid not in self.cache_data:
            self.cache_data[uid] = {
                # 聊天机器人类型
                'robot': False,
                # 是否发送提示，提示只主动发送一次
                'isSendTip': False,
            }
        if key in self.cache_data[uid]:
            if val is not None:
                self.cache_data[uid][key] = val() if callable(val) else val
            return self.cache_data[uid][key]
        else:
            return lambda val: self.cache_data[uid].update({ key: val })

    def isSelf(self, uid):
        return int(self.zhipin.getUserInfo().get('userId')) == int(uid)

    def prevMsgParser(self, text):
        if self.msgCacheFileOut and not self.msgCacheFileOut and not self.testName:
            # 消息写入文件
            self.msgCacheFileOut.write(text + '\n')


    def parser_1_1_1(self, msg):
        body_text = get(msg, 'body.text').strip()
        if self.isSelf(get(msg, 'from.uid')):
            if body_text.find(selfFlagKey) == 0:
                new_msg = deepcopy(msg)
                to = new_msg.get('to')
                new_msg['to'] = new_msg['from']
                new_msg['from'] = to
                new_msg['selfflag'] = True
                new_msg['body']['text'] = body_text[len(selfFlagKey):].strip()
                self.logger.warning('修改自测数据，重新执行')
                return self.parser_1_1_1(new_msg)
            self.logger.warning('消息为自己发送，跳出')
            return
        text = ''
        bossId = get(msg, 'from.uid')
        bossName = get(msg, 'from.name')
        if body_text == '100':
            text = defaultTip['rebotTip']
        elif body_text == '1000':
            text = defaultTip['rebotChatGPT']
            self.bossConfig(bossId, 'robot', 'chatgpt')
        elif body_text == '1001':
            text = defaultTip['rebotXiaoi']
            self.bossConfig(bossId, 'robot', 'xiaoi')
        elif body_text == '1002':
            text = defaultTip['rebotMoli']
            self.bossConfig(bossId, 'robot', 'moli')
        elif body_text == '1003':
            text = defaultTip['rebotQingyunke']
            self.bossConfig(bossId, 'robot', 'qingyunke')
        elif body_text == '1004':
            text = defaultTip['rebotClose']
            self.bossConfig(bossId, 'robot', False)
        elif body_text == '101':
            text = defaultTip['firstTip'] % (get(msg, 'from.name'), self.selfMessageObj['tip'])
        elif self.selfMessageObj.get(body_text):
            # 配置指令
            text = body_text
            while self.selfMessageObj.get(text) is not None:
                text = self.selfMessageObj.get(text)
        elif self.bossConfig(bossId, 'robot') != False:
            text = self.robotAsk(self.bossConfig(bossId, 'robot'), body_text, bossId, bossName)
        if text:
            self.sendMessage(text, msg)

    def parser_1_1_7(self, msg):
        text = defaultTip['applicationResume']
        self.sendMessage(text, msg)

    def parser_1_1_20(self, msg):
        if self.isSelf(get(msg, 'from.uid')):
            self.logger.warning('消息为自己发送，跳出')
            return
        text = defaultTip['notText']
        self.sendMessage(text, msg)

    def parser_1_3_1(self, msg):
        pass
        # self.parser_1_1_1(msg)

    def parser_1_3_4(self, msg):
        pass

    def parser_1_3_8(self, msg):
        if self.isSelf(get(msg, 'from.uid')):
            self.logger.warning('消息为自己发送，跳出')
            return
        bossId = int(get(msg, 'from.uid'))
        if not bossId: return
        isSendTip = self.bossConfig(bossId, 'isSendTip')
        if isSendTip:
            # 已经发送过提示
            return
        self.bossConfig(bossId, 'isSendTip', True)
        text = defaultTip['firstTip'] % (get(msg, 'from.name'), self.selfMessageObj['tip'])
        self.sendMessage(text, msg)

    def parser_1_4_15(self, msg):
        pass

    def parser_1_4_16(self, msg):
        pass

    def parser_4(self, payload):
        pass

    def parser_6(self, payload):
        uid = int(get(payload, 'messageRead.0.userId') or 0)
        mid = int(get(payload, 'messageRead.0.messageId') or 0)
        message = self.zhipin.getHistoryMsg(uid, mid=mid)
        if message:
            self.logger.info('消息已查看(%s): %s' % (get(message, 'to.name'), message.get('pushText')))

    def sendMessage(self, text, msg):
        # 发送消息
        selfflag = msg.get('selfflag', False)
        origin = msg.get('to')
        target = msg.get('from')
        (boss, job, *_) = self.zhipin.bossdata(target.get('uid'))
        if not boss:
            self.logger.error('uid置换encryptBossId失败')
            return
        (data, buff) = textHandler(
            text,
            origin,
            {
                **target,
                'encryptUid': boss.get('encryptBossId')
            },
            self.zhipin.getUserInfo()
        )
        self.logger.debug('自动回复消息: \n%s' % text)
        self.logger.error('发送消息::sendMessage\n%s' % str(data))
        # if selfflag: self.send('chat', buff)
        self.send('chat', buff)

    def runByCache(self):
        if not self.msgCacheFileIn:
            self.logger.error('回放模式需要显式调用参数--message-in')
            return
        for msg in self.msgCacheFileIn.readlines():
            if not msg: continue
            payload = json.loads(msg)
            self.parser(payload)

    def runByExample(self):
        example_path = os.path.abspath(os.path.join(__file__, f'../examples/{self.testName}.json'))
        if not os.path.exists(example_path): raise ZhipinError(10000, other=self.testName)
        payload = json.load(open(example_path, 'r'))
        self.parser(payload)

    def init(self):
        self.robotAsk = robotInit(os.path.dirname(os.path.abspath(__file__)))
        self.zhipin = ZhipinWeb(self.session) if self.session else Zhipin()
        # 初始化聊天服务客户端
        if not self.msgCacheFileIn and not self.testName:
            self.mqttInit(self.zhipin)
        # 初始化智能聊天机器人
        if self.msgConfigFile:
            # 解析回复模版
            try:
                selfMessageStr = self.msgConfigFile[0].read()
                self.selfMessageObj = json.loads(selfMessageStr)
            except Exception as e:
                self.logger.error('消息回复模版解析失败，请检查文件%s内容是否为JSON格式'
                        % self.msgConfigFile.name)
        if self.msgConfigJson:
            # 解析回复字串
            self.selfMessageObj = self.msgConfigJson

    def run(self):
        self.init()
        try:
            if self.client:
                self.client.loop_forever()
            elif self.msgCacheFileIn:
                self.runByCache()
            elif self.testName:
                self.runByExample()
        except Exception as e:
            print('Error looping')
            print(e)
        finally:
            self.client and self.client.disconnect()
            self.msgCacheFileIn and self.msgCacheFileIn.close()
            self.msgCacheFileOut and self.msgCacheFileOut.close()
            self.logger.warning('如果程序未退出可能是robot还在心跳，可按键Ctrl + c终止程序执行')


def runcmd():
    parser = getParser(**CMDINFO)
    handle = parser.parse_args(namespace=ZhipinClient())
    handle.run()

if __name__ == "__main__":
    runcmd()


