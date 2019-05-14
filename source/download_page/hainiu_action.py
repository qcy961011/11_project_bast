#-*- encoding: utf-8 -*-
'''
hainiu_action.py
Created on 2018/8/31 下午2:19
Copyright (c) 2018/8/31, 海牛学院版权所有.
@author: 青牛
'''


from source.commons.util import LogUtil
from source.commons.util import DBUtil
from source.commons.util import Util
from source.configs import config
from source.commons.action import ProducerAction
from source.commons.action import ConsumerAction
from source.commons.action import Producer
from source.commons.action import Consumer
import Queue,sys


queue_name = "hainiuqueue"
class HainiuProducer(ProducerAction):

    def __init__(self,limit,fail_times):
        super(self.__class__,self).__init__()
        self.limit = limit
        self.fail_times = fail_times
        self.rl = LogUtil().get_logger('producer','producer' + queue_name)


    def queue_items(self):
        '''
        从队列中取出要处理的消息，并封装成消费者动作，然后更新队列的状态
        :return:            封装好的消费者动作列表
        '''

        # 会限制本机处理失败之后就不再进行数据的获取，通过机器IP来限制
        # select_queue_sql = """
        # select id,action,params from hainiu_queue where
        # type=1 and is_work =0 and fail_times <=%s and fail_ip <> '%s'
        # limit 0,%s for update;
        # """

        select_queue_sql = """
        select id,action,params from hainiu_queue where 
        type=1 and is_work =0 and fail_times <=%s
        limit 0,%s for update;
        """

        update_queue_sql = """
        update hainiu_queue set is_work=1 where id in (%s);
        """

        return_list = []
        try:
            d = DBUtil(config._HAINIU_DB)
            sql = select_queue_sql % (self.fail_times,self.limit)
            select_dict = d.read_dict(sql)

            query_ids = []
            for record in select_dict:
                id = record['id']
                action = record['action']
                params = record['params']
                query_ids.append(str(id))
                c = HainiuConsumer(id,action,params)
                return_list.append(c)

            if query_ids:
                ids = ",".join(query_ids)
                sql = update_queue_sql % ids
                d.execute(sql)
        except:
            self.rl.exception()
            self.rl.error(sql)
            d.rollback()
        finally:
            d.close()

        return return_list



class HainiuConsumer(ConsumerAction):

    def __init__(self,id,ac,params):
        super(self.__class__, self).__init__()
        self.id = id
        self.ac = ac
        self.params = params
        self.rl = LogUtil().get_logger("consumer","consumer" + queue_name)

    def action(self):
        is_success = True
        try:
            print self.ac,self.params
            # 1/0
        except:
            is_success = False
            self.rl.exception()

        return super(self.__class__, self).result(is_success,[self.id,self.ac,self.params])

    def success_action(self,values):
        delete_sql = """
        delete from hainiu_queue where id=%s
        """
        try:
            d = DBUtil(config._HAINIU_DB)
            id = values[0]
            sql = delete_sql % id
            d.execute(sql)
        except:
            self.rl.exception()
            self.rl.error(sql)
            d.rollback()
        finally:
            d.close()

    def fail_cation(self,values):
        update_sql = """
        update hainiu_queue set fail_times=fail_times+1,fail_ip='%s' where id=%s;
        """
        update_sql_1 = """
        update hainiu_queue set is_work=0 where id=%s;
        """
        try:
            d = DBUtil(config._HAINIU_DB)
            id = values[0]
            u = Util()
            ip = u.get_local_ip()
            sql = update_sql % (ip,id)
            d.execute_no_commit(sql)
            if(self.try_num == Consumer._WORK_TRY_NUM):
                sql = update_sql_1 % id
                d.execute_no_commit(sql)
            d.commit()
        except:
            self.rl.exception()
            self.rl.error(sql)
        finally:
            d.close()

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    #初始化使用的队列
    q = Queue.Queue()
    #初始化生产者动作
    pp = HainiuProducer(20,6)
    #初始化生产者
    p = Producer(q,pp,queue_name,10,2,2,3)
    #启动整个生产和消费任务
    p.start_work()