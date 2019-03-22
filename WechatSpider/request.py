from setting import TIMEOUT
from requests import Request

class WechatRequest(Request):
    '''重新定义微信请求的数据结构'''
    def __init__(self,url,callback,method = 'GET',headers = None,need_proxy = False,fail_time = 0,timeout = TIMEOUT):
        Request.__init__(self,method,url,headers)
        self.callback = callback
        self.need_proxy = need_proxy
        self.fail_time = fail_time
        self.timeout = timeout