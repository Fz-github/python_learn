from setting import VALID_STATUES,MYSQL_TABLE
from redisqueue import RedisQueue
from spider import Spider
from request import WechatRequest
from mysql import MySQL
import time
from multiprocessing import Pool

queue = RedisQueue()
mysql = MySQL()
spider = Spider()

def schedule():
    '''
    调度请求
    '''
    while not queue.empty():
        wechat_request = queue.pop()
        callback = wechat_request.callback
        print('Schedule',wechat_request.url)
        response = spider.request(wechat_request)
        if response and response.status_code in VALID_STATUES:
            results = list(callback(response))
            if results:
                for result in results:
                    print("New result",result)
                    if isinstance(result,WechatRequest):
                        queue.add(result)
                    if isinstance(result,dict):
                        mysql.insert(MYSQL_TABLE,result)
            else:
                spider.error(wechat_request)
        else:
            spider.error(wechat_request)
        
        time.sleep(3)

if __name__ == "__main__":
    spider.start()
    pool = Pool(processes=4)
    for i in range(4):
        pool.apply_async(schedule)
    
    pool.close()
    pool.join()
