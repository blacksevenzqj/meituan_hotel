# -*- coding: utf-8 -*-
"""
Created on Fri May 15 10:49:00 2020

@author: Administrator
"""

import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')
import itertools
import matplotlib.gridspec as gridspec

from math import isnan
import FeatureTools as ft
# ft.set_file_path(r"E:\code\python_workSpace\idea_space\meituan_hotel\analysis")
import Tools_customize as tc
import Binning_tools as bt
from sqlalchemy import create_engine

# In[]:
# i.meituan.com
# 一、表读取
sql = "select * from hotel_orders_view"
hotel_orders_data = ft.read_from_mysql(sql, "wx_fyinn", "CBSFWPFkzwtL8382", "47.108.49.9", "3306", "wx_fyinn")
# In[]:
hotel_orders_data2 = hotel_orders_data.copy()

# In[]:
hotel_orders_data2['o_rt_hotel_room_size'] = hotel_orders_data2['o_rt_hotel_room_size'].map(lambda x: np.float16(x[0:x.find('平方米')]) if '平方米' in x else np.float16(x))

# In[]:
print(hotel_orders_data2.iloc[0]['o_pay_time'], type(hotel_orders_data2.iloc[0]['o_pay_time']))
print(hotel_orders_data2.iloc[3]['o_pay_time'], type(hotel_orders_data2.iloc[3]['o_pay_time']), hotel_orders_data2.iloc[3]['o_pay_time'] is pd.NaT)
print(hotel_orders_data2['o_pay_time'].dtypes)
# In[]:
hotel_orders_data2['o_pay_time'] = pd.to_datetime(hotel_orders_data2['o_pay_time'], format = "%Y-%m-%d %H:%M:%S", errors = 'coerce')
# hotel_orders_data2['o_pay_time'] = hotel_orders_data2['o_pay_time'].map(lambda x: pd.NaT if x is  None else pd.to_datetime(x, format = "%Y-%m-%d %H:%M:%S", errors = 'coerce'))

# In[]:
print(hotel_orders_data2.iloc[0]['o_create_time'], type(hotel_orders_data2.iloc[0]['o_create_time']))
print(hotel_orders_data2.iloc[3]['o_create_time'], type(hotel_orders_data2.iloc[3]['o_create_time']), hotel_orders_data2.iloc[3]['o_create_time'] is pd.NaT)
print(hotel_orders_data2['o_create_time'].dtype)
# In[]:
hotel_orders_data2['o_create_time'] = pd.to_datetime(hotel_orders_data2['o_create_time'], format = "%Y-%m-%d %H:%M:%S", errors = 'coerce')

# In[]:
print(hotel_orders_data2['o_rt_hotel_room_computer'].iloc[4], type(hotel_orders_data2.iloc[4]['o_rt_hotel_room_computer']))
# In[]:
hotel_orders_data2['o_rt_hotel_room_computer'] = hotel_orders_data2['o_rt_hotel_room_computer'].astype(np.int8)

# In[]:
print(hotel_orders_data2['o_rt_hotel_room_computer'].iloc[4], type(hotel_orders_data2.iloc[4]['o_rt_hotel_room_computer']))
print(hotel_orders_data2['o_rt_hotel_room_member'].iloc[4], type(hotel_orders_data2.iloc[4]['o_rt_hotel_room_member']))

# In[]:
hotel_orders_data3 = hotel_orders_data2.copy()

# In[]:
print(hotel_orders_data3.info())
hotel_orders_data3 = ft.reduce_mem_usage(hotel_orders_data3)
print(hotel_orders_data3.info())

# In[]:
mis_val_table_ren_columns = ft.missing_values_table(hotel_orders_data2)

# In[]:
print(hotel_orders_data3['o_room_number'].isna())
hotel_orders_data3['o_room_number'] = hotel_orders_data3['o_room_number'].fillna(np.nan)

# In[]:
















