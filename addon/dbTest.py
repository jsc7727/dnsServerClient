from DNS.addon.DbMysql import mysql
import MySQLdb
import os

if __name__ == '__main__':
    print(os.path.dirname(os.path.abspath(__file__)))
    msql = mysql()
    cursor = msql.cursor
    try:
        # print('데이터베이스가 연결되었습니다.')
        # cursor.execute("SHOW DATABASES")
        # for x in cursor:
        #     print(x)
        print()
        cursor.execute("SHOW TABLES;")
        # for x in cursor:
        #     print(x)
        #msql.dropTable()
        #msql.mkIpTable()
        #msql.addIp("192.168.0.9")
        #msql.addDomain("hun.hs.ac.kr",'203.252.23.8')
        #a = msql.findIpByDomain("hs.ac.kr")
        #print(a)
        #print(msql.findDomainByIp("192.168.0.1"))

    except MySQLdb.Error as err:
        print('오류 : ', err)

.addon/mysqlConfig.conf
.addon/dbTest.py
test
.server/log.txt
__pycache__/