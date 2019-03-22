from pickle import dumps,loads
from request import WechatRequest
from redis import StrictRedis
from setting import REDIS_HOST,REDIS_PASSWORD,REDIS_DATABASE,REDIS_PORT,REDIS_KEY



class RedisQueue():
    def __init__(self):
        '''
        初始化Redis
        '''
        self.db = StrictRedis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DATABASE,password=REDIS_PASSWORD)

    def add(self,request):
        '''
        向队列添加序列化后的Request
        :param request:请求对象
        :param  fail_time: 失败次数
        :return: 添加结果
        '''
        if isinstance(request,WechatRequest):
            return self.db.rpush(REDIS_KEY,dumps(request))
        else:
            return False

    def pop(self):
        '''
        取出下一个Request并反序列化
        '''
        if self.db.llen(REDIS_KEY):
            return loads(self.db.lpop(REDIS_KEY))
        else:
            return False
    
    def empty(self):
        '''
        队列是否为空
        '''
        return self.db.llen(REDIS_KEY) == 0
