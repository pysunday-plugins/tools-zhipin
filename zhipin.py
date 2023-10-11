#coding: utf-8
import os
import sys
import re
import argparse
from pprint import pprint
from urllib.parse import urlencode
from sunday.tools.zhipin import config
from sunday.login.zhipin.login_by_cmd_0918 import Zhipin as ZhipinLogin
from sunday.login.zhipin.config import getUserInfo
from sunday.tools.zhipin.params import ZHIPIN_CMDINFO
from sunday.core import Logger, getParser, Fetch
from pydash import get, find

class Zhipin():
    def __init__(self, isInit=True):
        self.logger = Logger('ZHIPIN HANDLER').getLogger()
        self.geekFriendList = None
        self.bossInfo = {}
        self.getData()
        if isInit: self.init()

    def init(self):
        self.zhipin = ZhipinLogin()
        self.zhipin.login()
        self.rs = self.zhipin.rs

    def getData(self, key=None, val=None):
        if key is None:
            self.cache_data = {}
        elif key in self.cache_data:
            return self.cache_data[key]
        elif val:
            self.cache_data[key] = val() if callable(val) else val
            return self.cache_data[key]
        else:
            return lambda val: self.cache_data.update({ key: val })

    def getUserInfo(self):
        return self.getData('userInfo', lambda: get(self.rs.get_json(getUserInfo), 'zpData'))

    def getToken(self):
        return self.getData('token', lambda: self.getUserInfo()['token'])

    def getPassword(self):
        return self.getData('password', lambda: get(self.rs.get_json(config.wt), 'zpData.wt2'))

    def getCookies(self):
        cookieObj = self.rs.getCookiesDict()
        cookieArr = ['{}={}'.format(key, val) for (key, val) in cookieObj.items()]
        cookieStr = '; '.join(cookieArr)
        # self.logger.debug('cookies: %s' % cookieStr)
        return cookieStr

    def getGeekFriendList(self):
        if not self.geekFriendList:
            res = self.rs.get_json(config.getGeekFriendListUrl)
            self.geekFriendList = get(res, 'zpData.result')
            # self.logger.debug('geekFriendList: %s' % self.geekFriendList)
        return self.geekFriendList

    def getGeekFriend(self, uid):
        friends = self.getGeekFriendList()
        friend = find(friends, lambda f: f.get('uid') == int(uid))
        # self.logger.debug('getGeekFriend: %d => %s' % (int(uid), friend))
        return friend

    def getFriendBy30DaysList(self):
        res = self.rs.get_json(config.friendBy30DaysUrl)
        return get(res, 'zpData.friendList')

    def getFriendBy30Days(self, uid):
        friends = self.getFriendBy30DaysList()
        friend = find(friends, lambda f: f.get('friendId') == int(uid))
        return friend

    def bossdata(self, uid):
        friend = self.getFriendBy30Days(uid)
        if not friend: return
        id = friend.get('encryptFriendId')
        source = friend.get('friendSource')
        res = self.rs.get_json(config.bossdataUrl % (id, source))
        ans = (get(res, 'zpData.data'), get(res, 'zpData.job'))
        # self.logger.debug('bossdata: %d => %s' % (int(uid), ans))
        return ans

    def historyMsg(self, bossId, count=20, page=1, mid=None):
        # 获取聊天记录
        res = self.rs.get(config.historyMsgUrl % (bossId, count, page)).json()
        ans = get(res, 'zpData.messages')
        if mid and type(ans) == list:
            ans = find(ans, lambda m: m.get('mid') == mid)
        # self.logger.debug('historyMsg: %s => %s' % (bossId, ans))
        return ans

    def getHistoryMsg(self, uid, count=20, page=1, mid=None):
        boss = self.getBossInfo(uid)
        if not boss: return {} if mid else []
        ans = self.historyMsg(boss.get('encryptBossId'), count, page, mid=mid)
        return ans

    def getBossInfo(self, uid):
        # 获取boss信息
        if uid in self.bossInfo: return self.bossInfo[uid]
        bossInfo = self.bossdata(uid)[0]
        if bossInfo:
            self.bossInfo[bossInfo.get(uid)] = bossInfo
        return bossInfo

    def getJob(self):
        # self.zhipin.setZpStoken()
        params = {
            'experience': 106,
            'page': 2,
            'city': '101020100',
            'query': 'Python'
        }
        res = self.rs.get_json(config.jobListUrl % urlencode(params))
        hasMore = get(res, 'zpData.hasMore')
        html = get(res, 'zpData.html')


class ZhipinWeb(Zhipin):
    """
    用于Web服务调用
    """
    def __init__(self, session):
        Zhipin.__init__(self, False)
        self.rs = Fetch()
        if session is not None:
            for key, val in session.items():
                self.rs.setCookie(key, val, '.zhipin.com')


class ZhipinSelf(Zhipin):
    """
    用于命令行调用
    """
    def __init__(self):
        Zhipin.__init__(self, False)

    def bossHandler(self):
        # boss子命令
        if len(self.bossId):
            boss = self.getBossInfo(self.bossId[0])
            pprint(boss)

    def userHandler(self):
        # user子命令
        user = self.getUserInfo()
        pprint(user)

    def friendHandler(self):
        # 历史聊天用户信息
        if self.friendId:
            pprint(self.getGeekFriend(self.friendId))
        else:
            pprint(self.getGeekFriendList())

    def friend30Handler(self):
        # 历史聊天用户信息
        if self.friendId:
            pprint(self.getFriendBy30Days(self.friendId))
        else:
            pprint(self.getFriendBy30DaysList())

    def historyHandler(self):
        # history子命令
        if len(self.bossId):
            history = self.getHistoryMsg(self.bossId[0], mid=self.messageId)
            pprint(history)

    def jobHandler(self):
        # job子命令
        jobs = self.getJob()
        pprint(jobs)

    def run(self):
        self.init()
        if self.subName == 'boss':
            self.bossHandler()
        elif self.subName == 'user':
            self.userHandler()
        elif self.subName == 'friend':
            self.friendHandler()
        elif self.subName == 'friend30':
            self.friend30Handler()
        elif self.subName == 'history':
            self.historyHandler()
        elif self.subName == 'job':
            self.jobHandler()


def runcmd():
    (parser, subparsersObj) = getParser(**ZHIPIN_CMDINFO)
    handle = parser.parse_args(namespace=ZhipinSelf())
    handle.run()


if __name__ == "__main__":
    runcmd()
