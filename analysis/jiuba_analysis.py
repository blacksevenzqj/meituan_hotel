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
# 一、表读取
sql = "SELECT a.`bar_id`, a.bar_name,a.bar_score,a.bar_phone,a.city,a.area,a.business,a.bar_address,a.tuan,a.juan,a.wai,FROM_UNIXTIME(a.bar_update_time, '%%Y-%%m-%%d %%H:%%i:%%S') AS bar_update_time,b.package_id, b.package_name, b.package_price, b.package_unit,b.`activity`,b.`limit_price`,b.`market_price`,b.`sales_volume`,b.`sales_time_period`,b.`effective_start_date`,b.`effective_end_date`,b.`package_title`,b.`package_rule`,c.`id`, c.item_name,c.`item_price`,c.`item_unit`,c.`copies_nm`,c.`item_rule`FROM `bar` a LEFT JOIN `bar_package` b ON a.`bar_id` = b.`bar_id` LEFT JOIN `bar_package_item` c ON b.`package_id` = c.`package_id` ORDER BY a.`bar_score` DESC, b.`package_name` DESC, c.`item_rule` DESC"
data = ft.read_from_mysql(sql, "root", "root", "127.0.0.1", "3306", "meituan_bar")