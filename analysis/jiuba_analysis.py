# -*- coding: utf-8 -*-
"""
Created on Fri May  1 14:55:19 2020

@author: dell
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
ft.set_file_path(r"E:\code\python_workSpace\idea_space\meituan_hotel\analysis")
import Tools_customize as tc
import Binning_tools as bt
from sqlalchemy import create_engine

# In[]:
# i.meituan.com
# 一、表读取
sql = "select * from bar_view"
bar_data = ft.read_from_mysql(sql, "root", "root", "127.0.0.1", "3306", "meituan_bar")

# In[]:
mis_val_table_ren_columns = ft.missing_values_table(bar_data)

# In[]:
bar_data['bar_phone'] = bar_data['bar_phone'].map(lambda x: np.nan if not x else x)
bar_data['bar_address'] = bar_data['bar_address'].map(lambda x: np.nan if not x else x)
bar_data['tuan'] = bar_data['tuan'].map(lambda x: np.nan if not x else x)
bar_data['juan'] = bar_data['juan'].map(lambda x: np.nan if not x else x)
bar_data['wai'] = bar_data['wai'].map(lambda x: np.nan if not x else x)

bar_data['package_id'] = bar_data['package_id'].map(lambda x: np.nan if not x else x)
bar_data['package_name'] = bar_data['package_name'].map(lambda x: np.nan if not x else x)

bar_data['package_unit'] = bar_data['package_unit'].map(lambda x: np.nan if not x else x)
bar_data['activity'] = bar_data['activity'].map(lambda x: np.nan if not x else x)

bar_data['sales_time_period'] = bar_data['sales_time_period'].map(lambda x: np.nan if not x else x)
bar_data['effective_start_date'] = bar_data['effective_start_date'].map(lambda x: np.nan if not x else x)
bar_data['effective_end_date'] = bar_data['effective_end_date'].map(lambda x: np.nan if not x else x)
bar_data['package_title'] = bar_data['package_title'].map(lambda x: np.nan if not x else x)
bar_data['package_rule'] = bar_data['package_rule'].map(lambda x: np.nan if not x else x)

bar_data['item_name'] = bar_data['item_name'].map(lambda x: np.nan if not x else x)
bar_data['item_unit'] = bar_data['item_unit'].map(lambda x: np.nan if not x else x)
bar_data['item_rule'] = bar_data['item_rule'].map(lambda x: np.nan if not x else x)
bar_data['package_update_time'] = bar_data['package_update_time'].map(lambda x: np.nan if not x else x)

# In[]:
bar_data['sales_time_period'] = bar_data['sales_time_period'].map(lambda x: int(x[4:]) if x is not np.nan else x)

# In[]:
sns.set(font='SimHei', font_scale=1.3)
# In[]:
# 1、不同酒吧评分
fig, ax = plt.subplots(1,1,figsize=(10,20))
sns.barplot(x='bar_score',y='bar_name',data =bar_data, ax=ax, ci=None)
ax.set_xlabel("酒吧得分")
ax.set_ylabel("酒吧名称")
ax.set_title("不同酒吧评分")

# In[]:
bar_group_max = bar_data.groupby(["bar_name", "package_name"], as_index=False)[['package_price','sales_time_period']].max()
# In[]:
# 2、不同酒吧套餐总价
fig, ax = plt.subplots(1,1,figsize=(10,20))
sns.barplot(x='bar_name', y='package_price', data =bar_group_max, ax=ax, ci=None, estimator=sum,
           order=bar_group_max.groupby("bar_name")['package_price'].sum().sort_values(ascending=False).index
           )
fig.autofmt_xdate(rotation = 45)
ax.set_xlabel("酒吧名称")
ax.set_ylabel("酒吧套餐总价")
ax.set_title("不同酒吧套餐总价")

# In[]:
# 3、酒吧套餐类别
fig, ax = plt.subplots(2,2,figsize=(18,20))
sns.barplot(x='bar_name', y='package_price', hue='package_name' ,data=bar_group_max[bar_group_max['bar_name']=='花家+（昆明广场店）'], ax=ax[0][0], ci=None, estimator=sum,
            hue_order=bar_group_max[bar_group_max['bar_name']=='花家+（昆明广场店）'].groupby("package_name")['package_price'].sum().sort_values(ascending=False).index
           )
ax[0][0].set_xlabel("")
ax[0][0].set_ylabel("套餐价格")
ax[0][0].set_title("花家+（昆明广场店）酒吧套餐类别价格")

sns.barplot(x='bar_name', y='package_price', hue='package_name' ,data=bar_group_max[bar_group_max['bar_name']=='黑森林酒吧（同德店）'], ax=ax[0][1], ci=None, estimator=sum,
            hue_order=bar_group_max[bar_group_max['bar_name']=='黑森林酒吧（同德店）'].groupby("package_name")['package_price'].sum().sort_values(ascending=False).index
           )
ax[0][1].set_xlabel("")
ax[0][1].set_ylabel("")
ax[0][1].set_title("黑森林酒吧（同德店）酒吧套餐类别价格")

sns.barplot(x='bar_name', y='package_price', hue='package_name' ,data=bar_group_max[bar_group_max['bar_name']=='长亭酒馆（同德昆明广场店）'], ax=ax[1][0], ci=None, estimator=sum,
            hue_order=bar_group_max[bar_group_max['bar_name']=='长亭酒馆（同德昆明广场店）'].groupby("package_name")['package_price'].sum().sort_values(ascending=False).index
           )
#fig.autofmt_xdate(rotation = 45)
ax[1][0].set_xlabel("")
ax[1][0].set_ylabel("套餐价格")
ax[1][0].set_title("长亭酒馆（同德昆明广场店）酒吧套餐类别价格")

sns.barplot(x='bar_name', y='package_price', hue='package_name' ,data=bar_group_max[bar_group_max['bar_name']=='WOW酒馆（北京路店）'], ax=ax[1][1], ci=None, estimator=sum,
            hue_order=bar_group_max[bar_group_max['bar_name']=='WOW酒馆（北京路店）'].groupby("package_name")['package_price'].sum().sort_values(ascending=False).index
           )
#fig.autofmt_xdate(rotation = 45)
ax[1][1].set_xlabel("")
ax[1][1].set_ylabel("")
ax[1][1].set_title("WOW酒馆（北京路店）酒吧套餐类别价格")

# In[]:
# 4、酒吧套餐销售数量
fig, ax = plt.subplots(2,2,figsize=(18,20))
sns.barplot(x='bar_name', y='sales_time_period', hue='package_name' ,data=bar_group_max[bar_group_max['bar_name']=='花家+（昆明广场店）'], ax=ax[0][0], ci=None, estimator=sum,
            hue_order=bar_group_max[bar_group_max['bar_name']=='花家+（昆明广场店）'].groupby("package_name")['sales_time_period'].sum().sort_values(ascending=False).index
           )
ax[0][0].set_xlabel("")
ax[0][0].set_ylabel("半年内套餐销售数量")
ax[0][0].set_title("花家+（昆明广场店）酒吧半年内套餐类别销量")


sns.barplot(x='bar_name', y='sales_time_period', hue='package_name' ,data=bar_group_max[bar_group_max['bar_name']=='黑森林酒吧（同德店）'], ax=ax[0][1], ci=None, estimator=sum,
            hue_order=bar_group_max[bar_group_max['bar_name']=='黑森林酒吧（同德店）'].groupby("package_name")['sales_time_period'].sum().sort_values(ascending=False).index
           )
ax[0][1].set_xlabel("")
ax[0][1].set_ylabel("")
ax[0][1].set_title("黑森林酒吧（同德店）酒吧半年内套餐类别销量")


sns.barplot(x='bar_name', y='sales_time_period', hue='package_name' ,data=bar_group_max[bar_group_max['bar_name']=='长亭酒馆（同德昆明广场店）'], ax=ax[1][0], ci=None, estimator=sum,
            hue_order=bar_group_max[bar_group_max['bar_name']=='长亭酒馆（同德昆明广场店）'].groupby("package_name")['sales_time_period'].sum().sort_values(ascending=False).index
           )
#fig.autofmt_xdate(rotation = 45)
ax[1][0].set_xlabel("")
ax[1][0].set_ylabel("半年内套餐销售数量")
ax[1][0].set_title("长亭酒馆（同德昆明广场店）酒吧半年内套餐类别销量")


sns.barplot(x='bar_name', y='sales_time_period', hue='package_name' ,data=bar_group_max[bar_group_max['bar_name']=='WOW酒馆（北京路店）'], ax=ax[1][1], ci=None, estimator=sum,
            hue_order=bar_group_max[bar_group_max['bar_name']=='WOW酒馆（北京路店）'].groupby("package_name")['sales_time_period'].sum().sort_values(ascending=False).index
           )
#fig.autofmt_xdate(rotation = 45)
ax[1][1].set_xlabel("")
ax[1][1].set_ylabel("")
ax[1][1].set_title("WOW酒馆（北京路店）酒吧半年内套餐类别销量")

# In[]:
# 5、酒吧套餐商品明细
#bar_group_item_max = bar_data.groupby(["bar_name", "package_name", 'item_name'], as_index=False)[['package_price','sales_time_period','item_price', 'copies_nm','item_rule']].max()

# In[]:
bar_data['limit_price'] = bar_data['limit_price'].map(lambda x: 0 if isnan(x) else x)
# In[]:
ccc = bar_data[bar_data['limit_price'] != 0]
# In[]:
