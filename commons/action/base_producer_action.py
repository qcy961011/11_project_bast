#-*- encoding: utf-8 -*-
'''
base_producer_action.py
Created on 2018/8/30 下午2:19
Copyright (c) 2018/8/30, 海牛学院版权所有.
@author: 青牛
'''
class ProducerAction(object):
    '''
    生产者的基类
    '''

    def queue_items(self):
        '''
        得到消费任务，用于放于到队列中，供消费进程使用

        :return:        消息动作
        '''
        pass