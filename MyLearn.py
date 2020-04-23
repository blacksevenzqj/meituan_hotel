import base64
import zlib
import re,json,os
from datetime import datetime
import requests as curl, time
from pyquery import PyQuery as pq
from db.Db import Db
from multiprocessing import Pool

class Meituan2:
    def __init__(self, db_config):
        """
        :param db_config:数据库连接配置
        """
        self.db = Db(**db_config)
        # self.proxies_list = []
        #载入代理池
        # self.load_proxy_list()

    # def load_proxy_list(self,proxy_file_path = '/root/proxy_list_xigua.txt'):
    #     '''
    #     载入代理池
    #     :return:
    #     '''
    #     proxies_list = []
    #     # proxy_file_path = 'dict.txt'
    #     if os.path.isfile(proxy_file_path):
    #         with open(proxy_file_path) as f:
    #             for line in f.readlines():
    #                 line = line.strip()
    #                 if line:
    #                     proxies_list.append(line)
    #     self.proxies_list = proxies_list

    # def get_proxy(self):
    #     '''
    #     代理池出栈操作
    #     :return:
    #     '''
    #     if not self.proxies_list: # 代理池为空  俩情况：1.第一次没有载入，2.载入之后被使用完一遍了
    #         self.load_proxy_list()

    #     if self.proxies_list:
    #         return self.proxies_list.pop(0) #弹出第一个
    #     return None


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
        # from requests.packages.urllib3.exceptions import InsecureRequestWarning
        # curl.packages.urllib3.disable_warnings(InsecureRequestWarning)
        # return curl.get(uri,params=params,headers=headers,verify=False)

        # curl.adapters.DEFAULT_RETRIES = 5
        s = curl.session()
        s.keep_alive = False  # 关闭多余连接

        # while True:
        #     try:
        #         re = s.get(uri, params=params, headers=headers, timeout=5) #必须设置超时时间使用代理不能一直等待
        #         return re
        #     # except curl.exceptions.ProxyError as e:
        #     #     raise e
        #     except:#查找自动代理文件
        #         # print("Connection refused by the server..")
        #         # print("Let me sleep for 5 seconds")
        #         # print("ZZzzzz...")
        #         time.sleep(5)
        #         continue
        re = s.get(uri, params=params, headers=headers, timeout=5) #必须设置超时时间使用代理不能一直等待
        return re


    def hotel_rooms(self, id):
        '''
        读取当天的酒店房间数据
        :param id:
        :return:
        '''
        now = datetime.now()
        now_00 = int(datetime(now.year, now.month, now.day, 0, 0).timestamp())  # 当天凌晨点的时间戳
        params = {
            'utm_medium': 'touch',
            'platformid': '1',
            'version_name': '999.9',
            'start': now_00 * 1000,
            'end': (now_00 + 86400) * 1000,
            # 'version_name':'999.9',
            # 'type':'0',
            '_token': self.build_token()
        }
        uri = 'https://ihotel.meituan.com/group/v1/yf/list/%d' % id
        try:
            _room_info = self.request(uri=uri, params=params)
            room_info = _room_info.json()
            return room_info
        except json.decoder.JSONDecodeError as e:
            # print(_room_info.text)
            print(_room_info.status_code)
            raise e


    def read_city_hotels(self, name):
        '''
        读取指定城市的酒店列表
        :param name:城市名的拼音，如 昆明：kunming,郑州：zhengzhou
        :return:
        '''
        # rel = []
        page = 1
        while True:
            url = r'https://i.meituan.com/s/%s-电竞酒店?p=%d' % (name, page)
            content = self.request(url).text
            document = pq(content)
            hotel_list_selecter = document('dd.poi-list-item')
            length = hotel_list_selecter.length
            if length < 1:
                break

            for item in hotel_list_selecter.items():
                score = item.find('em.star-text').text().strip()
                link = item.find('a').attr('href')
                id = re.search(r'/(\d+)', link)
                if id:  # 没有id  应该就是广告
                    id = id.group(1)
                else:
                    continue

                # 酒店信息
                rel_item = (
                    int(id),
                    item.find('span.poiname').text().strip(),  # 标题
                    float(score if score else 0),  # 评分
                    item.find('p[data-com]').text().strip(),  # 地址
                )
                yield rel_item
                # rel.append(rel_item)
            else:
                page = page + 1

        # return rel
                
    # def read_city_hotels(self, name):
    #     '''
    #     读取指定城市的酒店列表
    #     :param name:城市名的拼音，如 昆明：kunming,郑州：zhengzhou
    #     :return:
    #     '''
    #     # rel = []
    #     page = 1
    #     url = r'https://i.meituan.com/s/%s-电竞酒店?p=%d' % (name, page)
    #     content = self.request(url).text
    #     document = pq(content)
    #     hotel_list_selecter = document('dd.poi-list-item')
    #     length = hotel_list_selecter.length
    #     if length < 1:
    #         return
    #
    #     for item in hotel_list_selecter.items():
    #         score = item.find('em.star-text').text().strip()
    #         link = item.find('a').attr('href')
    #         id = re.search(r'/(\d+)', link)
    #         if id:  # 没有id  应该就是广告
    #             id = id.group(1)
    #         else:
    #             return
    #
    #         # 酒店信息
    #         rel_item = (
    #             int(id),
    #             item.find('span.poiname').text().strip(),  # 标题
    #             float(score if score else 0),  # 评分
    #             item.find('p[data-com]').text().strip(),  # 地址
    #         )
    #         yield rel_item
    #         # rel.append(rel_item)
    #     else:
    #         page = page + 1
    #
    #     # return rel


    def read_hotel_info(self, id):
        """
        读取酒店详情
        :param id: 酒店id
        :return:
        """
        now = datetime.now()
        now_00 = int(datetime(now.year, now.month, now.day, 0, 0).timestamp())  # 当天凌晨点的时间戳
        params = {
            'utm_medium': 'touch',
            'platformid': '1',
            'version_name': '999.9',
            'start': now_00 * 1000,
            'end': (now_00 + 86400) * 1000,
            # 'version_name':'999.9',
            # 'type':'0',
            '_token': self.build_token()
        }
        uri = 'https://ihotel.meituan.com/group/v1/poi/%d' % id
        try:
            _hotel_info = self.request(uri=uri, params=params)
            hotel_info = _hotel_info.json()
            if hotel_info and hotel_info['data']:
                return hotel_info['data'][0]
        except json.decoder.JSONDecodeError as e:
            # print(_hotel_info.text)
            print(_hotel_info.status_code)
            raise e

        return False


    def build_data(self, citys):
        """
        准备写入的数据
        :param list|str citys:城市名字（拼音）,字符串需要英文逗号间隔
        :return:
        """
        rel = {}  # 城市下的酒店-房间信息
        m = self
        if isinstance(citys, str):
            citys = citys.split(',')

        print(citys)
        for city in citys:
            print(city)
            # city_hotels = m.read_city_hotels(name='kunming')  # 读取城市下的所有酒店列表
            city_hotels = m.read_city_hotels(name=city)  # 读取城市下的所有酒店列表
            
            print(city_hotels)
            
            for (index, item) in enumerate(city_hotels):
                rel[item[0]] = {
                    'info': item,
                    'rooms': [],
                    'city': city,
                }

                rooms_info = m.hotel_rooms(item[0])
                if rooms_info['data']['result']:
                    for room in rooms_info['data']['result']:
                        name = ''
                        if room['goodsRoomModels'] and room['goodsRoomModels'][0]['roomName']:
                            name = room['goodsRoomModels'][0]['roomName']
                        else:
                            name = room['goodsName'].split('-')[0].split('，')[-1]  # 房间名

                        goodsid = room['goodsId']

                        desc_list = [item['targetName'] for item in room[
                            'lowStarServiceInformationList']]  # room['lowStarServiceInformationList'][0]['targetName']
                        desc_list.append(room['cancelRule'])
                        desc_list = sorted(set(desc_list), key=desc_list.index)  # 去重 按照之前顺序排序
                        desc = ' '.join(str(i) for i in desc_list)#保证desc_list元素为str类型

                        invRemain = -1  # 剩余数量 0满房，-1不可用
                        if room['goodsStatus'] == 1:  # 可预定
                            invRemain = room['invRemain']  # 剩余数量
                            if invRemain == 0:
                                invRemain = float('inf')  # 设置为无穷大
                        elif room['goodsStatus'] == 0:  # 满房
                            invRemain = 0
                        else:  # 暂不可订
                            ...

                        price = room['averagePrice'] / 100

                        rel[item[0]]['rooms'].append({
                            'goodsid': goodsid,
                            'name': name,
                            'price': price,
                            'inv_remain': str(invRemain),  # 剩余房间数
                            'desc': desc,
                            'use_time': room['useTime'],
                        })


                    yield rel[item[0]]

        # return rel


    def insert_data(self,citys):
        """写入数据库"""
        rel = 0

        now = int(time.time())
        data = self.build_data(citys)
        print(data)

        for i in data:
            hotel_info = self.read_hotel_info(i['info'][0])  # 读取酒店详情信息

            # 酒店信息
            self.db.cursor.execute('select id from hotel where hotel_id = %d limit 1' % i['info'][0])
            result = self.db.cursor.fetchone()
            if not result:
                # 新增数据
                self.db.insert_data('hotel', {
                    'hotel_id': i['info'][0],
                    'name': i['info'][1],
                    'score': str(i['info'][2]),
                    'area': i['info'][3],
                    'address': hotel_info.get('addr', ''),
                    'city': i['city'],
                    'update_time': now,
                })
                rel += 1
            else:  # 更新数据
                ...

            # 房间信息
            for room in i['rooms']:
                self.db.cursor.execute('select id from hotel_room where goods_id = %d and time = %d limit 1' % (room['goodsid'], now))
                has = self.db.cursor.fetchone()
                if not has:#避免重复
                    self.db.insert_data('hotel_room', {
                        'goods_id': room['goodsid'],
                        'hotel_id': i['info'][0],
                        'name': room['name'],
                        'price': room['price'],
                        'inv_remain': str(room['inv_remain']),
                        'desc': room['desc'],
                        'use_time': room['use_time'],
                        'time': now,
                    })
                    rel += 1

        return rel
    
    
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
     

# if __name__ == '__main__':
#     start = datetime.now()

#     def run(name):
#         # conf = {'host': '10.10.10.10', 'port': 3306, 'user': 'root', 'password': 'root', 'db': 'meituan_hotel', 'charset': 'utf8'} # todo
#         # conf = {'host': '47.240.23.55', 'port': 3306, 'user': 'root', 'password': 'su^uBXZZw7w?EsmgvAt{x', 'db': 'meituan_hotel','charset': 'utf8'}
#         conf = {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': '123456','db': 'meituan_hotel', 'charset': 'utf8'}
#         m = Meituan(db_config=conf)
#         return m.insert_data([name])

#     # 线程池操作
#     p = Pool(5)  # 最多5个线程
#     res = {}
#     # citys = ['kunming', 'zhengzhou', 'chengdu']
#     citys = ['kunming']
#     for i in citys:
#         res[i] = p.apply_async(run, args=(i,))
#     p.close()
#     p.join()

#     re = 0
#     re_ = {}
#     for city in res:
#         item = res[city]
#         count = item.get() #获取进程运行的返回值
#         re += count
#         re_[city] = count

#     stop = datetime.now()
#     print('%s insert total num: %d ,time-consuming:%s  %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), re, stop - start, re_))

# https://blog.csdn.net/weixin_41679826/article/details/85937767
    
    
# In[]:
conf = {'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': 'root','db': 'meituan_hotel', 'charset': 'utf8'}
m = Meituan2(db_config=conf)
m.insert_data(['kunming'])
    
    
    
    
    