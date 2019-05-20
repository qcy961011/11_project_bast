'''  将内链表的数据从mysql中拿取放入redis中
data_transfer_action.py
Created on 2019/5/16 20:09
Copyright (c) 2019/5/16
@author: hly
'''
import io
import queue
import sys
import traceback

from bs4 import BeautifulSoup
from tld import get_tld
from urllib.parse import urlparse

from com.frame.commen.base_consumer_action import ConsumerAction
from com.frame.commen.base_producer_action import ProducerAction
from com.frame.commen import queue_producer
from com.frame.configs import configs
from com.frame.util.db_util import DBUtil
from com.frame.util.html_util import HtmlUtil
from com.frame.util.log_util import LogUtil
from com.frame.util.redis_utill import RedisUtill
from com.frame.util.request_util import RequestUtil
from com.frame.util.util import Util
from com.frame.util.time_util import TimeUtil

queue_name = "transfer"


class DateTransferProduce(ProducerAction):
    _limit_count = 0

    def __init__(self, limit, fail_times):
        super(self.__class__, self).__init__()
        self.limit = limit
        self.fail_times = fail_times
        self.rl = LogUtil().get_logger('DateTransferProduce', 'DateTransferProduce')

    def queue_items(self):
        select_internally_sql = """
            select a_url,a_md5,a_title from qcy_web_seed_internally where status = 0 limit %s,%s
        """
        list = []
        redisConn = RedisUtill().creat_conn()
        u = Util()
        try:
            d = DBUtil(configs._DB_CONFIG)
            sql = select_internally_sql
            select_dict = d.read_dict_parma(sql, [DateTransferProduce._limit_count * self.limit, self.limit])
            for record in select_dict:
                a_url = record['a_url']
                md5 = u.get_md5(str(a_url))
                if redisConn.get('key:' + md5) is None:
                    redisConn.set('key:' + md5, a_url)
                    redisConn.set('down:' + md5, a_url)
                    # redisConn.set("count:" + md5, 1)
                    c = DateTransferConsumer(a_url)
                    list.append(c)
                else:
                    continue
            DateTransferProduce._limit_count = DateTransferProduce._limit_count + 1
        except:
            d.rollback()
            d.commit()
        finally:
            d.close()
        return list


class DateTransferConsumer(ConsumerAction):
    def __init__(self, a_url):
        ConsumerAction.__init__(self)
        self.a_url = a_url
        self.rl = LogUtil().get_logger('DateTransferConsumer', 'DateTransferConsumer')

    def get_domain(url=None):
        domain = get_tld(url)
        return domain

    def action(self):
        redisConn = RedisUtill().creat_conn()
        u = Util()
        result = True
        hu = HtmlUtil()
        r = RequestUtil()
        db = DBUtil(configs._DB_CONFIG)
        time = TimeUtil()
        try:
            md5 = u.get_md5(str(self.a_url))
            url = redisConn.get("down:" + md5)
            print(url)
            redisConn.delete("down:" + md5)
            if url is not None:
                print(url)
                html = r.http_get_phandomjs(url)
                soup = BeautifulSoup(html, 'lxml')
                title_doc = soup.find("title") if soup.find("title") != None else ""
                domain = DateTransferConsumer.get_domain(url)
                parsed_uri = urlparse(url)
                host = '{uri.netloc}'.format(uri=parsed_uri)
                data = html.replace('\r', '').replace('\n', '').replace('\t', '')
                insert_web_page_sql = """
                    insert into qcy_web_page (url,md5,create_time,create_day,create_hour,domain,param,update_time,host,
                    title,fail_ip,status) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    on DUPLICATE KEY UPDATE fail_times=fail_times+1,fail_ip=values(fail_ip);
                """
                now_time = time.str2timestamp(time.now_time())
                now_day = time.now_day(format='%Y%m%d')
                now_hour = time.now_hour()
                ip = u.get_local_ip()
                db.execute(insert_web_page_sql, (
                    url,
                    md5,
                    now_time,
                    now_day,
                    now_hour,
                    domain,
                    data,
                    now_day,
                    host,
                    str(title_doc),
                    ip,
                    1))
        except Exception as e:
            traceback.print_exc()
            redisConn.set("down:" + md5, url)
            result = False

        finally:
            pass
        return self.result(result, self.a_url)

    def success_action(self, values):
        pass

    def fail_cation(self, values):
        pass


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
    q = queue.Queue()
    pp = DateTransferProduce(1, 1)
    p = queue_producer.Producer(q, pp, configs._BASE_URL_PRODUCE_NAME, configs._BASE_URL_MAX_NUMBER,
                                configs._BASE_URL_SLEEP_TIME, configs._BASE_URL_WORK_SLEEP_TIME,
                                configs._BASE_URL_WORK_TRY_NUMBER)
    p.start_work()
