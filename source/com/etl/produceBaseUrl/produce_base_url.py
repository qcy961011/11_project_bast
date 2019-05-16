# -*- coding: utf-8 -*-
"""
produce_base_url.py
Created on 2019/5/15 20:37
Copyright 2019/5/15
@author: qcy
"""
from com.frame.commen import base_producer_action
from com.frame.commen import base_consumer_action
from com.frame.commen import queue_producer
from com.frame.util.log_util import LogUtil
from queue import Queue
from com.frame.configs import configs
from com.frame.util.db_util import DBUtil

class produceBaseUrlAction(base_consumer_action.ConsumerAction):
    def __init__(self, text):
        """
        初始化消费者实现类
        :param text:
        """
        super(self.__class__, self).__init__()
        self.text = text
        self.rl = LogUtil().get_base_logger()

    def action(self):
        pass

    def success_action(self, values):
        pass

    def fail_cation(self, values):
        pass


class produceBaseUrlProduce(base_producer_action.ProducerAction):


    def queue_items(self):
        get_seed_sql = "select * from qcy_web_seed where status = 0 limit 1"
        db = DBUtil(configs._DB_CONFIG)
        d = db.read_dict(get_seed_sql)
        update_seed_status = "update qcy_web_seed set status = 1 where id = %s"
        db.executemany_no_commit(update_seed_status, [(d[0]["id"])])
        db.commit()
        pass

    def get_page_href(self, url):

        pass

if __name__ == "__main__":
    # 初始化使用的队列
    q = Queue()
    # 初始化生产者动作
    pp = produceBaseUrlProduce()
    # 初始化生产者
    p = queue_producer.Producer(q, pp, configs._BASE_URL_PRODUCE_NAME , configs._BASE_URL_MAX_NUMBER, configs._BASE_URL_SLEEP_TIME, configs._BASE_URL_WORK_SLEEP_TIME, configs._BASE_URL_WORK_TRY_NUMBER)
    # 启动整个生产和消费任务
    p.start_work()
