#pip install --upgrade setuptools
# https://blog.csdn.net/somezz/article/details/83104368

import time, datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

def func():
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('do func time :',ts)
 
def func2():
    #耗时2S
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('do func2 time：',ts)
    time.sleep(2)
 
def dojob():

    scheduler = BlockingScheduler()
    
    #添加任务,时间间隔2S
    scheduler.add_job(func, trigger='interval', seconds=2)
    #添加任务,时间间隔5S
    scheduler.add_job(func2, trigger='interval', seconds=3, id='test_job2')
    scheduler.start()
 
dojob()


# In[]:
from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler

def tick():
    print('Tick! The time is: %s' % datetime.now())

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', seconds=3)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C    '))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
