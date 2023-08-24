from sunday.tools.zhipin.zhipin import Zhipin
from sunday.login.zhipin.config import jobListUrl

zhipin = Zhipin()
zhipin.zhipin.setZpStoken()
params = {
    'experience': 106,
    'page': 2,
    'city': '101020100',
    'query': 'Python'
}
zhipin.zhipin
