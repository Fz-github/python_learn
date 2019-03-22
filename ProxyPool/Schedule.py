TESTER_CYCLE = 20
GETTER_CYCLE = 20
TESTER_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = True

from multiprocessing import Process
from API import app
from Crawler import Getter
from ProxyCheck import Tester
import time

class Scheduler():
    def scheduler_tester(self,cycle=TESTER_CYCLE):
        '''
        定时检测
        '''
        tester = Tester()
        while True :
            tester.run()
            time.sleep(cycle)


    def scheduler_getter(self,cycle=GETTER_CYCLE):
        '''
        定时获取代理
        '''
        getter = Getter()
        while True:
            print('开始抓取')
            getter.run()
            time.sleep(cycle)
        
    def scheduler_api(self):
        '''
        开启API
        '''
        app.run()

    def run(self):
        if TESTER_ENABLED:
            tester_process = Process(target = self.scheduler_tester)
            tester_process.start()
        
        if GETTER_ENABLED:
            getter_process = Process(target = self.scheduler_getter)
            getter_process.start()

        if API_ENABLED:
            api_process = Process(target = self.scheduler_api)
            api_process.start()


