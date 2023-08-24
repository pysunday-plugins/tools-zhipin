import paho.mqtt.client as mqtt
import certifi
import socks
from pydash import omit

def setHeader(cookies, password):
    def func(header):
        return {
            **omit(header, ['Sec-Websocket-Version', 'Sec-Websocket-Protocol']),
            'Cookie': cookies,
            'Sec-WebSocket-Version': 13,
            'Sec-WebSocket-Protocol': password,
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Origin': 'https://www.zhipin.com',
        }
    return func

def mqttInit(clientId, url, port, path, username, password, cookies, on_connect, on_message, logger=None, isProxy=False):
    """
    初始化mqtt客户端

    **Parameters:**

    * **clientId:** `str` -- 客户端id
    * **url:** `str` -- 服务端地址
    * **port:** `str` -- 服务端端口
    * **path:** `str` -- 服务端路径
    * **username:** `str` -- 用户名
    * **password:** `str` -- 密码
    * **cookies:** `str` -- cookie对象
    * **on_connect:** `function` -- 连接成功的回调
    * **on_message:** `function` -- 收到消息通知的回调
    * **logger:** `Logger` -- 日志工具对象
    * **isProxy:** `bool` -- 是否开启代理
    """
    # 初始化聊天服务
    client = mqtt.Client(client_id=clientId, transport='websockets')
    if logger: client.enable_logger(logger)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username, password)
    client.ws_set_options(path, headers=setHeader(cookies, password))
    client.tls_set(certifi.where())
    client.tls_insecure_set(True)
    if isProxy:
        client.proxy_set(proxy_type=socks.HTTP, proxy_addr='127.0.0.1', proxy_port=8888)
    client.connect(url, port, 60)
    return client

