**该文档为sunday_mkreadme程序自动生成。**

**该插件代码仅用于个人学习、研究或欣赏。插件代码代码作者不保证内容的正确性。通过使用该插件及相关代码产生的风险与代码作者无关。**

**该插件基于[PySunday](https://github.com/pysunday/pysunday/)开发，官网地址：https://pysunday.github.io/**

# 安装

安装插件：`sunday_install pysunday-plugins/tools-zhipin`

# 插件描述

zhipin工具集合

# 命令用法

## 1. zhipin

```bash
> zhipin -h

usage: zhipin [-v] [-h] [--loglevel LEVEL] {boss,history,user,job,friend,friend30} ...

zhipin查询工具

Optional:
  -v, --version                            当前程序版本
  -h, --help                               打印帮助说明
  --loglevel LEVEL                         日志等级（debug、info、warning、error、critical）, 默认debug

子命令:
  {boss,history,user,job,friend,friend30}

使用案例:
    zhipin boss 20521234
    zhipin user
    zhipin friend 20521234
    zhipin history 112051234
    zhipin history 112051234 -m 321012345678
    
```

## 2. zhipin_chat

```bash
> zhipin_chat -h

usage: zhipin_chat [--config FILE] [--message-in [FILE]] [--message-out [FILE]] [--robot] [--robot-open] [-t TEST_NAME] [-v] [-h]
                   [--loglevel LEVEL]

zhipin聊天工具

Optional:
  --config FILE                        消息映射的json文件
  --message-in [FILE]                  读取消息文件用于回放使用，默认为执行目录下的message.cache.log文件
  --message-out [FILE]                 消息保存文件，用于之后回放使用，默认为执行目录下的message.cache.log文件
  --robot                              是否使用机器人回复消息
  --robot-open                         是否默认开启智能回复
  -t TEST_NAME, --test-name TEST_NAME  测试标签名称, 取examples目录下的文件名
  -v, --version                        当前程序版本
  -h, --help                           打印帮助说明
  --loglevel LEVEL                     日志等级（debug、info、warning、error、critical）, 默认debug

使用案例:
    zhipin_chat --robot --config
    zhipin_chat --robot --config /path/to/name.json --message-out /path/to/message.log
    zhipin_chat --robot --config /path/to/name.json --playback --messsage-in /path/to/message.log
    
```

# 依赖的PySunday插件：

1. [pysunday-plugins/tools-imrobot](https://github.com/pysunday-plugins/tools-imrobot)
2. [pysunday-plugins/login-zhipin](https://github.com/pysunday-plugins/login-zhipin)