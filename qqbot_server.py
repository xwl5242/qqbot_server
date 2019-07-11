# -*- coding:utf-8 -*-

import hmac
import json
import config
import requests
from cqhttp import CQHttp


bot = CQHttp(api_root='http://127.0.0.1:5700',
             access_token=config.ACCESS_TOKEN, secret=config.SECRET)


def bd_short_url(long_url):
    data = {'url': long_url}
    headers = {'Content-Type': 'application/json', 'Token': config.BD_SU_TOKEN}
    r = requests.post(url=config.BD_SU_URL, headers=headers, data=json.dumps(data))
    return json.loads(r.text)


def sina_short_url(long_url):
    r = requests.get(f'{config.SINA_URL}?appkey={config.SINA_KEY}&long_url={long_url}')
    return json.loads(r.text)


def at_msg(user_id, msg):
    return f'[CQ:at,qq={user_id}]\n\n{msg}'


def search_tv(kw):
    sec = config.SECRET
    kw_b = str(kw).encode('utf-8')
    sec = sec.encode('utf-8') if isinstance(sec, str) else sec
    sig = hmac.new(sec, kw_b, 'sha1').hexdigest()
    r = requests.post(f'http://127.0.0.1:9999/api/search_tv',
                      data=kw_b, headers={'X-Signature': sig})
    resp = json.loads(r.text)
    msg = f'很抱歉，没有找到 "{kw}" 相关的影视资源。\n获取更多，你也可以移步优视频网：\nhttp://www.yoviptv.com\n\n开启美好生活·趣无止境'
    if int(resp.get('ret_nums')) != 0:
        sr = sina_short_url(resp.get('url'))
        if sr.get('rs_code') == 0:
            msg = f'影视详情：\n关键词：{kw}\n观看地址：{sr.get("short_url")}\n\n开启美好生活·趣无止境'
    return msg


def search_weather(kw):
    return '天气搜索测试回复'


@bot.on_message()
def handle_msg(context):
    user_id, message = context['user_id'], str(context['message'])
    if message:
        for kw in config.GROUP_MSG_REPLY_KW:
            if message.startswith(kw):
                print(message)
                reply = eval(config.GROUP_MSG_REPLY_KW_FUNC.get(kw))(message.replace(kw, '').strip())
                return {'reply': '\n\n'+reply, 'at_sender': True}


@bot.on_notice('group_increase', 'group_decrease')
def handle_group_increase_decrease(context):
    """
    群成员增加和减少
    :param context:
    :return:
    """
    group_id, user_id, notice_type = context['group_id'], context['user_id'], context['notice_type']
    if notice_type:
        if notice_type == 'group_increase':
            # 群组增加成员
            # 进群自动回复，发送群消息，并@新成员
            bot.send_group_msg(group_id=group_id, message=at_msg(user_id, config.IN_GROUP_MSG))
        elif notice_type == 'group_decrease':
            # 群组减少成员
            sub_type = context['sub_type']
            if sub_type:
                if sub_type == 'leave':
                    # 自己主动离开
                    msg = config.LEAVE_GROUP_MSG.replace('@user_id', str(user_id))
                else:
                    # 被踢出去
                    msg = config.KICK_GROUP_MSG.replace('@user_id', str(user_id))
                bot.send_group_msg(group_id=group_id, message=msg)
        else:
            pass


bot.run(host='127.0.0.1', port=5599, debug=False)

if __name__ == '__main__':
    print(bd_short_url('http://www.yoviptv.com/t-t/k=1'))


