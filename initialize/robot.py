import os
from sunday.tools.imrobot import Xiaoi, Moli, Qingyunke
from sunday.core import enver

def robotInit(pwd, logger):
    # 初始化机器人
    xiaoi = Xiaoi()
    xiaoi.open()
    xiaoi.heartbeat()
    qingyunke = Qingyunke()
    moli = None
    logger.info('初始化xiaoi机器人')
    (getenv, setenv, getfile) = enver(os.path.join(pwd, '.env'))
    key = getenv('MOLI_KEY')
    secret = getenv('MOLI_SECRET')
    if key and secret:
        moli = Moli(key=key, secret=secret)
        logger.info('初始化moli机器人')
    logger.info('初始化qingyunke机器人')
    return [xiaoi, moli, qingyunke]

