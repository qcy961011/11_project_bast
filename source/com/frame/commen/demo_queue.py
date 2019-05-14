# -*- coding: utf-8 -*-
"""
demo_queue.py
Created on 2019/5/14 10:08
Copyright 2019/5/14
@author: qcy
"""
from queue import Queue

from com.frame.util.log_util import LogUtil
from com.frame.commen.queue_consumer import ConsumerAction
from com.frame.commen import base_consumer_action
from com.frame.commen import base_producer_action
from com.frame.commen import queue_producer

class DemoConsumerAction(base_consumer_action.ConsumerAction):

    def __init__(self, text):
        """
        初始化消费者实现类
        :param text:
        """
        super(self.__class__, self).__init__()
        self.text = text
        self.rl = LogUtil().get_base_logger()

    def action(self):
        """
        消费者的具体实现

        :return:
        """
        result = True
        r_test = ''
        try:
            r_test = "Demo" + str(self.text)
        except:
            result = False
            self.rl.exception()

        return self.result(result, [r_test])

    def fail_cation(self, values):
        if self.try_num >= ConsumerAction._WORK_TRY_NUM:
            pass

    def success_action(self, values):
        pass


class DemoProducerAction(base_producer_action.ProducerAction):

    def queue_items(self):
        """
        生成指定的消费者动作
        :return:
        """
        _list = []
        for i in range(0, 100):
            c = DemoConsumerAction(i)
            _list.append(c)
        return _list


if __name__ == "__main__":
    # 初始化使用的队列
    q = Queue()
    # 初始化生产者动作
    pp = DemoProducerAction()
    # 初始化生产者
    p = queue_producer.Producer(q, pp, "qiao", 100, 10, 3, 3)
    # 启动整个生产和消费任务
    p.start_work()
