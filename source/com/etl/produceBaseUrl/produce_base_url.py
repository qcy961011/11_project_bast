"""
produce_base_url.py
Created on 2019/5/15 20:37
Copyright 2019/5/15
@author: qcy
"""
import re
import queue
import pymysql

from bs4 import BeautifulSoup

from com.frame.commen import base_producer_action
from com.frame.commen import base_consumer_action
from com.frame.commen import queue_producer
from com.frame.util.log_util import LogUtil
from com.frame.util.util import Util

from com.frame.configs import configs
from com.frame.util.db_util import DBUtil
from com.frame.util.request_util import RequestUtil
from com.frame.util.html_util import HtmlUtil
from urllib.parse import urlparse
import tld
from com.frame.util.time_util import TimeUtil


class produceBaseUrlAction(base_consumer_action.ConsumerAction):
    def __init__(self, url, domain):
        """
        初始化消费者实现类
        :param text:
        """
        super(self.__class__, self).__init__()
        self.url = url
        self.domain = domain
        self.rl = LogUtil().get_logger("ConsumerAction", "ConsumerAction")

    def action(self):
        result = True
        try:
            r_test = self.url
            url = self.url
            r = RequestUtil()
            hu = HtmlUtil()
            t = TimeUtil()
            u = Util()
            ip = u.get_local_ip()
            md5 = u.get_md5(url)
            host = hu.get_url_host(url)
            htmlm877 = r.http_get_phandomjs(url)
            data = htmlm877.replace('\r', '').replace('\n', '').replace('\t', '')
            # print(html)
            list = []
            a_set = set()
            soup = BeautifulSoup(data, 'lxml')
            a_docs = soup.find_all("a")
            for a in a_docs:
                a_href = RequestUtil.get_format_url(self, url, a, host)
                a_title = a.get_text().strip()
                if a_href == '' or a_title == '':
                    continue
                if a_set.__contains__(a_href):
                    continue
                a_set.add(a_href)
                a_url = a_href
                parsed_uri = urlparse(url)
                a_host = '{uri.netloc}'.format(uri=parsed_uri)
                a_md5 = u.get_md5(a_href)
                a_xpath = hu.get_dom_parent_xpath_js(a)
                list.append(a_href)
                # title_doc = soup.find_all("title")
                update_time = int(t.str2timestamp(t.now_time()))
                create_time = update_time
                create_day = t.now_day(format='%Y%m%d')
                create_hour = t.now_hour()
                status = 0
                param = '资讯'
                inner_talbe = "qcy_web_seed_internally"
                exter_table = "qcy_web_seed_externally"
                # 分类插入到不同的表，根据domain来划分
                insert_sql = """
                         insert into <table> (url,md5,domain,host,a_md5,a_host,a_xpath,create_time,a_title, a_url,
                        create_day, create_hour,update_time,status,param) 
                        values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s",%s,%s,%s,%s,"%s") on DUPLICATE KEY UPDATE update_time={},fail_times=fail_times+1
                               """.format(update_time)
                # print(url, md5, self.domain, host, a_md5, a_host, a_xpath, create_time,
                #                  pymysql.escape_string(a_title),
                #                  pymysql.escape_string(a_url),
                #                  create_day, create_hour, update_time, status)
                insert_values = (url, md5, self.domain, host, a_md5, a_host, a_xpath, create_time,
                                 pymysql.escape_string(a_title),
                                 pymysql.escape_string(a_url),
                                 create_day, create_hour, update_time, status, param)
                print(insert_sql % (url, md5, self.domain, host, a_md5, a_host, a_xpath, create_time,
                                    pymysql.escape_string(a_title),
                                    pymysql.escape_string(a_url),
                                    create_day, create_hour, update_time, status, param))
                try:
                    d = DBUtil(configs._DB_CONFIG)
                    if a_host.__contains__(self.domain):
                        r_test = insert_sql.replace('<table>', inner_talbe)
                        d.execute(r_test, value=insert_values)
                        # print("插入内链表")
                    else:
                        r_test = insert_sql.replace('<table>', exter_table)
                        d.execute(r_test, value=insert_values)
                        # print("插入外链表")
                except:
                    result = False
                    self.rl.exception()
                finally:
                    d.close()
                    r.close_phandomjs()
        except:
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

    # def get_page_href(url=None):
    #     r = RequestUtil()
    #     hu = HtmlUtil()
    #     html = r.http_get_phandomjs(url)
    #     # o = urlparse(url)
    #     soup = BeautifulSoup(html)
    #     a_docs = soup.find_all("a")
    #     host = hu.get_url_host(url)
    #     a_list = []
    #     for a in a_docs:
    #         # 获取a标签的href
    #         a_href = r.get_format_url(url, a, host)
    #         if a_href.find("./") != -1:
    #             a_list.append(a_href)
    #         elif produceBaseUrlProduce._regex.search(a_href):
    #             a_list.append(a_href)
    #     return a_list

    def get_domain(url=None):
        domain = tld.get_fld(url)
        return domain

    def queue_items(self):
        get_seed_sql = "select * from qcy_web_seed where status = 0 limit 1"
        db = DBUtil(configs._DB_CONFIG)
        d = db.read_dict(get_seed_sql)
        url_list = d[0]["url"]
        update_seed_status = "update qcy_web_seed set status = 1 where id = %s"
        db.executemany_no_commit(update_seed_status, [(d[0]["id"])])

        db.commit()
        _items_list = []
        try:
            # a_list = produceBaseUrlProduce.get_page_href(url=d[0]["url"])
            domain = produceBaseUrlProduce.get_domain(url=d[0]["url"])
            web_queue_insert_sql = "insert into qcy_web_queue (type,action,params)  values(1, %s , %s)"
            _items_list.append(produceBaseUrlAction(url_list, domain))
            db.executemany(web_queue_insert_sql, [(url_list, 'test')])
            # for a in a_list:
            #     web_queue_insert_sql = "insert into qcy_web_queue (type,action,params)  values(1, %s , %s)"
            #     _items_list.append(produceBaseUrlAction(a, domain))
            #     db.executemany(web_queue_insert_sql, [(a, 'test')])
        except:
            update_seed_status = "update qcy_web_seed set status = 0 where id = %s"
            db.executemany(update_seed_status, [(d[0]["id"])])
        finally:
            db.close()
        return _items_list


if __name__ == "__main__":
    # 初始化使用的队列
    q = queue.Queue()
    # 初始化生产者动作
    pp = produceBaseUrlProduce()
    # 初始化生产者
    p = queue_producer.Producer(q, pp, configs._BASE_URL_PRODUCE_NAME, configs._BASE_URL_MAX_NUMBER,
                                configs._BASE_URL_SLEEP_TIME, configs._BASE_URL_WORK_SLEEP_TIME,
                                configs._BASE_URL_WORK_TRY_NUMBER)
    # 启动整个生产和消费任务
    p.start_work()
