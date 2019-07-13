# -*- coding:utf-8 -*-

import hmac
import json
import config
import requests
from cqhttp import CQHttp


bot = CQHttp(api_root='http://127.0.0.1:5700',
             access_token=config.ACCESS_TOKEN, secret=config.SECRET)


def bd_short_url(long_url):
    """
    百度短地址接口调用
    :param long_url: 要转换为短地址的长地址
    :return:
    """
    data = {'url': long_url}
    headers = {'Content-Type': 'application/json', 'Token': config.BD_SU_TOKEN}
    r = requests.post(url=config.BD_SU_URL, headers=headers, data=json.dumps(data))
    return json.loads(r.text)


def sina_short_url(long_url):
    """
    新浪短地址接口调用
    :param long_url: 要转换为短地址的长地址
    :return:
    """
    r = requests.get(f'{config.SINA_URL}?appkey={config.SINA_KEY}&long_url={long_url}')
    return json.loads(r.text)


def weather(city):
    """
    天气查询接口的调用，目前只支持根据城市名称查询
    :param city: 城市名称
    :return:
    """
    if city:
        url = config.WEATHER_URL+'?version=v1&city='+city
        r = requests.get(url=url,)
    return json.loads(r.text)


def at_msg(user_id, msg):
    return f'[CQ:at,qq={user_id}]\n\n{msg}'


def search_earthquake(kw, **kwargs):
    """
    地震查询
    :param kw:
    :param kwargs:
    :return:
    """
    import time
    r = requests.get(url=f'http://news.ceic.ac.cn/ajax/google?rand={time.time()}')
    eqs = json.loads(r.text)[::-1][:10]
    msg = ''
    if eqs and len(eqs) > 0:
        for eq in eqs:
            msg = f"{msg}{eq.get('LOCATION_C')}\n震级：{eq.get('M')}，\n时间：{eq.get('O_TIME')}\n\n"
    msg = f"{msg}开启美好生活·趣无止境"
    return msg


def search_tv(kw, **kwargs):
    """
    电影查询功能
    :param kw: 关键字 电影名字
    :param kwargs:
    :return:
    """
    sec = config.SECRET
    kw_b = str(kw).encode('utf-8')
    sec = sec.encode('utf-8') if isinstance(sec, str) else sec
    sig = hmac.new(sec, kw_b, 'sha1').hexdigest()
    r = requests.post(url=config.TV_SEARCH_URL,
                      data=kw_b, headers={'X-Signature': sig})
    resp = json.loads(r.text)
    msg = f'很抱歉，没有找到 "{kw}" 相关的影视资源。\n获取更多，你也可以移步优视频网：\nhttp://www.yoviptv.com\n\n开启美好生活·趣无止境'
    if int(resp.get('ret_nums')) != 0:
        sr = sina_short_url(resp.get('url'))
        if sr.get('rs_code') == 0:
            msg = f'影视详情：\n关键词：{kw}\n观看地址：{sr.get("short_url")}\n\n开启美好生活·趣无止境'
    return msg


def search_weather(kw, **kwargs):
    """
    天气查询
    :param kw: 城市
    :param kwargs: 其他信息
    :return:
    """
    msg = None
    area = kwargs.get('area')
    city = area if (not kw and area) else kw
    city = str(city).replace('市区', '').replace('市', '')
    out = ['省', '区', '乡', '村', '国', '镇']
    if len([o for o in out if o in city]) > 0 or len(city) > 5:
        msg = '温馨提示：天气查询时只输入具体城市名称即可查询，如：北京/郑州/正定/磁县/雄县'
    else:
        weather_json = weather(city)
        if weather_json:
            msg = ''
            city = weather_json.get('city')
            msg = f'{msg}所在城市：{city}\n\n'
            day3 = weather_json.get('data')[0:3]
            for i, day in enumerate(day3):
                msg = f"{msg}{day.get('day')}\t{day.get('week')}\n天气：{day.get('wea')}\n"
                msg = f"{msg}气温：{day.get('tem2')} ~ {day.get('tem1')}\n"
                if i == 0:
                    msg = f"{msg}空气质量：{day.get('air_level')}\n{day.get('air_tips')}\n"
                zwx = day.get('index')[0]
                msg = f"{msg}{zwx.get('title')}：{zwx.get('level')}\n{zwx.get('desc')}\n\n"
            msg = f"{msg}\n开启美好生活·趣无止境"
    return msg


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
    app.run(host='127.0.0.1', port=5599, debug=False)


