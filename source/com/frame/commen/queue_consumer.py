# -*- coding: utf-8 -*-
"""
queue_consumer.py
Created on 2019/5/13 23:27
Copyright 2019/5/13
@author: qcy
"""
import random
import threading
from com.frame.commen import base_consumer_action
from com.frame.util.log_util import LogUtil
import time


class ConsumerAction(threading.Thread):
    """
    消费者线程，主要任务是执行拿到的消费动作
    """

    # 消费动作失败之后的重试尝试的次数，可供外面访问
    _WORK_TRY_NUM = 0

    def __init__(self, queue, name, sleep_time, work_try_num):
        """
        初始化消费线程
        :param queue:           使用的队列
        :param name:            消费者线程的名称，用其代表消费者的名字
        :param sleep_time:      执行下一次消费动作的休息时间
        :param work_try_num:    每个消费动作允许失败的次数
        """
        super(self.__class__, self).__init__()
        self.queue = queue
        self.name = name
        self.sleep_time = sleep_time
        self.work_try_num = work_try_num
        ConsumerAction._WORK_TRY_NUM = work_try_num
        self.rl = LogUtil().get_logger('consumer', 'consumer' + self.name[:self.name.find("_")])

    def run(self):
        while True:
            try:
                action = self.queue.get()
                if not isinstance(action, base_consumer_action.ConsumerAction):
                    raise Exception('Action not extends consumer base')
                sleep_time = random.randint(0, self.sleep_time * 10) * 0.1
                time.sleep(sleep_time)

                action.consumser_thread_name = self.name
                start_time = time.clock()
                re = action.action()

                end_time = time.clock()
                # 计算执行消费动作的时间
                work_sec = int(round(end_time - start_time))
                # 输出消费线程日志
                self.rl.info(("queue name %s finish,sleep time %s\'s,action time %s \'s,"
                              "action retry %s times,result:%s") % \
                             (self.name, sleep_time, work_sec, action.try_num,
                              re.__str__() if re is not None else ''))
                # 根据消费动作的结果和该消费动作的失败次数，决定是否再次放入队列中重新尝试
                if not re[0] and action.try_num < self._WORK_TRY_NUM:
                    # 该消费动作的失败次数累加
                    action.try_num += 1
                    # 再次把消费动作放到队列中，其消费动作在队列中的状态为new
                    self.queue.put(action)

                # 把得到的消费动作的状态在队列中从new转为done
                self.queue.task_done()
            except:
                self.rl.exception()
