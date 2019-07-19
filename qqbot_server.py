# -*- coding:utf-8 -*-

from config import config
from cqhttp import CQHttp
from mbot.custom_bot import api
from mbot.bd_unit_bot import BDUnitBot


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
    user_id, message, m_type = context['user_id'], str(context['message']), str(context['message_type'])
    message = message.replace(' ', '')
    if message:
        if m_type == 'group' or m_type == 'discuss':
            # 群组或讨论组，只有@机器人，才开始闲聊
            if message.startswith(f"[CQ:at,qq={config.CUR_QQ}]"):
                # 消息以@开头,闲聊
                message = message.replace(f"[CQ:at,qq={config.CUR_QQ}]", '')
                uid, reply = BDUnitBot.chat(user_id, message)
                return {'reply': reply, 'at_sender': True}
            else:
                # 关键字回复
                for kw in config.GROUP_MSG_REPLY_KW:
                    if message.startswith(kw):
                        to_func = config.GROUP_MSG_REPLY_KW_FUNC.get(kw)
                        real_kw = message.replace(kw, '').strip()
                        real_kw = real_kw.replace(' ', '')
                        area = context['sender']['area']
                        reply = api(to_func, kw=real_kw, area=area)
                        if reply:
                            return {'reply': '\n\n'+reply, 'at_sender': True}
        elif m_type == 'private':
            # 直接开启闲聊
            if message.startswith('电影'):
                to_func = config.GROUP_MSG_REPLY_KW_FUNC.get('电影')
                reply = api(to_func, kw=message.replace('电影', '').replace(' ', ''))
            else:
                uid, reply = BDUnitBot.chat(user_id, message)
            return {'reply': reply}


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
    app.run(host='127.0.0.1', port=5599, debug=False)

