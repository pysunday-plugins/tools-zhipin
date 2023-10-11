# coding: utf-8
from sunday.core.getException import getException

errorMap = {
        10000: '未收录该消息数据',
        # 其它
        99999: '程序执行异常，请反馈开发人员',
        -1: '目标网站接口异常，请稍后再试',
        -2: '数据库写入失败!',
        }

captchaErrorMax = 4

ZhipinError = getException(errorMap, ['stack', 'origin'])

def getErrorObj(e):
    return {
            **dict(e),
            'success': False,
            }

