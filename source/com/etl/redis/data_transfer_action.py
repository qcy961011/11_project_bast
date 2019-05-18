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
from com.frame.commen.queue_producer import Producer
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
    def __init__(self, limit, fail_times):
        super(self.__class__, self).__init__()
        self.limit = limit
        self.fail_times = fail_times
        self.rl = LogUtil().get_logger('DateTransferProduce', 'DateTransferProduce')

    def queue_items(self):
        select_internally_sql = """
            select a_url,a_md5,a_title from hainiu_web_seed_internally where status = 0 limit %s
        """
        list = []
        redisConn = RedisUtill().creat_conn()
        u = Util()
        try:
            d = DBUtil(configs._DB_CONFIG)
            sql = select_internally_sql
            select_dict = d.read_dict_parma(sql, [self.limit])
            for record in select_dict:
                a_url = record['a_url']
                md5 = u.get_md5(str(a_url).encode('utf-8'))
                if redisConn.get('key:' + md5) is None:
                    redisConn.set('key:' + md5, a_url)
                    redisConn.set('down:' + md5, a_url)
                    # redisConn.set("count:" + md5, 1)
                    c = DateTransferConsumer(a_url)
                    list.append(c)
                else:
                    continue
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
            md5 = u.get_md5(str(self.a_url).encode('utf-8'))
            url = redisConn.get("down:" + md5)
            if url is not None:
                html = r.http_get_phandomjs(url)
                soup = BeautifulSoup(html, 'lxml')
                title_doc = soup.find_all("title")
                domain = DateTransferConsumer.get_domain(url)
                parsed_uri = urlparse(url)
                host = '{uri.netloc}'.format(uri=parsed_uri)
                data = html.replace('\r', '').replace('\n', '').replace('\t', '')
                insert_web_page_sql = """
                    insert into qcy_hainiu_web_page (url,md5,create_time,create_day,create_hour,domain,param,update_time,host,
                    title,fail_ip,status) values ("%s","%s",%s,%s,%s,"%s","%s",%s,"%s","%s","%s",%s)
                    on DUPLICATE KEY UPDATE fail_times=fail_times+1,fail_ip=values(fail_ip);
                """
                db.execute(insert_web_page_sql, value=(
                url, md5, time.str2timestamp(time.now_time()), time.now_day(format='%Y%m%d'), time.now_hour(), domain,
                data, time.str2timestamp(time.now_time()),
                host, title_doc, u.get_local_ip(), 1))
        except Exception as e:
            traceback.print_exc()
            result = False
        finally:
            pass
        return self.result(result, self.a_url)



if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
    q = queue.Queue()
    pp = DateTransferProduce(20, 6)
    p = Producer(q, pp, queue_name, 10, 2, 2, 3)
    p.start_work()
