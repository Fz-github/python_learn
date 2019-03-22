from requests import Session
from setting import *
from redisqueue import RedisQueue
from mysql import MySQL
from request import WechatRequest
from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq 
from requests import ReadTimeout,ConnectionError

class Spider():

    base_url = 'https://weixin.sogou.com/weixin'

    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9",
        'Connection': "keep-alive",
        #'Cookie': "SUV=00562B8C716BA3C55B7CC61EC47BF699; IPLOC=CN4409; SUID=2FC240714F18910A000000005C56AB35; LSTMV=660%2C763; LCLKINT=15780; ABTEST=6|1551706158|v1; SNUID=6FEC6D5C2C28AE4D9E6D0A0B2DCEB6ED; weixinIndexVisited=1; ppinf=5|1551925959|1553135559|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxMTpGeiVFOSU5MiU4QXxjcnQ6MTA6MTU1MTkyNTk1OXxyZWZuaWNrOjExOkZ6JUU5JTkyJThBfHVzZXJpZDo0NDpvOXQybHVMelMwNlJDd21tV09nX21LZ1d2blZRQHdlaXhpbi5zb2h1LmNvbXw; pprdig=tEYSbQNdMLiJ4_U8ItrJe8DDerrSK-6LmPazScIYQjimbIM6vnHQTzITlaGOkYT_yZjXNmSD296WaS8o0hJHupmDO4DsEcPc03J8plg5omvRYGih96qypuqNYvLbarzbDFiTzPR4Jjb_--D230l9iLlg4ci-TevfpGlXt7XwoY8; sgid=22-39570427-AVyAgsemAFa1A4kW57WnCd0; ppmdig=155195247300000013eb86436418439cbc817a32caf385f4; sct=17; JSESSIONID=aaaVHQpkEIMGZ55MMJZKw",
        'Cookie':"SUV=00A2174B68EE87F85A759F794AB15945; SUID=C5A36B71462B8B0A5AC244F7000C0119; wuid=AAHqV3s9HwAAAAqLK0aU3gYAGwY=; CXID=92BEB38BD51275423AE8BECD7B2A1BA0; ABTEST=7|1551955029|v1; SNUID=C0E7B5E83336B04D8452281C34A4A06F; JSESSIONID=aaaWedz9VN3W2hk1vGZKw; weixinIndexVisited=1; IPLOC=DE; sct=2; ppinf=5|1551958938|1553168538|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTozOkZSWnxjcnQ6MTA6MTU1MTk1ODkzOHxyZWZuaWNrOjM6RlJafHVzZXJpZDo0NDpvOXQybHVCcWlHWFJoMkx1MHBhWFlRUzJOWDYwQHdlaXhpbi5zb2h1LmNvbXw; pprdig=WxjaTtTZ4GIAAJ4HiR6MYUEnsVjtLCwR-veqmLz5lg6epW0nnqBmfAAbSUbfMNk_9ojiX8WTxKLMJOyRcF_iZeb6sqMRWEF-aHzHI0Jj41LyOzXzo4IEd1eTKUrY02xhYhqmTer0KiIB12JEOM6NMhA6zcrpXyrP8g0KS2jy-0c; sgid=30-39601585-AVyBA5qHXV1H89vTcMYQiczk; ppmdig=155195893900000015c111d9eff12d245155d997b6542ec1",
        'Host': "weixin.sogou.com",
        'Referer': "https://weixin.sogou.com/",
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }

    # session = Session()
    # detail_session = Session()
    queue = RedisQueue()

    def get_proxy(self):
        '''
        从代理池获取代理
        :return: 代理ip
        '''
        try:
            re = requests.get(PROXY_POOL_URL)
            if re.status_code == 200:
                return re.text
                #return '80.240.26.157:1226'
            return None
        except ConnectionError:
            return None

    def start(self):
        '''
        初始化工作
        '''
        # 全局更新Headers
        # self.session.headers.update(self.headers)
        start_url=self.base_url + '?' + urlencode({'type':2,'query':KEYWORD,'page':44})
        wechat_request = WechatRequest(url=start_url,callback = self.parse_index,need_proxy=True)
        # 调度第一个请求
        self.queue.add(wechat_request)


    def request(self,wechat_request):
        '''
        执行请求
        :param wechat_request：请求
        :return:响应
        '''
        try:
            if wechat_request.need_proxy:
                proxy = self.get_proxy()
                if proxy:
                    proxies = {
                        'http':'http://' + proxy
                    }
                    return requests.get(wechat_request.url,headers = self.headers,timeout = wechat_request.timeout,proxies=proxies)
                    #return self.session.send(wechat_request.prepare(),timeout = wechat_request.timeout,allow_redirects=False,proxies=proxies)
            else:
                return requests.get(wechat_request.url)

            # return self.detail_session.send(wechat_request.prepare(),timeout = wechat_request.timeout,allow_redirects=False)

        except(ConnectionError,ReadTimeout) as e:
            print(e.args)
            return False

    def error(self,wechat_request):
        '''
        错误处理
        :param wechat_request：请求
        '''
        wechat_request.fail_time += 1
        print('Request Failed',wechat_request.fail_time,'Times',wechat_request.url)
        if wechat_request.fail_time < MAX_FEILED_TIME:
            self.queue.add(wechat_request)
            
    
    def parse_index(self,response):
        '''
        解释索引页
        :param response: 响应
        :retrun：新的响应
        '''
        doc = pq(response.text)
        print(doc('#top_login').text())
        items =doc('.txt-box h3 a').items()
        for item in items:
            url = item.attr.href
            wechat_request= WechatRequest(url=url,callback = self.parse_detail,need_proxy=False)
            yield wechat_request

        next = doc('#sogou_next').attr.href
        if next:
            url = self.base_url + str(next)
            wechat_request = WechatRequest(url=url,callback = self.parse_index,need_proxy=True)
            yield wechat_request

    def parse_detail(self,response):
        '''
        解析详情页
        :param response:响应
        :return:微信公众号文章
        '''
        doc = pq(response.text)
        data ={
            'title':doc('#activity-name').text(),
            'content':doc('#js_content').text(),
            # 'nickname':doc('#meta_content > span:nth-child(2)').text(),
            # 'wechat':doc('#js_name').text()
        }
        yield data