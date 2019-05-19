# -*- encoding: utf-8 -*-
'''
redis_utill.py
Created on 2017/6/30 16:06
Copyright (c) 2017/6/30, 海牛学院版权所有.
@author: 青牛
'''

# from redis.connection import (ConnectionPool, UnixDomainSocketConnection,SSLConnection, Token)
import json
import sys
import threading

import redis


class RedisUtill(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        """
        单例模式
        """
        if not hasattr(RedisUtill, "_instance"):
            with RedisUtill._instance_lock:
                if not hasattr(RedisUtill, "_instance"):
                    RedisUtill._instance = object.__new__(cls)

        return RedisUtill._instance

    def creat_conn(self):
        redis_nodes = [{'host': 'nn1.hadoop', 'port': 6379},
                       {'host': 'nn2.hadoop', 'port': 6379},
                       {'host': 's1.hadoop', 'port': 6379},
                       {'host': 's2.hadoop', 'port': 6379},
                       {'host': 's3.hadoop', 'port': 6379},
                       {'host': 's4.hadoop', 'port': 6379}]
        # redis_nodes = [{'host': '127.0.0.1', 'port': 6379}]
        try:
            redisconn = StrictRedisCluster(startup_nodes=redis_nodes)
            # redisconn = redis.Redis(host='localhost', port='6379', decode_responses=True)
        except Exception:
            print("Connect Error!")
            sys.exit(1)

        self.redisconn = redisconn
        return redisconn

    def get_conn(self):
        '''
        获取 redis 集群链接

        如果之前链接无效从新链接  --- 防止频繁 重新链接集群
        :return:    创建的链接
        '''
        if not hasattr(self, "redisconn"):
            RedisUtill.redisconn = self.creat_conn()
            self.redisconn = RedisUtill.redisconn
        return self.redisconn

    def keys_limit_scan(self, pattern='*', limit=1, cursor=0):
        '''
        批量获取 keys
        '''
        limit_keys_obj = self.get_conn().scan(cursor, pattern, limit)
        limit_keys_list = []
        for key, value in limit_keys_obj.items():
            for i in value[1]:
                limit_keys_list.append(i)

        return limit_keys_list

    def get_values_batch_keys(self, keys):
        '''
        通过 keys 批量获取值values  --列表 []
        '''
        return self.get_conn().mget(keys)

    def get_value_for_key(self, key):
        '''
        通过 key  获取值   单个
        '''
        return self.get_conn().get(key)

    def set_data(self, key, value):
        '''
        保存单个值
        '''
        return self.get_conn().set(key, value)

    def set_batch_datas(self, keydicts):
        '''
        批量保存  c传入字典 {key:value,key2:value2}
        '''
        return self.get_conn().mset(keydicts)


    def delete_data(self, key):
        '''
        删除
        '''
        return self.get_conn().delete(key)

    def delete_batch(self, keys):
        '''
        批量删除   --- redis 的郁闷到奔溃  传，key 的列表  []
        '''
        for i in keys:
            self.get_conn().delete(i)

    def rename_key(self, src, dst_new):
        '''
        重命名 key
        '''
        return self.get_conn().rename(src, dst_new)

    def get_all_key_value(self):
        '''
        获取所用的数据  打印信息
        '''
        keys = self.get_conn().keys()
        for i in keys:
            print(i, ':', self.get_conn().get(i))


if __name__ == '__main__':
    # reload(sys)
    # sys.setdefaultencoding('utf-8')

    g = RedisUtill()
    dicts = {'key1': 11, 'key2': 22, 'key3': 'aaa'}
    s = g.set_batch_datas(dicts)
    print (s)
    list = ['key1', 'key2', 'key3']
    dd = g.get_values_batch_keys(list)
    print (dd)

    # 解决中文乱码问题
    g = RedisUtill()
    # 重命名
    sss = g.rename_key('key3', 'key4')
    print (g.get_value_for_key('key4'), sss)

    list = ['wo', 'shi', '大家', '中文']
    result = json.dumps(list, encoding='UTF-8', ensure_ascii=False)
    g.set_data('testxiugai',result)

    std = g.get_value_for_key('testxiugai')
    ddddd = json.loads(std)
    ddddd[1] = '修改成中文'
    result = json.dumps(ddddd, encoding='UTF-8', ensure_ascii=False)
    g.set_data('testxiugai', result)
    std2 = g.get_value_for_key('testxiugai')
    ddddd2 = json.loads(std2)
    for i in ddddd2:
        print (i)

    g.set_data('hainiu:key1', 123)
    g.set_data('hainiu:key2', 33)
    dlist = ['hainiu:key1', 'hainiu:key2']
    print (g.get_values_batch_keys(dlist))
    list = ('key1', 'key2', 'key3')

    dd = g.get_values_batch_keys(list)
    g.delete_batch(list)
    dd2 = g.get_values_batch_keys(list)
    print (dd)
    print (dd2)

    # 清理数据
    g = RedisUtill()
    dd = g.get_conn().keys('*')
    s = g.delete_batch(dd)
    jj = g.get_conn().keys('*')
    print (dd)
    print (s)
    print (jj)

    obj1 = RedisUtill()

    obj1.get_conn()
    obj2 = RedisUtill()
    obj2.get_conn()
    print(obj1,obj2)

    #测试是否为单例
    def task(arg):
        obj = RedisUtill()
        print(obj)

    for i in range(10):
        t = threading.Thread(target=task,args=[i,])
        t.start()
