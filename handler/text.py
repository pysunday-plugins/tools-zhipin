# coding: utf-8
import time
from pydash import pick
from sunday.tools.zhipin.message import text as msg_text

def textHandler(text, source, target, userInfo):
    sourceCopy = pick(source, ['uid', 'encryptUid', 'source'])
    targetCopy = pick(target, ['uid', 'encryptUid', 'source'])
    message = {
        "tempID": userInfo.get('userId') + int(time.time() * 1000),
        "isSelf": True,
        "body": {
            "type": 1,
            "text": text,
            "sticker": None
        },
        "from": sourceCopy,
        "to": targetCopy,
        # "encryptUid": "9efdaee8ae5c9bdd1nZ62NS9EFdS"
        "time": int(time.time() * 1000),
        "mSource": "server",
        "typeSource": "newSubmit",
        "type": 1,
        "isSelf": True
    }
    payload = msg_text(message)
    return (payload, bytearray(payload.SerializeToString()))

if __name__ == "__main__":
    textHandler('haha', kk['from'], kk['to'])

