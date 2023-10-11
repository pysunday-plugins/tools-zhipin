# coding: utf-8
baseUrl = 'https://www.zhipin.com/wapi'

wt = baseUrl + '/zppassport/get/wt'

# 获取聊天记录列表
getGeekFriendListUrl = baseUrl + '/zprelation/friend/getGeekFriendList.json?page=1'

# 获取boss数据
bossdataUrl = baseUrl + '/zpchat/geek/getBossData?bossId=%s&bossSource=%s'

historyMsgUrl = baseUrl + '/zpchat/geek/historyMsg?bossId=%s&c=%d&page=%d'

jobListUrl = baseUrl + '/zpgeek/mobile/search/joblist.json?%s'

# 获取最近30天联系人
friendBy30DaysUrl = baseUrl + '/zprelation/friend/geekFilterByLabel?labelId=0'
