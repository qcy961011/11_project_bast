# -*- coding: utf-8 -*-
"""
produce_base_url.py
Created on 2019/5/15 20:37
Copyright 2019/5/15
@author: qcy
"""
import re

from bs4 import BeautifulSoup

from com.frame.commen import base_producer_action
from com.frame.commen import base_consumer_action
from com.frame.commen import queue_producer
from com.frame.util.log_util import LogUtil
from queue import Queue
from com.frame.configs import configs
from com.frame.util.db_util import DBUtil
from com.frame.util.request_util import RequestUtil
from com.frame.util.html_util import HtmlUtil
from urllib.parse import urlparse
from tld import get_tld


class produceBaseUrlAction(base_consumer_action.ConsumerAction):
    def __init__(self, url , domain):
        """
        初始化消费者实现类
        :param text:
        """
        super(self.__class__, self).__init__()
        self.url = url
        self.domain = domain
        self.rl = LogUtil().get_base_logger()


    def action(self):
        result = True
        r_test = self.url
        url = self.url
        r = RequestUtil()
        hu = HtmlUtil()
        html = r.http_get_phandomjs(url)
        # print(html)
        soup = BeautifulSoup(html, 'lxml')
        title_doc = soup.find_all("title")

        try:
            if str(self.url).find(self.domain) != -1:
                r_test = '内链'
            else:
                r_test = '外链'
        except:
            result = False
            self.rl.exception()

        return self.result(result, [r_test])

    def success_action(self, values):
        pass

    def fail_cation(self, values):
        pass


class produceBaseUrlProduce(base_producer_action.ProducerAction):

    _regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def get_page_href(url=None):
        r = RequestUtil()
        hu = HtmlUtil()
        html = r.http_get_phandomjs(url)
        o = urlparse(url)
        soup = BeautifulSoup(html)
        a_docs = soup.find_all("a")
        host = hu.get_url_host(url)
        a_list = []
        for a in a_docs:
            # 获取a标签的href
            a_href = r.get_format_url(url, a, host)
            if a_href.find("./") != -1:
                a_list.append(a_href)
            elif produceBaseUrlProduce._regex.search(a_href):
                a_list.append(a_href)
        return a_list

    def get_domain(url=None):
        domain = get_tld(url)
        return domain

    def queue_items(self):
        get_seed_sql = "select * from qcy_web_seed where status = 0 limit 1"
        db = DBUtil(configs._DB_CONFIG)
        d = db.read_dict(get_seed_sql)
        update_seed_status = "update qcy_web_seed set status = 1 where id = %s"
        db.executemany_no_commit(update_seed_status, [(d[0]["id"])])
        db.commit()
        try:
            a_list = produceBaseUrlProduce.get_page_href(url=d[0]["url"])
            domain = produceBaseUrlProduce.get_domain(url=d[0]["url"])
            _items_list = []
            for a in a_list:
                web_queue_insert_sql = "insert into qcy_web_queue (type,action,params)  values(1, %s , %s)"
                _items_list.append(produceBaseUrlAction(a, domain))
                n = db.executemany(web_queue_insert_sql, [(a, 'test')])
        except:
            update_seed_status = "update qcy_web_seed set status = 0 where id = %s"
            db.executemany(update_seed_status, [(d[0]["id"])])
        finally:
            db.close()
        return _items_list


if __name__ == "__main__":
    # 初始化使用的队列
    q = Queue()
    # 初始化生产者动作
    pp = produceBaseUrlProduce()
    # 初始化生产者
    p = queue_producer.Producer(q, pp, configs._BASE_URL_PRODUCE_NAME, configs._BASE_URL_MAX_NUMBER,
                                configs._BASE_URL_SLEEP_TIME, configs._BASE_URL_WORK_SLEEP_TIME,
                                configs._BASE_URL_WORK_TRY_NUMBER)
    # 启动整个生产和消费任务
    p.start_work()
