# -*- coding:utf-8 -*-
import hmac
import json
import requests
from config import config


class CBot:

    @staticmethod
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

    @staticmethod
    def sina_short_url(long_url):
        """
        新浪短地址接口调用
        :param long_url: 要转换为短地址的长地址
        :return:
        """
        r = requests.get(f'{config.SINA_URL}?appkey={config.SINA_KEY}&long_url={long_url}')
        return json.loads(r.text)

    @staticmethod
    def weather(city):
        """
        天气查询接口的调用，目前只支持根据城市名称查询
        :param city: 城市名称
        :return:
        """
        if city:
            url = config.WEATHER_URL + '?version=v1&city=' + city
            r = requests.get(url=url, )
        return json.loads(r.text)

    @staticmethod
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

    @staticmethod
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
            sr = CBot.sina_short_url(resp.get('url'))
            if sr.get('rs_code') == 0:
                msg = f'影视详情：\n关键词：{kw}\n观看地址：{sr.get("short_url")}\n\n开启美好生活·趣无止境'
        return msg

    @staticmethod
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
            weather_json = CBot.weather(city)
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

