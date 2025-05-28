**该仓库代码仅用于个人学习、研究或欣赏。仓库代码代码作者不保证内容的正确性。通过使用该插件及相关代码产生的风险与仓库代码作者无关。**

**如相关主体（zhipin）不愿意该仓库代码公开，请及时通知仓库作者，予以删除**

# 安装插件

该插件依赖[sunday](https://pysunday.github.io), 需要先安装PySunday

执行PySunday安装该插件：`sunday_install pysunday-plugins/tools-zhipin`

## zhipin命令使用

```bash
 $ zhipin -h
usage: zhipin [-v] [-h] {boss,history,user,friend} ...

zhipin查询工具

Optional:
  -v, --version               当前程序版本
  -h, --help                  打印帮助说明

子命令:
  {boss,history,user,friend}

使用案例:
    zhipin boss 20521234
    zhipin user
    zhipin friend 20521234
    zhipin history 112051234
    zhipin history 112051234 -m 321012345678
```

## zhipin_chat命令使用

**如需开启茉莉机器人请先配置.env.example文件中的MOLI_KEY和MOLI_SECRET字段**

```bash
usage: zhipin_chat [-v] [-h] [--config FILE] [--message-in [FILE]] [--message-out [FILE]] [--robot] [--playback]

zhipin聊天工具

Optional:
  -v, --version         当前程序版本
  -h, --help            打印帮助说明
  --config FILE         消息映射的json文件
  --message-in [FILE]   读取消息文件用于回放使用，在--playback下生效，默认为执行目录下的message.cache.log文件
  --message-out [FILE]  消息保存文件，用于之后回放使用，默认为执行目录下的message.cache.log文件
  --robot               是否使用机器人回复消息
  --playback            是否使用本地消息回放

使用案例:
    zhipin_chat --robot --config
    zhipin_chat --robot --config /path/to/name.json --message-out /path/to/message.log
    zhipin_chat --robot --config /path/to/name.json --playback --messsage-in /path/to/message.log
```

# 实用技巧

## 1. 解决命令行登录与网页登录冲突问题

执行`zhipin_login2brower`后将结果复制到浏览器控制台执行
