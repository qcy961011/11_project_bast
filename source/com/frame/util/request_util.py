# -*- encoding: utf-8 -*-
'''
Created on 2017/7/1 13:49
Copyright (c) 2017/7/1, 海牛学院版权所有.
@author: 青牛
'''
import io
import sys
import threading
import urllib.request
from http import cookiejar
from urllib import parse
from urllib.parse import urlparse
from tld import get_tld

from selenium.webdriver import PhantomJS
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class RequestUtil:
    __browserAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'

    def __init__(self):
        self.cookies = ''
        self._lock = threading.RLock()

    def http_get_request(self, url, referer, timeout=''):
        self._lock.acquire()
        cookie = cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie), SmartRedirectHandler())
        urllib.request.install_opener(opener)
        headers = {'User-Agent': self.__browserAgent,
                   'Referer': referer,
                   'Cache-Control': 'max-age=0',
                   'Accept': '*/*',
                   'Connection': 'Keep-Alive',
                   'Accept-encoding': 'gzip'}
        req = urllib.request.Request(url=url, headers=headers)
        if timeout == '':
            open = urllib.request.urlopen(req)
        else:
            open = urllib.request.urlopen(req, timeout=timeout)
        if self.cookies == '':
            for item in cookie:
                self.cookies = self.cookies + item.name + '=' + item.value + ';'
            self.cookies = self.cookies[:-1]
        if url != open.url:
            req = urllib.request.Request(url=open.url, headers=headers)
        self._lock.release()
        return (open, req)

    def http_post_request(self, url, datas, referer, timeout=''):
        self._lock.acquire()
        postdata = urllib.parse.urlencode(datas)
        headers = {'User-Agent': self.__browserAgent,
                   'Referer': referer,
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Cache-Control': 'no-cache',
                   'Accept': '*/*',
                   'Connection': 'Keep-Alive',
                   'Accept-encoding': 'gzip',
                   'Cookie': self.cookies}
        req = urllib.request.Request(url=url, data=postdata, headers=headers)
        req.get_host()
        if timeout == '':
            open = urllib.request.urlopen(req)
        else:
            open = urllib.request.urlopen(req, timeout=timeout)
        if url != open.url:
            req = urllib.request.Request(url=open.url, headers=headers)
        self._lock.release()
        return (open, req)

    def http_get(self, url, refer='https://www.baidu.com'):
        return self.http_get_request(url, refer, 60)

    def http_post(self, url, datas, refer='https://www.baidu.com'):
        return self.http_post_request(url, datas, refer, 60)

    def http_post_request2(self, url, datas, timeout=''):
        if timeout == '':
            open = urllib.request.urlopen(url, datas)
        else:
            open = urllib.request.urlopen(url, datas, timeout=timeout)
        data = open.read()
        return data

    def http_post2(self, url, datas):
        return self.http_post_request2(url, datas, 300)

    def create_phandomjs(self, service_args, caps, timeout=30):

        self.driver = PhantomJS(desired_capabilities=caps, service_args=service_args,executable_path=r'D:\tool\phantomjs-2.1.1-windows\bin\phantomjs.exe')
        self.driver.set_page_load_timeout(timeout)
        self.driver.set_script_timeout(timeout)
        self.driver.implicitly_wait(timeout)

    def close_phandomjs(self):
        try:
            self.driver.quit()
        except:
            pass

    def http_get_phandomjs(self, url, refer='https://www.baidu.com', timeout=1000):
        caps = dict(DesiredCapabilities.PHANTOMJS)
        caps['browserName'] = 'chrome'
        caps["phantomjs.page.settings.resourceTimeout"] = timeout
        caps["phantomjs.page.settings.loadImages"] = False
        caps["phantomjs.page.settings.userAgent"] = (self.__browserAgent)
        caps["phantomjs.page.customHeaders.Referer"] = (refer)

        service_args = []
        service_args.append('--load-images=no')
        service_args.append('--disk-cache=yes')
        service_args.append('--cookies-file=')

        self.create_phandomjs(timeout=timeout, service_args=service_args, caps=caps)
        self.driver.get(url)
        # self.driver.save_screenshot('hainiu.png')
        return self.driver.page_source

    def get_format_url(self, url: object, a_doc: object, host: object) -> object:
        a_href = a_doc.get('href')
        try:
            if a_href is not None and a_href.__len__() > 0:
                a_href = str(a_href).strip()
                a_href = a_href[:a_href.index('#')] if a_href.__contains__('#') else a_href
                # a_href = a_href.encode('utf8')
                # a_href = urllib.quote(a_href,safe='.:/?&=')
                if a_href.startswith('//'):
                    url = 'https:' + a_href if url.startswith('https:') else 'http:' + a_href
                    url = urlparse(str(url))
                    a_href = url.url
                elif a_href.startswith('/'):
                    url = 'https://' + host + a_href if url.startswith('https:') else 'http://' + host + a_href
                    url = urlparse(str(url))
                    a_href = url.url
                elif a_href.startswith('./') or a_href.startswith('../'):
                    url = urlparse(str(url) + '/' + a_href)
                    a_href = url.url
                elif not a_href.startswith('javascript') and not a_href.startswith('mailto') and not a_href.startswith(
                        'http') and a_href != '':
                    url = 'https://' + host + '/' + a_href if url.startswith('https:') else 'http://' + host + '/' + a_href
                    url = urlparse(str(url))
                    a_href = url.url
                a_href = a_href[:-1] if a_href.endswith('/') else a_href
                # a_href = a_href.lower()
            get_tld(a_href)
        except:
            return ''

        if not a_href.startswith('http'):
            return ''

        if a_href.__contains__('?'):
            a_params_str = a_href[a_href.index('?') + 1:]
            a_params = a_params_str.split('&')
            a_params.sort()
            a_params_str = '&'.join(a_params)
            a_href = a_href[:a_href.index('?') + 1] + a_params_str

        return a_href

class SmartRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib.request.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        result.status = code
        return result


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
    r = RequestUtil()
    html = r.http_get_phandomjs('http://mil.news.sina.com.cn/china/2017-06-30/doc-ifyhrxsk1462288.shtml')
    html = html.decode('utf-8').encode(sys.getfilesystemencoding())
    print(html)
    r.close_phandomjs()
