#coding=utf-8

import base64
import zlib
import re,json,os
from datetime import datetime
import requests as curl, time
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
from db.Db import Db
from multiprocessing import Pool

# In[]:
class JiuBa:
    def __init__(self, db_config):
        """
        :param db_config:数据库连接配置
        """
        self.db = Db(**db_config)


    def encode(self, string):
        """
        编码
        :param token:
        :return:
        """
        token_string = zlib.compress(string.encode())
        token_decode = base64.b64encode(token_string)
        return token_decode.decode()


    def decode(self, token):
        """
        解码
        :param token:
        :return:
        """
        token_decode = base64.b64decode(token.encode())  # token为token字符串
        # 解压
        token_string = zlib.decompress(token_decode)
        return token_string


    def build_token(self):
        # 移动端网页中的源token
        # r'{"rId":100004,"ver":"1.0.6","ts":1557986259492,"cts":1557986260704,"brVD":[1125,2436],"brR":[[375,812],[375,812],24,24],"bI":["https://i.meituan.com/awp/h5/hotel/poi/deal.html?poiId=189285561",""],"mT":[],"kT":[],"aT":[],"tT":[],"aM":"","sign":"eJwlzrsSgyAQheF3saBkdnEXloJCQN7DUZyxiDpeirx9YnL6f77T1HUKyCxgDMEztdz3MgVO5FrjKWeHgs5QAaIiWXxOvsTY9TFLAoTWio2M2BeXKXdAKZKwU/u2BBRvhNmiOrbtlbZ7vYI6r+G4HtP51sLfvN57DaDusx5fW/0ejIPn2SOO1TmaWxGZjX4yIcNEGjVoaD7BLDJV"}'

        # 测试发现其他参数可以不要。只需要传入时间戳 用来检验实效性
        timestamp = int(round(time.time() * 1000))
        token = r'{"rId":0,"ver":"1.0.6","ts":0,"cts":%d,"brVD":[],"brR":[],"bI":[],"mT":[],"kT":[],"aT":[],"tT":[],"aM":"","sign":""}' % (
            timestamp)
        return self.encode(token)


    def request(self, uri, params={}):

        # https://ihotel.meituan.com/group/v1/yf/list/182625269? =1&=&end=1558022400000&&poi=189285561&uuid=ca95f911ce774f3888f2.1557842544.1.0.0&iuuid=5C473294DD7181724F044F8D89DC9FBBAEBD8C0103686B511EF7D4DA04CB4857&_token=
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'Cookie': '__utmb=1',  # __utmb 移动端访问的标记
            'Connection': 'close',
        }
        s = curl.session()
        s.keep_alive = False  # 关闭多余连接

        re = s.get(uri, params=params, headers=headers, timeout=5) #必须设置超时时间使用代理不能一直等待
        return re

    def request_json(self, uri, params={}):
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'Cookie': '__utmb=1',  # __utmb 移动端访问的标记
            'Content-Type': 'application/json;charset=utf-8',
            'Connection': 'close',
        }
        s = curl.session()
        s.keep_alive = False  # 关闭多余连接

        re = s.get(uri, params=params, headers=headers, timeout=5).json()
        return re

    def read_bars_packages(self, outer):
        packages = []
        bar_temp_info = {}
        try:
            two = outer.contents[3]
            dd_list = two.find_all("dl", attrs={"class": "list bd-deal-list"})
            dd_list2 = dd_list[0].find_all("dd")
            for i in dd_list2:
                package = {}
                package['package_id'] = ""
                package['bar_id'] = ""
                package['package_name'] = ""
                package['package_price'] = 0.0
                package['package_unit'] = ""
                package['activity'] = ""
                package['market_price'] = 0.0
                package['sales_volume'] = 0
                package['sales_time_period'] = 0
                package['effective_start_date'] = ""
                package['effective_end_date'] = ""
                package['package_title'] = ""
                package['package_rule'] = ""

                goods1 = i.find("a", attrs={"class": "react"})
                goods1_href = goods1.attrs['href']
                print(goods1_href)
                goods1_href_temp1 = goods1_href[goods1_href.rfind("/") + 1:]
                goods1_href_temp2 = goods1_href_temp1[:goods1_href_temp1.find(".")]

                package["package_id"] = goods1_href_temp2
                package["package_name"] = goods1.find("div", attrs={"class": "title text-block"}).string
                package["package_price"] = goods1.find("span", attrs={"class": "strong"}).string
                package["package_unit"] = goods1.find("span", attrs={"class": "strong-color"}).string
                print("套餐ID is ", package["package_id"], "套餐名称 is ", package["package_name"])  # 624190488

                activity = goods1.find("span", attrs={"class": "tag"})
                if activity is not None:
                    activity = activity.string
                else:
                    activity = ""
                package["activity"] = activity

                market_price = goods1.find("del")
                if market_price is not None:
                    market_price = float(market_price.string[:-1])
                else:
                    market_price = 0.0
                package["market_price"] = market_price

                sales_volume = i.find("a", attrs={"class": "statusInfo"}).string
                package["sales_volume"] = sales_volume[sales_volume.find("售") + 1:]

                print("*" * 30)

                items_data = []
                try:
                    # Ajax请求：
                    # https://www.meituan.com/dz/deal/624190488
                    goods_href = "https://i.meituan.com/general/platform/dztg/getdealskustructdetail.json?dealGroupId=" + goods1_href_temp2
                    print(goods_href)
                    goods1_content = j.request_json(goods_href)
                    print(goods1_content)

                    if goods1_content['optionalGroups'] or goods1_content['mustGroups']:
                        print(goods1_content['title'], goods1_content['marketPrice'], goods1_content['price'])
                        if package["market_price"]:
                            package["market_price"] = float(goods1_content['marketPrice'])
                        if goods1_content['desc']:
                            package["package_rule"] = BeautifulSoup(goods1_content['desc'], "html.parser").text

                    if goods1_content['optionalGroups']:
                        for goods1_group in goods1_content['optionalGroups']:
                            print(goods1_group['desc'])
                            for item in goods1_group['dealStructInfo']:
                                item_data_1 = {}
                                print(item['title'], item['price'], item['copies'])
                                item_data_1["item_name"] =  item['title']
                                item_data_1["item_price"] = item['price'][:-1]
                                item_data_1["item_unit"] = item['price'][-1]
                                item_data_1["copies_nm"] = item['copies'][:-1]
                                items_data.append(item_data_1)
                            print("-" * 30)
                    if goods1_content['mustGroups']:
                        for goods1_group in goods1_content['mustGroups']:
                            for items in goods1_group['dealStructInfo']:
                                item_data_2 = {}
                                item_data_2["item_name"] = items['title']
                                item_data_2["item_price"] = items['price'][:-1]
                                item_data_2["item_unit"] = items['price'][-1]
                                item_data_2["copies_nm"] = items['copies'][:-1]
                                # for item in items["items"]:
                                #     print(item['value'], item['name'])
                                items_data.append(item_data_2)
                            print("-" * 30)

                    main1_href = "https://i.meituan.com/general/platform/mttgdetail/mtdealbasegn.json?dealid=" + goods1_href_temp2 + "&shopid=&eventpromochannel=&stid=&lat=&lng="
                    print(main1_href)
                    main1_content = j.request_json(main1_href)
                    print(main1_content)
                    print(main1_content['title'], main1_content['solds'], main1_content['soldStr'],
                          main1_content['start'],
                          main1_content['end'], main1_content['dealBuyConfig']['buttonText'])
                    package["package_title"] = main1_content['title']
                    package["sales_time_period"] = main1_content['soldStr']
                    package["effective_start_date"] = main1_content['start']
                    package["effective_end_date"] = main1_content['end']

                    print(main1_content['shop']['name'], main1_content['shop']['phone'], main1_content['shop']['addr'],
                          main1_content['shop']['lat'], main1_content['shop']['lng'])
                    if not bar_temp_info:
                        print("0" * 30)
                        bar_temp_info["bar_phone"] = main1_content['shop']['phone']
                        bar_temp_info["bar_address"] = main1_content['shop']['addr']
                        bar_temp_info["lng"] = main1_content['shop']['lng']
                        bar_temp_info["lat"] = main1_content['shop']['lat']

                except:
                    print("Desc is Error")
                    print()
                print("*" * 30)
                print()
                package["items_data"] = items_data
                packages.append(package)
        except:
            print("None of Goods")

        return packages, bar_temp_info


    def read_city_bars(self, city, business_id):
        url = r'https://i.meituan.com/s/%s-酒吧?bid=%d' % (name, business_id)
        content = self.request(url).text
        bars_soup = BeautifulSoup(content, "html.parser")
        # print(soup.prettify())

        bar_infos = []
        outer_list = bars_soup.find_all("dl", attrs={"class": "list", "gaevent": "search/list"})
        for outer in outer_list:
            bar_info = {}
            one_contents = outer.contents[1]
            a_react = one_contents.find("a", attrs={"class": "react"})
            jiuba_href = a_react.attrs['href']
            print(jiuba_href)
            jiuba_id = jiuba_href[jiuba_href.rfind("/") + 1:]
            print("酒吧ID is ", jiuba_id)
            poiname = a_react.find("span", attrs={"class": "poiname"}).string
            print(poiname)
            bar_info["bar_id"] = jiuba_id
            bar_info["bar_name"] = poiname

            dealtype_icon_all = a_react.find_all("span", attrs={"class": "dealtype-icon"})
            print("dealtype-icon is ", dealtype_icon_all)

            juan = a_react.find("span", attrs={"class": "dealtype-icon dealcard-magiccard"})
            if juan is not None:
                juan = juan.string
                print(juan)
            else:
                juan = ""

            wai = a_react.find("span", attrs={"class": "dealtype-icon dealcard-waimai"})
            if wai is not None:
                wai = wai.string
                print(wai)
            else:
                wai = ""

            list_str = ""
            for a in dealtype_icon_all:
                print(a.string)
                list_str = list_str + a.string
            # print(list_str)
            if juan != "":
                list_str = list_str.replace(juan, "") # re.sub(juan, '', list_str)
            if wai != "":
                list_str = list_str.replace(wai, "")

            bar_info["tuan"] = list_str
            bar_info["juan"] = juan
            bar_info["wai"] = wai

            score = a_react.find("em", attrs={"class": "star-text"})
            if score is not None:
                score = score.string
                score = float(score)
                print("评分", score)
            else:
                score = 0.0
            bar_info["bar_score"] = score

            # juli1 = one_contents.find("span", attrs={"data-com": "locdist"})  # 应该是Ajax请求的
            business = one_contents.find('a', onclick='return false;').string  # one.find('a', onclick=True)
            print(business)
            bar_info["business"] = business
            print(bar_info)
            print()
            packages, bar_temp_info = self.read_bars_packages(outer)
            print(packages)
            print(bar_temp_info)
            print()
            if ('bar_phone' in bar_temp_info.keys()):
                bar_info["bar_phone"] = bar_temp_info["bar_phone"]
            else:
                bar_info["bar_phone"] = ""

            if ('bar_address' in bar_temp_info.keys()):
                bar_info["bar_address"] = bar_temp_info["bar_address"]
            else:
                bar_info["bar_address"] = ""

            if ('lng' in bar_temp_info.keys()):
                bar_info["lng"] = bar_temp_info["lng"]
            else:
                bar_info["lng"] = 0.0

            if ('lat' in bar_temp_info.keys()):
                bar_info["lat"] = bar_temp_info["lat"]
            else:
                bar_info["lat"] = 0.0

            bar_info["packages"] = packages
            bar_infos.append(bar_info)

        return bar_infos


    def build_data(self, city, business_id):
        m = self
        print(city)
        data = m.read_city_bars(city, business_id)  # 读取城市下的所有酒店列表
        print("%" * 30)
        print(data)
        print()
        return data

    def insert_data(self,city,business_id):
        bar_num = 0
        now = int(time.time())
        # data = self.build_data(city, business_id)

        data = [{'bar_id': '1641244426', 'bar_name': 'WOW酒馆（北京路店）', 'tuan': '团', 'juan': '券', 'wai': '', 'bar_score': 4.9, 'business': '同德昆明广场', 'bar_phone': '18502800168/16606646694', 'bar_address': '北京路金色年华广场2楼', 'lng': 102.7233593631883, 'lat': 25.069190350290118, 'packages': [{'package_id': '636936705', 'package_name': '代金券', 'package_price': '89', 'package_unit': '元', 'activity': '', 'market_price': '100元', 'sales_volume': '3', 'package_title': '仅售89元，价值100元代金券！', 'sales_time_period': '半年消费3', 'effective_start_date': 'Apr 13, 2020 11:02:40 AM', 'effective_end_date': 'May 9, 2021 11:59:59 PM', 'items_data': []}, {'package_id': '624190488', 'package_name': '百威/乐堡二选一小食小聚超值体验套餐', 'package_price': '39.9', 'package_unit': '元', 'activity': '休闲娱乐团购新用户减42元', 'market_price': '108元', 'sales_volume': '1381', 'package_rule': '1.每人每天限用1张，单桌使用总数不能超过4张。', 'package_title': '仅售39.9元，价值108元百威/乐堡二选一小食小聚超值体验套餐！', 'sales_time_period': '半年消费1826', 'effective_start_date': 'Dec 9, 2019 4:00:18 PM', 'effective_end_date': 'Jan 9, 2021 11:59:59 PM', 'items_data': [{'item_name': '百威啤酒', 'item_price': '15', 'item_unit': '元', 'copies_nm': '6'}, {'item_name': '乐堡啤酒', 'item_price': '15', 'item_unit': '元', 'copies_nm': '6'}, {'item_name': '风味豆干', 'item_price': '18', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '冰毛豆', 'item_price': '18', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '花生米', 'item_price': '15', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '凉拌黄瓜', 'item_price': '15', 'item_unit': '元', 'copies_nm': '1'}]}, {'package_id': '624194967', 'package_name': '女士专享鸡尾酒1杯/饮品限时抢购', 'package_price': '1', 'package_unit': '元', 'activity': '', 'market_price': '28元', 'sales_volume': '403', 'package_rule': '1.每人每天最多可用2张', 'package_title': '仅售1元，价值28元女士专享鸡尾酒1杯/饮品限时抢购！', 'sales_time_period': '半年消费357', 'effective_start_date': 'Dec 9, 2019 4:15:36 PM', 'effective_end_date': 'Jan 5, 2021 11:59:59 PM', 'items_data': [{'item_name': '墨西哥日出', 'item_price': '28', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '白俄罗斯', 'item_price': '28', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '天使堕落', 'item_price': '28', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '玛格丽特', 'item_price': '28', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '莫吉托', 'item_price': '28', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '奶奶遇上冰沙', 'item_price': '25', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '金桔柠檬', 'item_price': '25', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '初恋味道', 'item_price': '25', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '柠檬蜂蜜茶', 'item_price': '15', 'item_unit': '元', 'copies_nm': '1'}]}, {'package_id': '624200971', 'package_name': '花酒斗酒系列乐享体验套餐', 'package_price': '58', 'package_unit': '元', 'activity': '休闲娱乐团购新用户减29.4元', 'market_price': '123元', 'sales_volume': '239', 'package_rule': '本系列果酒为WOW特制而成，每种酒由12杯为一套，清爽可口，颜值炫目，且可自由组合搭配', 'package_title': '仅售58元，价值123元花酒斗酒系列乐享体验套餐！', 'sales_time_period': '半年消费241', 'effective_start_date': 'Dec 9, 2019 4:37:08 PM', 'effective_end_date': 'Jan 9, 2021 11:59:59 PM', 'items_data': [{'item_name': '桃花醉', 'item_price': '98', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '红颜笑', 'item_price': '98', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '蓝颜痴', 'item_price': '98', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '青梅弄', 'item_price': '98', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '黄非红', 'item_price': '98', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '水果沙拉', 'item_price': '25', 'item_unit': '元', 'copies_nm': '1'}]}, {'package_id': '624403704', 'package_name': '多人进口啤酒新店特惠套餐', 'package_price': '108', 'package_unit': '元', 'activity': '', 'market_price': '210元', 'sales_volume': '322', 'package_title': '仅售108元，价值210元多人进口啤酒新店特惠套餐！', 'sales_time_period': '半年消费331', 'effective_start_date': 'Dec 10, 2019 11:54:29 AM', 'effective_end_date': 'Jan 9, 2021 11:59:59 PM', 'items_data': [{'item_name': '乐堡啤酒', 'item_price': '15', 'item_unit': '元', 'copies_nm': '12'}, {'item_name': '百威啤酒', 'item_price': '15', 'item_unit': '元', 'copies_nm': '12'}, {'item_name': '科罗娜啤酒', 'item_price': '15', 'item_unit': '元', 'copies_nm': '12'}, {'item_name': '鸡米花', 'item_price': '30', 'item_unit': '元', 'copies_nm': '1'}]}, {'package_id': '624587912', 'package_name': '网红野格红牛洋酒单瓶小食超值套餐', 'package_price': '198', 'package_unit': '元', 'activity': '', 'market_price': '293元', 'sales_volume': '143', 'package_title': '仅售198元，价值293元网红野格红牛洋酒单瓶小食超值套餐！', 'sales_time_period': '半年消费150', 'effective_start_date': 'Dec 11, 2019 9:45:16 AM', 'effective_end_date': 'May 9, 2021 11:59:59 PM', 'items_data': [{'item_name': '占边威士忌', 'item_price': '183', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '野格', 'item_price': '253', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '绝对伏特加', 'item_price': '253', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '红牛', 'item_price': '40', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '红茶', 'item_price': '40', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '绿茶', 'item_price': '40', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '雪碧', 'item_price': '40', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '可乐', 'item_price': '32', 'item_unit': '元', 'copies_nm': '1'}]}]}, {'bar_id': '168919511', 'bar_name': '黑森林酒吧（同德店）', 'tuan': '团', 'juan': '', 'wai': '外', 'bar_score': 4.7, 'business': '同德昆明广场', 'bar_phone': '0871-65360216', 'bar_address': '人民中路正义坊北馆4楼', 'lng': 102.70803650012134, 'lat': 25.04362587157603, 'packages': [{'package_id': '36920794', 'package_name': '5L黑森林自酿啤酒套餐', 'package_price': '249', 'package_unit': '元', 'activity': '', 'market_price': '417元', 'sales_volume': '7505', 'package_title': '仅售249元，价值417元5L黑森林自酿啤酒套餐，不限时段通用，免费WiFi！', 'sales_time_period': '半年消费770', 'effective_start_date': 'Mar 26, 2016 10:40:50 AM', 'effective_end_date': 'Dec 26, 2020 11:59:59 PM', 'items_data': []}, {'package_id': '36152494', 'package_name': '4~6人芬兰伏特加套餐', 'package_price': '198', 'package_unit': '元', 'activity': '', 'market_price': '351元', 'sales_volume': '1343', 'package_title': '仅售198元，价值351元4~6人芬兰伏特加套餐，不限时段通用，免费WiFi！', 'sales_time_period': '半年消费239', 'effective_start_date': 'Mar 6, 2016 12:00:01 AM', 'effective_end_date': 'Dec 26, 2020 11:59:59 PM', 'items_data': []}, {'package_id': '55980114', 'package_name': '2-4人野格利口酒套餐', 'package_price': '329', 'package_unit': '元', 'activity': '', 'market_price': '384元', 'sales_volume': '244', 'package_title': '仅售329元，价值384元2-4人野格利口酒套餐，不限时段通用，免费WiFi！', 'sales_time_period': '半年消费101', 'effective_start_date': 'Mar 19, 2019 9:52:05 AM', 'effective_end_date': 'Dec 26, 2020 11:59:59 PM', 'items_data': []}]}, {'bar_id': '184182228', 'bar_name': '长亭酒馆（同德昆明广场店）', 'tuan': '团', 'juan': '', 'wai': '', 'bar_score': 4.0, 'business': '同德昆明广场', 'bar_phone': '18206870097', 'bar_address': '北京路928号同德昆明广场负一楼', 'lng': 102.71926106548113, 'lat': 25.072037989141876, 'packages': [{'package_id': '625385813', 'package_name': '百威啤酒套餐', 'package_price': '228', 'package_unit': '元', 'activity': '', 'market_price': '285元', 'sales_volume': '5', 'package_rule': '购买须知由于订桌紧张，需每日18点以前预约，21点前需要到店周五周六法定节假日不能使用。如有任何疑问请拨打18206870097咨询', 'package_title': '仅售228元，价值285元百威啤酒套餐，不限时段通用，免费WiFi！', 'sales_time_period': '半年消费5', 'effective_start_date': 'Dec 17, 2019 5:33:49 PM', 'effective_end_date': 'Dec 17, 2020 11:59:00 PM', 'items_data': [{'item_name': '油呛鱿鱼', 'item_price': '35', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '油呛毛肚', 'item_price': '35', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '油呛螺肉', 'item_price': '35', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '百威啤酒1打', 'item_price': '220', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '冰毛豆', 'item_price': '25', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '纸巾', 'item_price': '5', 'item_unit': '元', 'copies_nm': '1'}]}, {'package_id': '625444403', 'package_name': '洋酒套餐', 'package_price': '418', 'package_unit': '元', 'activity': '', 'market_price': '520元', 'sales_volume': '1', 'package_rule': '购买须知由于订桌紧张，需每日18点以前预约，21点前需要到店周五周六法定节假日不能使用。如有任何疑问请拨打18206870097咨询', 'package_title': '仅售418元，价值520元洋酒套餐，不限时段通用，免费WiFi！', 'sales_time_period': '半年消费1', 'effective_start_date': 'Dec 17, 2019 5:24:24 PM', 'effective_end_date': 'Jan 13, 2021 11:59:59 PM', 'items_data': [{'item_name': '油呛鱿鱼', 'item_price': '35', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '油呛毛肚', 'item_price': '35', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '油呛螺肉', 'item_price': '35', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '野格力嬌', 'item_price': '360', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '红牛4听', 'item_price': '60', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '码头卤牛肉', 'item_price': '35', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '铁壳花生', 'item_price': '25', 'item_unit': '元', 'copies_nm': '1'}, {'item_name': '纸巾', 'item_price': '5', 'item_unit': '元', 'copies_nm': '1'}]}]}, {'bar_id': '195577724', 'bar_name': '花家+（昆明广场店）', 'tuan': '团', 'juan': '', 'wai': '外', 'bar_score': 4.4, 'business': '同德昆明广场', 'bar_phone': '0871-63815267', 'bar_address': '白云路同德广场悦汇坊1楼', 'lng': 102.72152345610544, 'lat': 25.06980430402594, 'packages': [{'package_id': '617838942', 'package_name': '代金券', 'package_price': '87', 'package_unit': '元', 'activity': '', 'market_price': '100元', 'sales_volume': '4', 'package_title': '仅售87元，价值100元代金券，全场通用！', 'sales_time_period': '半年消费5', 'effective_start_date': 'Oct 30, 2019 12:53:17 PM', 'effective_end_date': 'Oct 28, 2020 11:59:59 PM', 'items_data': []}, {'package_id': '617852396', 'package_name': '精酿黑啤多人套餐+小吃', 'package_price': '249', 'package_unit': '元', 'activity': '', 'market_price': '409元', 'sales_volume': '184', 'package_rule': '精酿黑啤3升 338冰毛豆1份26薯片1份20豆腐干1份20纸巾1盒5', 'package_title': '仅售249元，价值409元精酿黑啤多人套餐+小吃，免费WiFi！', 'sales_time_period': '半年消费188', 'effective_start_date': 'Oct 30, 2019 2:06:11 PM', 'effective_end_date': 'Oct 28, 2020 11:59:59 PM', 'items_data': [{'item_name': '精酿黑啤多人套餐', 'item_price': '409', 'item_unit': '元', 'copies_nm': '1'}]}, {'package_id': '630704985', 'package_name': '野格1瓶套餐', 'package_price': '329', 'package_unit': '元', 'activity': '', 'market_price': '469元', 'sales_volume': '6', 'package_rule': '野格1瓶350红牛4听68冰毛豆1份26薯片1份20', 'package_title': '仅售329元，价值469元野格1瓶套餐，免费WiFi！', 'sales_time_period': '半年消费6', 'effective_start_date': 'Jan 17, 2020 9:48:24 AM', 'effective_end_date': 'Oct 28, 2020 11:59:59 PM', 'items_data': [{'item_name': '野格套餐', 'item_price': '469', 'item_unit': '元', 'copies_nm': '1'}]}, {'package_id': '617853200', 'package_name': '豪帅龙舌兰银标1瓶套餐', 'package_price': '398', 'package_unit': '元', 'activity': '', 'market_price': '469元', 'sales_volume': '9', 'package_rule': '豪帅银标龙舌兰1瓶480雪碧4听60冰毛豆1份26薯片1份20纸巾1盒5', 'package_title': '仅售398元，价值469元豪帅龙舌兰银标1瓶套餐！', 'sales_time_period': '半年消费11', 'effective_start_date': 'Oct 30, 2019 11:57:18 AM', 'effective_end_date': 'Oct 28, 2020 11:59:59 PM', 'items_data': [{'item_name': '野格套餐', 'item_price': '469', 'item_unit': '元', 'copies_nm': '1'}]}, {'package_id': '630400901', 'package_name': '杰克丹尼1瓶套餐+小吃', 'package_price': '398', 'package_unit': '元', 'activity': '', 'market_price': '469元', 'sales_volume': '0', 'package_rule': '杰克丹尼1瓶480可乐4听60冰毛豆1份26薯片1份20纸巾1盒5', 'package_title': '仅售398元，价值469元杰克丹尼1瓶套餐+小吃，免费WiFi！', 'sales_time_period': '半年消费0', 'effective_start_date': 'Jan 17, 2020 6:30:34 PM', 'effective_end_date': 'Oct 28, 2020 11:59:59 PM', 'items_data': [{'item_name': '野格套餐', 'item_price': '469', 'item_unit': '元', 'copies_nm': '1'}]}]}, {'bar_id': '177453261', 'bar_name': '原点酒吧', 'tuan': '', 'juan': '', 'wai': '', 'bar_score': 4.0, 'business': '同德昆明广场', 'packages': []}, {'bar_id': '169154345', 'bar_name': '原点origin（同德店）', 'tuan': '', 'juan': '', 'wai': '', 'bar_score': 4.0, 'business': '同德昆明广场', 'packages': []}, {'bar_id': '182195280', 'bar_name': 'MAO Livehouse昆明店', 'tuan': '', 'juan': '', 'wai': '', 'bar_score': 3.5, 'business': '同德昆明广场', 'packages': []}, {'bar_id': '1634850214', 'bar_name': '享站吧精酿啤酒直供站（昆明广场店）', 'tuan': '', 'juan': '', 'wai': '外', 'bar_score': 4.0, 'business': '同德昆明广场', 'packages': []}, {'bar_id': '195843994', 'bar_name': 'LOU锈NGE', 'tuan': '', 'juan': '', 'wai': '', 'bar_score': 3.5, 'business': '同德昆明广场', 'packages': []}, {'bar_id': '177739371', 'bar_name': '倍轻松（同德昆明广场店）', 'tuan': '', 'juan': '', 'wai': '', 'bar_score': 3.5, 'business': '同德昆明广场', 'packages': []}, {'bar_id': '677223130', 'bar_name': 'The fall(坠） bar', 'tuan': '', 'juan': '', 'wai': '', 'bar_score': 0.0, 'business': '同德昆明广场', 'packages': []}]

        for i in data:
            package_num = 0
            print("i['bar_id'] is ", i['bar_id'])
            self.db.cursor.execute('select id from bar where bar_id = %s limit 1' % i['bar_id'])
            result = self.db.cursor.fetchone()
            if not result:
                # 新增数据
                self.db.insert_data('bar', {
                    'bar_id': i['bar_id'],
                    'bar_name': i['bar_name'],
                    'bar_score': i['bar_score'],
                    'bar_phone': i['bar_phone'],
                    # 'city': i['city'], # 默认昆明，代码暂时没有填
                    # 'area': i['area'], # 默认盘龙区，代码暂时没有填
                    'business': i['business'],
                    'bar_address': i['bar_address'],
                    'lng': i['lng'],
                    'lat': i['lat'],
                    'tuan': i['tuan'],
                    'juan': i['juan'],
                    'wai': i['wai'],
                    'bar_update_time': now
                })
                bar_num += 1
            else:  # 更新数据
                ...

            # 套餐信息：
            for package in i['packages']:
                self.db.cursor.execute('select id from bar_package where package_id = %s and package_update_time = %d limit 1' % (package['package_id'], now))
                has = self.db.cursor.fetchone()
                if not has: # 避免重复
                    self.db.insert_data('bar_package', {
                        'package_id': package['package_id'],
                        'bar_id': i['bar_id'],
                        'package_name': package['package_name'],
                        'package_price': package['package_price'],
                        'package_unit': package['package_unit'],
                        'activity': package['activity'],
                        # 'market_price': package['market_price'],
                        'sales_volume': package['sales_volume'],
                        'sales_time_period': package['sales_time_period'],
                        'effective_start_date': package['effective_start_date'],
                        'effective_end_date': package['effective_end_date'],
                        'package_title': package['package_title'],
                        # 'package_rule': package['package_rule'],
                        'package_update_time': now,
                    })
                    package_num += 1

                item_num = 0
                for item in package['items_data']:
                    self.db.cursor.execute('select id from bar_package_item where item_update_time = %d limit 1' % (now))
                    has2 = self.db.cursor.fetchone()
                    if not has:  # 避免重复
                        self.db.insert_data('bar_package_item', {
                            'item_name': item['item_name'],
                            'item_price': item['item_price'],
                            'item_unit': item['item_unit'],
                            'copies_nm': item['copies_nm'],
                            'item_rule': item['item_rule'],
                            'package_id': item['package_id'],
                            'item_update_time': now,
                        })
                        item_num += 1

        return bar_num
    
    
    def insert_data2(self,citys):
        """写入数据库"""
        rel = 0
        now = int(time.time())
        # 酒店信息
       
        # 新增数据
        self.db.insert_data('hotel', {
            'hotel_id': '456',
            'name': "456",
            'score': "789",
            'area': "101112",
            'address': "131415",
            'city': "161718",
            'update_time': now,
        })
        rel += 1
     

conf = {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': '123456','db': 'meituan_bar', 'charset': 'utf8'}
j = JiuBa(db_config=conf)
name = 'kunming'
bid = 14437 # 同德广场
j.insert_data('kunming', bid)