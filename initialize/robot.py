import os
from sunday.tools.imrobot import Xiaoi, Moli, Qingyunke
from sunday.core import enver, Logger
from sunday.tools.gpt.ask import GptAsk
logger = Logger('机器人初始化').getLogger()

robotNameMap = {
    'xiaoi': '小i',
    'chatgpt': 'ChatGPT',
    'moli': '茉莉',
    'qingyunke': '青云客'
}

def xiaoiInit():
    try:
        xiaoi = Xiaoi()
        xiaoi.open()
        xiaoi.heartbeat()
        logger.info('初始化小i机器人')
        return xiaoi
    except Exception as e:
        logger.error('小i机器人初始化失败')
        logger.exception(e)
        return None

def qingyunkeInit():
    try:
        qingyunke = Qingyunke()
        logger.info('初始化青云客机器人')
        return qingyunke
    except Exception as e:
        logger.error('青云客机器人初始化失败')
        logger.exception(e)
        return None

def moliInit(pwd):
    try:
        (getenv, setenv, getfile) = enver(os.path.join(pwd, '.env'))
        key = getenv('MOLI_KEY')
        secret = getenv('MOLI_SECRET')
        if not key or not secret: return None
        moli = Moli(key=key, secret=secret)
        logger.info('初始化茉莉机器人')
        return moli
    except Exception as e:
        logger.error('茉莉机器人初始化失败')
        logger.exception(e)
        return None

def robotInit(pwd):
    # 初始化机器人
    robotMap = {
        'xiaoi': xiaoiInit(),
        'qingyunke': qingyunkeInit(),
        'moli': moliInit(pwd)
    }
    def ask(robotType, text, *args, **kwargs):
        if robotType not in robotNameMap:
            raise Exception(f'机器人{robotType}不存在')
        res_text = ''
        try:
            if robotType == 'chatgpt':
                res_text = GptAsk(text).getData().get('response')
                if res_text: res_text += '\n--来自ChatGPT'
            elif robotType == 'moli' and robotMap['moli']:
                res_text = robotMap['moli'].askText(text, *args, **kwargs)
            elif robotType in robotMap and robotMap[robotType]:
                res_text = robotMap[robotType].askText(text)
        except Exception as e:
            logger.exception(e)
        return res_text or f'{robotNameMap[robotType]}机器人异常，请稍后重试或选择其它机器人'
    return ask
