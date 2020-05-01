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


    def request(self, uri, params={}, timeout=5):

        # https://ihotel.meituan.com/group/v1/yf/list/182625269? =1&=&end=1558022400000&&poi=189285561&uuid=ca95f911ce774f3888f2.1557842544.1.0.0&iuuid=5C473294DD7181724F044F8D89DC9FBBAEBD8C0103686B511EF7D4DA04CB4857&_token=
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'Cookie': '__utmb=1',  # __utmb 移动端访问的标记
            'Connection': 'close',
        }
        s = curl.session()
        s.keep_alive = False  # 关闭多余连接

        re = s.get(uri, params=params, headers=headers, timeout=timeout) #必须设置超时时间使用代理不能一直等待
        return re

    def request_json(self, uri, params={}, timeout=5):
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'Cookie': '__utmb=1',  # __utmb 移动端访问的标记
            'Content-Type': 'application/json;charset=utf-8',
            'Connection': 'close',
        }
        s = curl.session()
        s.keep_alive = False  # 关闭多余连接

        re = s.get(uri, params=params, headers=headers, timeout=timeout).json()
        return re


    # 限时抢购按钮
    def read_ajax_page(self, goods_href):
        from selenium import webdriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(goods_href)
        page_source = driver.page_source
        soup_button = BeautifulSoup(page_source, "html.parser")
        button_str = soup_button.find("button", attrs={"class": "buy"})
        limit_price = 0.0
        if button_str:
            button_str = button_str.string
            if "¥" in button_str and "限时抢购" in button_str:
                index = button_str.find("限时抢购")
                limit_price = button_str[1:index].strip()
                try:
                    limit_price = float(limit_price)
                except:
                    print("¥ 限时抢购 字符串截取错误" )
        return limit_price


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
                package['limit_price'] = 0.0
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
                    goods1_des_href = "https:" + goods1_href
                    limit_price = self.read_ajax_page(goods1_des_href)
                    package["activity"] = activity
                    package["limit_price"] = limit_price

                market_price = goods1.find("del")
                if market_price is not None:
                    market_price = float(market_price.string[:-1])
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
                    goods1_content = j.request_json(goods_href, timeout=10)
                    print(goods1_content)

                    if goods1_content['optionalGroups'] or goods1_content['mustGroups']:
                        print(goods1_content['title'], goods1_content['marketPrice'], goods1_content['price'])
                        # if条件判断认为：1、字符串非空、数字非0、数字非0.0 为True；2、字符串空、数字0、数字0.0 为False：
                        if not package["market_price"]:
                            package["market_price"] = float(goods1_content['marketPrice'][:-1])
                        if goods1_content['desc']:
                            package["package_rule"] = BeautifulSoup(goods1_content['desc'], "html.parser").text

                    if goods1_content['optionalGroups']:
                        for goods1_group in goods1_content['optionalGroups']:
                            print(goods1_group['desc'])
                            for item in goods1_group['dealStructInfo']:
                                print(item['title'], item['price'], item['copies'])
                                item_data_1 = {}
                                item_data_1["item_name"] = ""
                                item_data_1["item_price"] = 0.0
                                item_data_1["item_unit"] = ""
                                item_data_1["copies_nm"] = 0
                                item_data_1["item_rule"] = ""
                                item_data_1["item_name"] =  item['title']
                                item_data_1["item_price"] = item['price'][:-1]
                                item_data_1["item_unit"] = item['price'][-1]
                                item_data_1["copies_nm"] = item['copies'][:-1]
                                if "desc" in goods1_group.keys():
                                    item_data_1["item_rule"] = goods1_group['desc']
                                items_data.append(item_data_1)
                            print("-" * 30)
                    if goods1_content['mustGroups']:
                        for goods1_group in goods1_content['mustGroups']:
                            for items in goods1_group['dealStructInfo']:
                                item_data_2 = {}
                                item_data_2["item_name"] = ""
                                item_data_2["item_price"] = 0.0
                                item_data_2["item_unit"] = ""
                                item_data_2["copies_nm"] = 0
                                item_data_2["item_rule"] = ""
                                item_data_2["item_name"] = items['title']
                                item_data_2["item_price"] = items['price'][:-1]
                                item_data_2["item_unit"] = items['price'][-1]
                                item_data_2["copies_nm"] = items['copies'][:-1]
                                if "desc" in items.keys():
                                    item_data_2["item_rule"] = items['desc']
                                # for item in items["items"]:
                                #     print(item['value'], item['name'])
                                items_data.append(item_data_2)
                            print("-" * 30)

                    main1_href = "https://i.meituan.com/general/platform/mttgdetail/mtdealbasegn.json?dealid=" + goods1_href_temp2 + "&shopid=&eventpromochannel=&stid=&lat=&lng="
                    print(main1_href)
                    main1_content = j.request_json(main1_href, timeout=10)
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

                except IndexError as ie:
                    print('IndexError', ie)
                except KeyError as ke:
                    print('KeyError', ke)
                except Exception as e:
                    print('Error', e)
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
        data = self.build_data(city, business_id)

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
                        'limit_price': package["limit_price"],
                        'market_price': package['market_price'],
                        'sales_volume': package['sales_volume'],
                        'sales_time_period': package['sales_time_period'],
                        'effective_start_date': package['effective_start_date'],
                        'effective_end_date': package['effective_end_date'],
                        'package_title': package['package_title'],
                        'package_rule': package['package_rule'],
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
                            'package_id': package['package_id'],
                            'item_update_time': now,
                        })
                        item_num += 1

        return bar_num
    

conf = {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': 'root','db': 'meituan_bar', 'charset': 'utf8mb4'}
j = JiuBa(db_config=conf)
name = 'kunming'
bid = 14437 # 同德广场
j.insert_data('kunming', bid)