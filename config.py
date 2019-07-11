# -*- coding:utf-8 -*-

import configparser


cp = configparser.ConfigParser()
cp.read('config.ini', encoding='utf-8')

# access_token, secret
ACCESS_TOKEN = cp.get('QQ_BOT', 'access_token')
SECRET = cp.get('QQ_BOT', 'secret')

# msg：入群，退群自动回复
IN_GROUP_MSG = str(cp.get('GROUP_EVENT_MSG', 'in_group_msg')).replace(r'\n', '\n')
LEAVE_GROUP_MSG = str(cp.get('GROUP_EVENT_MSG', 'leave_group_msg'))
KICK_GROUP_MSG = str(cp.get('GROUP_EVENT_MSG', 'kick_group_msg'))

# group，群组支持的关键字回复列表
GROUP_MSG_REPLY_KW = str(cp.get('GROUP_FUNC', 'group_msg_keyword')).split(',')
GROUP_MSG_REPLY_KW_FUNC = {}
__msg_reply_kw_func = str(cp.get('GROUP_FUNC', 'group_msg_kw_func')).split(',')
for kw_func in __msg_reply_kw_func:
    funcs = kw_func.split(':')
    GROUP_MSG_REPLY_KW_FUNC[funcs[0]] = funcs[1]

# 百度短地址服务
BD_SU_URL = str(cp.get('SHORT_URL', 'bd_url'))
BD_SU_TOKEN = str(cp.get('SHORT_URL', 'bd_token'))
SINA_URL = str(cp.get('SHORT_URL', 'sina_url'))
SINA_KEY = str(cp.get('SHORT_URL', 'sina_appkey'))

# 天气预报接口url
WEATHER_URL = str(cp.get('WEATHER', 'weather_url'))
