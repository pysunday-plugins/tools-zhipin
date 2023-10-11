import json, os, random
from sunday.core import Logger, getParser
from sunday.core import Fetch
from pydash import get
from sunday.tools.zhipin.message import chatProtocolDecode
from sunday.tools.zhipin.initialize import mqttInit

def randomStr(num = 16, rangeNum = 16):
    """生成随机字符串，num为目标字符串长度，rangeNum为字符挑选范围"""
    text = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    ans = [''] * num
    for i in range(num):
        ans[i] = text[random.randint(0, rangeNum - 1)]
    return ''.join(ans)

class Mqtt:
    def __init__(self):
        self.fetch = Fetch()
        self.logger = Logger('ZHIPIN MQTT').getLogger()

    def mqttInit(self, zhipin):
        self.client = mqttInit(
            clientId="ws-" + randomStr(),
            url='ws.zhipin.com',
            port=443,
            path='/chatws',
            username=zhipin.getUserInfo()['token'] + '|0',
            password=zhipin.getPassword(),
            cookies=zhipin.getCookies(),
            on_connect=self.on_connect,
            on_message=self.on_message,
            logger=Logger('MQTT INIT').getLogger(),
            isProxy=False)

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("MQTT连接成功, 连接状态: %d" % rc)

    def on_message(self, client, userdata, message):
        self.logger.info('接收到消息, topic: %s, qos: %d, flag: %d' %
                (message.topic, message.qos, message.retain))
        try:
            payload = chatProtocolDecode(message.payload)
            self.parser(payload)
        except Exception as e:
            self.logger.error('消息解码失败!')
            self.logger.exception(e)

    def send(self, topic, payload=None, qos=1, retain=True):
        if self.client: self.client.publish(topic, payload, qos, retain)

    def prevMsgParser(self, text):
        """
        消息处理前执行
        """
        pass

    def parser(self, payload):
        text = json.dumps(payload, ensure_ascii=False)
        self.prevMsgParser(text)
        self.logger.debug('消息数据: %s' % text)
        # self.fetch.post('https://gptgoto.com/api/tools/respdata', headers={ 'Content-Type': 'application/json;charset=UTF-8' }, data=text)
        key = payload.get('type')
        try:
            funcname = f'parser_{key}'
            self.logger.info('消息类型: %s' % key)
            result = True
            if hasattr(self, funcname):
                result = getattr(self, funcname)(payload)
            else:
                self.logger.error(f'发现新数据：{key}')
                result = False
            if result == False:
                self.fetch.post('http://127.0.0.1:5700/tools/respdata', headers={ 'Content-Type': 'application/json;charset=UTF-8' }, data=text.encode('utf-8'))
        except Exception as err:
            self.logger.exception(err)

    def parser_1(self, payload):
        msg = payload.get('messages')[0]
        msgType = msg.get('type')
        bodyType = get(msg, 'body.type')
        key = f'1_{msgType}_{bodyType}'
        self.logger.info('消息类型: %s' % key)
        funcname = f'parser_{key}'
        if not hasattr(self, funcname):
            self.logger.error(f'发现新数据：{key}')
            return False
        getattr(self, funcname)(msg)

    def parser_1_1_1(self, msg):
        """
        发送或收到的信息
        复现1: 给boss发送消息
        复现2: boss发过来的消息
        """
        pass
    def parser_1_1_3(self, msg):
        """
        boss发来一张图片
        """
        pass
    def parser_1_1_4(self, msg):
        """
        作用未知
        """
        pass

    def parser_1_1_7(self, msg):
        """
        系统提示：发送简历弹框
        复现1: boss发来发简历邀约
        """
        pass

    def parser_1_1_20(self, msg):
        """
        发送或收到的表情
        复现1: 给boss发送表情
        复现2: boss发过来的表情
        """
        pass

    def parser_1_3_1(self, msg):
        """
        发送或收到的模版信息
        复现1: boss发来信息，并收到boss设置的默认模版文字信息
        复现2: 点击立即沟通，并发送自己设置的默认模版文字信息
        """
        pass

    def parser_1_3_4(self, msg):
        """
        作用未知
        1_3_8后收到的第二条msg
        """
        pass

    def parser_1_3_7(self, msg):
        """
        系统消息：您是否接受此工作地点?
        """
        pass

    def parser_1_3_8(self, msg):
        """
        初次聊天职位信息
        复现1: boss发来消息，收到的第一条msg，headTitle值为'Boss刘先生希望就如下职位与您沟通'
        复现2: 点击立即沟通后收到的第一条msg，headTitle值为'您正在与Boss颜女士直接沟通如下职位'
        """
        pass

    def parser_1_3_12(self, msg):
        """
        系统消息：简历已经发送给boss
        """
        pass

    def parser_1_3_15(self, msg):
        """
        系统消息：简历还没准备好？有福利！速领！
        """
        pass

    def parser_1_3_16(self, msg):
        """
        系统消息：对猎头满意度评价
        复现1: 给猎头发送完简历后出现
        """
        pass

    def parser_1_4_1(self, msg):
        """
        系统消息：对方已查看您的附件简历
        """
        pass

    def parser_1_4_7(self, msg):
        """
        系统消息：我觉得你很适合我们的岗位，你可以直接跟我互换电话联系我
        """
        pass

    def parser_1_4_12(self, msg):
        """
        系统消息：点击修改去设置中修改打招呼语
        """
        pass

    def parser_1_4_15(self, msg):
        """
        系统消息：问答
        """
        pass

    def parser_1_4_16(self, msg):
        """
        系统消息：竞争者PK情况
        """
        pass

    def parser_4(self, payload):
        pass

    def parser_5(self, payload):
        pass

    def parser_6(self, payload):
        """
        消息已查看通知
        """
        pass
