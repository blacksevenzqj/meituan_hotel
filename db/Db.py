import pymysql

class Db:
    '''
    简单数据库连接操作类
    '''
    def __init__(self,**kwargs):
        # host='10.10.10.10',port=3306,user='root',password='root',db='meituan_hotel',charset='utf8'
        self.connection = pymysql.connect(**kwargs)
        self.cursor = self.connection.cursor()

    def insert_data(self,table,data,not_str_filed=[]):
        '''
        根据dict数据写入数据表
        :param table:表名
        :param data: 写入的数据 dict类型
        :param not_str_filed:非字符串的字段，默认自动识别
        :return:
        '''
        fields = data.keys()
        values = []
        for index,item in enumerate(fields):
            val = data[item]
            if item in not_str_filed or not isinstance(val,str):#非字符串的字段，使用源数据放入
                val = str(val)#必须使用str，否则', '.join(values)报错，因为join的列表元素必须是字符串
                val = pymysql.escape_string(val)
            else:#用字符串引号包裹
                val = '"{0}"'.format(pymysql.escape_string(str(val)))


            values.append(val)

        assert len(fields) == len(values), '数据拼接错误'
        fields = ['`%s`' % item for item in fields]
        fields = ', '.join(fields)
        values = ', '.join(values)

        sql = 'INSERT INTO `{table}` ({fields}) VALUES ({values})'.format(table=table, fields=fields,values=values)

        # return sql
        effect_row = self.cursor.execute(sql)
        self.connection.commit()
        return effect_row

#
# m = Db(**{'host': '10.10.10.10', 'port': 3306, 'user': 'root', 'password': 'root', 'db': 'meituan_hotel', 'charset': 'utf8'})
# rel = m.insert_data('hotel',{
#     'name':122,
# })
# print(rel)



