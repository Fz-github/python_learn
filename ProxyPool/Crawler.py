import json 
from utils import get_page
from RedisHelp import RedisHelp
from pyquery import PyQuery as pq
import time

class ProxyMetaclass(type):
    def __new__(cls,name,bases,attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for key,value in attrs.items():
            if 'crawl' in key:
                attrs['__CrawlFunc__'].append(key)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls,name,bases,attrs)

class Crawler(object,metaclass = ProxyMetaclass):

    def get_proxies(self,callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            print("成功获取到代理",proxy)
            proxies.append(proxy)
        return proxies

    def crawl_daili66(self,page_count = 4):
        '''
        获取代理66
        :param page_count:页码
        ：return：代理 
        '''
        base_url = "http://www.66ip.cn/{}.html"
        urls = [base_url.format(page) for page in range(1,page_count+1)]
        for url in urls:
            print("Crawling",url)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip,port])

    def crawl_kuaidaili(self,page_count = 4):
        '''
        获取快代理
        :param page_count:页码
        :return: 代理
        ''' 
        base_url = "https://www.kuaidaili.com/free/inha/{}/"
        urls = [base_url.format(page) for page in range(1,page_count+1)]
        for url in urls:
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.table tr').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip,port])
            
            time.sleep(1)
        
    def crawl_data5u(self):
        '''
        获取无忧代理
        :return: 代理
        ''' 
        base_url = "http://www.data5u.com/free/gngn/index.shtml"
        html = get_page(base_url)
        if html:
            doc = pq(html)
            uls = doc('.wlist li:nth-child(2) ul:gt(0)').items()
            for ul in uls:
                ip = ul.find('span:nth-child(1) li').text()
                port = ul.find('span:nth-child(2) li').text()
                yield ':'.join([ip,port])


    def crawl_xicidaili(self):
        '''
        获取西刺代理
        :param page_count:页码
        :return: 代理
        ''' 
        base_url = 'http://www.xicidaili.com/wt/{}'
        urls = [base_url.format(page) for page in range(1,5)]
        for url in urls:
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('#ip_list tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(2)').text()
                    port = tr.find('td:nth-child(3)').text()
                    yield ':'.join([ip,port])


#代理池上限
POOL_UPPER_THRESHOLD = 10000 
        
class Getter():
    def __init__(self):
        '''初始化'''
        self.redis = RedisHelp()
        self.crawler = Crawler()

    def is_over_threshold(self):
        '''
        判断代理是否达到代理池上限
        '''
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        print("获取器开始执行：")
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
                for proxy in proxies:
                    self.redis.add(proxy)

getter = Getter()
getter.run()      

                    

            
                
