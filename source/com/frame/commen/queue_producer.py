# -*- coding: utf-8 -*-
"""
queue_producer.py
Created on 2019/5/13 23:29
Copyright 2019/5/13
@author: qcy
"""

import threading
from com.frame.util.log_util import LogUtil
from com.frame.commen.base_producer_action import ProducerAction
import time
from com.frame.commen.queue_consumer import ConsumerAction

class Producer(threading.Thread):
    """
    生产者线程
    """

    def __init__(self, queue, action, name, max_num, sleep_time, work_sleep_time, work_try_num):
        """
        初始化生产线程
        :param queue:
        :param action:
        :param name:
        :param max_num:
        :param seelp_time:
        :param work_sleep_time:
        :param work_try_num:
        """
        super(self.__class__, self).__init__()
        self.queue = queue
        self.action = action
        self.name = name
        self.max_num = max_num
        self.sleep_time = sleep_time
        self.work_sleep_time = work_sleep_time
        self.work_try_num = work_try_num
        self.rl = LogUtil().get_logger("producer", "producer" + self.name)
        if not isinstance(action, ProducerAction):
            raise Exception('Action not extends Producer base')

    def run(self):
        # 缓存生产者生产的消费动作，用于消费者线程有空闲时进行任务的填充
        action_list = []
        while True:
            try:
                start_time = time.clock()

                # 当缓存消费动作为空时，调用生产动作拿到新的一批消费动作
                if len(action_list) == 0:
                    action_list = self.action.queue_items()

                # 日志输出本次的消费动作有多少
                total_items = len(action_list)
                self.rl.info('get queue %s total items is %s' % (self.name, total_items))
                while True:
                    # 当缓存中的数据消耗完毕，退出循环，再次填充缓存
                    if len(action_list) == 0:
                        break
                    # 得到队列汇总work状态的消费动作有多少
                    unfinished_tasks = self.queue.unfinished_tasks
                    # 当work状态的消费动作小于消费者线程数时，就往队列中派发一个消费动作
                    if unfinished_tasks < self.max_num:
                        action = action_list.pop()
                        self.queue.put(action)
                end_time = time.clock()

                # 计算生产者完成本次生产任务的时间和频次
                sec = int(round(end_time - start_time))
                min = int(round(sec / float(60)))

                self.rl.info("put queue %s total items is %s,total time is %s\'s,(at %s items/min)" % \
                             (self.name, total_items, sec,
                              int(total_items) if min == 0 else round(float(total_items / float(min)), 2)))

                # 生产完一个任务之后的生产者休息的时间
                time.sleep(self.sleep_time)
            except:
                self.rl.exception()

    def start_work(self):
        """
        启动生产者线程和根据消费者线程的数量，设置启动对应数量的消费者线程
        """
        for i in range(0, self.max_num):
            qc = ConsumerAction(self.queue, self.name + "_" + str(i), self.work_sleep_time, self.work_try_num)
            qc.start()

        time.sleep(5)
        self.start()
