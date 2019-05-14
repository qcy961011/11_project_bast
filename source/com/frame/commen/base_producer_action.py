# -*- coding: utf-8 -*-
"""
base_producer_action.py
Created on 2019/5/13 23:24
Copyright 2019/5/13
@author: qcy
"""
class ProducerAction:
    """
     生产者基类
    """

    def queue_items(self):
        """
        得到消费任务，用于放于到队列中，供消费进程使用
        :return:
        """
    pass
