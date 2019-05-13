#-*- encoding: utf-8 -*-
'''
hainiu_queue.py
Created on 2018/8/31 下午3:23
Copyright (c) 2018/8/31, 海牛学院版权所有.
@author: 青牛
'''

from commons.util.log_util import LogUtil
from commons.util.db_util import DBUtil
from configs import config
import sys

def push_queue_items():
    inser_sql = """
    insert into hainiu_queue (type,params,action) values(1,%s,%s);
    """
    count_sql = """
    select count(1) from hainiu_web_seed;
    """

    select_sql = """
    select url,category from hainiu_web_seed limit %s,%s;
    
    """

    rl = LogUtil().get_base_logger()
    try:
        d = DBUtil(config._HAINIU_DB)
        sql = count_sql
        queue_total = d.read_one(sql)[0]
        print "queue_total",queue_total
        page_size = 1
        page = queue_total/page_size

        for i in range(0,page):
            sql = select_sql % (i * page_size,page_size)
            select_list = d.read_tuple(sql)
            print "page",i
            insert_list = []

            for record in select_list:
                url = record[0]
                category = record[1]
                insert_list.append((category,url))
                print url,category
            d.executemany(inser_sql,insert_list)
    except:
        rl.exception()
        rl.error(sql)
        d.rollback()
    finally:
        d.close()





if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    push_queue_items()