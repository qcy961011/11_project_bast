# -*- coding: utf-8 -*-
"""
config_util.py
Created on 2019/5/15 21:21
Copyright 2019/5/15
@author: qcy
"""
import io
import sys

from com.frame.configs import configs
import pymysql


class DBUtil:
    def __init__(self, config):
        self.db = pymysql.connect(host=config['HOST'], user=config['USER'], passwd=config['PASSWD'],
                                  db=config['DB'], charset=config['CHARSET'], port=config['PORT'])

    def execute(self, sql):
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        self.cursor.execute(sql)
        self.db.commit()

    def read_dict(self, sql):
        """execute sql return dict
        select a,b,c from table
        ({a:1,b:2,c:33},{a:1,b:3,c:45})
        """
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def commit(self):
        self.db.commit()

    def close(self):
        """close db connect
        """
        self.cursor = self.db.cursor()
        self.cursor.close()
        self.db.close()

    def executemany_no_commit(self, sql, values):
        self.cursor = self.db.cursor()
        self.cursor.executemany(sql, values)

    def executemany(self, sql, values):
        self.cursor = self.db.cursor()
        self.cursor.executemany(sql, values)
        self.db.commit()

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
    db = DBUtil(configs._DB_CONFIG)
    sql = """
    insert into hainiu_queue
        (type,action,params,fail_ip,create_times)
        values (1,"10153108084201229","Baltimore Ravens","Sports Team","2015-08-04 21:35:40");
    """
    for i in range(0, 10):
        db.execute(sql)

    d = db.read_dict("select count(1) as n from hainiu_queue")
    print(d)
    db.close()
