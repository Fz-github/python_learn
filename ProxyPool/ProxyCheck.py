VALID_STATUS_CODES = [200]
TEST_URL = 'https://www.baidu.com'
BTACH_TEST_SIZE = 100

from RedisHelp import RedisHelp
import time
import requests
import asyncio
import aiohttp
from asyncio import TimeoutError
from aiohttp import ClientProxyConnectionError as ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError,ClientError
from ssl import SSLCertVerificationError

class Tester(object):
    def __init__ (self):
        self.redis = RedisHelp()

    async def test_single_proxy(self,proxy):
        '''
        测试单个代理
        :param proxy: 代理
        '''
        # conn = aiohttp.TCPConnector(verify_ssl=False)
        #async with aiohttp.ClientSession(connector=conn) as session:
        async with aiohttp.ClientSession() as session:        
            try:
                if isinstance(proxy,bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://'+ proxy
                print('正在测试',proxy)
                async with session.get(TEST_URL,proxy=real_proxy,timeout = 15) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print(proxy,'代理可用')
                    else:
                        self.redis.decrease(proxy)
                        print(proxy,'请求响应码不合法')
            except(ProxyConnectionError,ClientConnectorError,TimeoutError,AttributeError):
                self.redis.decrease(proxy)
                print(proxy,'代理请求失败')
    

    def run (self):
        '''
        测试主函数
        '''
        print("测试器开始运行")
        try:
            proxies = self.redis.all()
            loop = asyncio.get_event_loop()
            #批量测试
            for i in range(0,len(proxies),BTACH_TEST_SIZE):
                test_proxies = proxies[i:i+BTACH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print("测试器发生错误",e.args)

tester = Tester()
tester.run()
                    