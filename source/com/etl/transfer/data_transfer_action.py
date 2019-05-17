'''  将内链表的数据从mysql中拿取放入redis中
data_transfer_action.py
Created on 2019/5/16 20:09
Copyright (c) 2019/5/16
@author: hly
'''
from source.com.frame.commen.base_producer_action import ProducerAction
from source.com.frame.commen.base_consumer_action import ConsumerAction
from source.com.frame.commen.queue_producer import Producer
from source.com.frame.util.log_util import LogUtil
from source.com.frame.util.redis_utill import RedisUtill
from source.com.frame.util.db_util import DBUtil
from source.com.frame.util.util import Util
from source.com.frame.configs import configs
import sys
import io
import queue

queue_name = "transfer"


class DateTransferProduce(ProducerAction):
    def __init__(self, limit, fail_times):
        super(self.__class__, self).__init__()
        self.limit = limit
        self.fail_times = fail_times
        self.rl = LogUtil().get_logger('DateTransferProduce', 'DateTransferProduce')

    def queue_items(self):
        select_internally_sql = """
            select a_url,a_md5,a_title from hainiu_web_seed_internally
        """
        list = []
        try:
            d = DBUtil(configs._DB_CONFIG)
            sql = select_internally_sql
            select_dict = d.read_dict(sql)
            for record in select_dict:
                a_url = record['a_url']
                a_md5 = record['a_md5']
                a_title = record['a_title']
                c = DateTransferConsumer(a_md5, a_url, a_title)
                list.append(c)
        except:
            d.rollback()
            d.commit()
        finally:
            d.close()
        return list


class DateTransferConsumer(ConsumerAction):
    def __init__(self, a_url, a_md5, a_title):
        ConsumerAction.__init__(self)
        self.a_url = a_url
        self.a_md5 = a_md5
        self.a_title = a_title
        self.rl = LogUtil().get_logger('DateTransferConsumer', 'DateTransferConsumer')

    def action(self):
        redis_dict_values = {}
        redis_dict_keys = []
        u = Util()
        a_url = ''
        redis_util = RedisUtill()

        dict_exit_key = "exist : %s" % self.a_md5
        redis_dict_values[dict_exit_key] = a_url
        redis_dict_keys.append(dict_exit_key)
        # 拿key去redis查是否存在  exist:a_md5,得到这些key对应的values，也就是url列表
        redis_exist_values = redis_util.get_values_batch_keys(redis_dict_keys)
        # 将存在的values列表转换成exist:md5形式
        redis_exist_keys = ["exist:%s" % u.get_md5(rev) for rev in redis_exist_values if rev != None]
        redis_dict_down_values = {}
        for key, value in redis_dict_values.items():
            if key not in redis_exist_keys:
                redis_dict_down_values["down:%s" % u.get_md5(value)] = value
                redis_dict_down_values[key] = value

        if redis_dict_down_values.__len__() != 0:
            redis_util.set_batch_datas(redis_dict_down_values)


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
    q = queue.Queue()
    pp = DateTransferProduce(20, 6)
    p = Producer(q, pp, queue_name, 10, 2, 2, 3)
    p.start_work()
