# -*- coding: utf-8 -*-
"""
RedisTest.py
Created on 2019/5/17 16:17
Copyright 2019/5/17
@author: qcy
"""
from rediscluster import StrictRedisCluster
import redis

def create_conn():
    redis_nodes = [{'host': '192.168.31.94', 'port': 6379}]
    redisconn = redis.Redis(host='localhost' , port='6379' , decode_responses=True)
    redisconn.set("qiao" , "123")
    print(redisconn.get("qiao"))


if __name__ == '__main__':
    create_conn()