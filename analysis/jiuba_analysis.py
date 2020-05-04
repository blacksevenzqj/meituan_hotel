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
sql = "select * from bar_view"
data = ft.read_from_mysql(sql, "root", "root", "127.0.0.1", "3306", "meituan_bar")