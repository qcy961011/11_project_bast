# -*- coding: utf-8 -*-
"""
configs.py
Created on 2019/5/14 0:02
Copyright 2019/5/14
@author: qcy
"""

# 日志地址
_LOG_DIR = 'E:/log/%s'
# base_url : base_url_producer_name
_BASE_URL_PRODUCE_NAME = "producer_url"
# base_url : max_num 启动的消费者的数量
_BASE_URL_MAX_NUMBER = 2
# base_url : sleep_time 执行下一次生产动作时休息的时间
_BASE_URL_SLEEP_TIME = 30
# base_url : work_sleep_time 每个消费者的休息时间
_BASE_URL_WORK_SLEEP_TIME = 5
# base_url : work_try_num 每个消费者动作允许失败的次数
_BASE_URL_WORK_TRY_NUMBER = 3

# DBConfigs
_DB_CONFIG = {'HOST': '192.168.88.195', 'USER': 'hainiu', 'PASSWD': '12345678', 'DB': 'hainiutest', 'CHARSET': 'utf8',
              'PORT': 3306}
