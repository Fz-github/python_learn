from setting import MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_PWD,MYSQL_DATABASE
import pymysql

class MySQL():
    def __init__(self,host=MYSQL_HOST,port=MYSQL_PORT,user=MYSQL_USER,password=MYSQL_PWD,database=MYSQL_DATABASE):
        '''
        MySQL初始化
        '''
        try:
            self.db = pymysql.connect(host,user,password,database,port= port,charset= 'utf8')
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(e.args)

    def insert(self,table,data):
        '''
        插入数据
        :param table: 数据表
        :param data:数据 
        :return:
        '''
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql_str = 'insert into %s (%s) values(%s)'%(table,keys,values)
        try:
            self.cursor.execute(sql_str,tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()

    def select_all(self,table):
        sql_str = 'select * from ' + table
        try:
            self.cursor.execute(sql_str)
            results = self.cursor.fetchall()
            return results

        except Exception as e:
            print(e.args)

