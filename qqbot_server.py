# -*- coding:utf-8 -*-

from config import config
from cqhttp import CQHttp


bot = CQHttp(api_root='http://127.0.0.1:5700',
             access_token=config.ACCESS_TOKEN, secret=config.SECRET)


def at_msg(user_id, msg):
    return f'[CQ:at,qq={user_id}]\n\n{msg}'


@bot.on_message()
def handle_msg(context):
    """
    群回复功能
    具体功能在config.ini中的GROUP_FUNC section下配置
    group_msg_keyword为可处理的关键字
    group_msg_kw_func要处理的关键字所对应的处理函数
    :param context:
    :return:
    """
    user_id, message = context['user_id'], str(context['message'])
    if message:
        reply = ''
        for kw in config.GROUP_MSG_REPLY_KW:
            if message.startswith(kw):
                to_func = config.GROUP_MSG_REPLY_KW_FUNC.get(kw)
                real_kw = message.replace(kw, '').strip()
                real_kw = real_kw.replace(' ', '')
                area = context['sender']['area']
                if not real_kw:
                    if 'search_weather' == to_func:
                        if area:
                            reply = eval(to_func)(real_kw, area=area)
                    else:
                        reply = eval(to_func)(real_kw)
                else:
                    reply = eval(to_func)(real_kw)
                if reply:
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


app = bot.server_app


if __name__ == '__main__':
    pass
    # app.run(host='127.0.0.1', port=5599, debug=False)

