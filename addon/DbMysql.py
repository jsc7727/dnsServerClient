import configparser
import os

import MySQLdb


class mysql:
    def __init__(self):
        config = configparser.ConfigParser()
        file = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(file, 'mysqlConfig.conf'))
        _config = self.get_config(config)
        print(_config)
        self.conn = MySQLdb.connect(**_config)
        self.cursor = self.conn.cursor()
        self.cursorDict = self.conn.cursor(MySQLdb.cursors.DictCursor)
        print('데이터베이스가 연결되었습니다.')
        self.cursor.execute("SHOW DATABASES")
        check = input("if want you drop table and make new table?\n yes : input yes \n no : input any key\n")
        if check == 'yes':
            self.dropTable()
            self.mkIpTable()
            print("삭제후 재생성 성공")

    def hitCount(self, limit=(-1)):
        sql = "SELECT domain, INET_NTOA(address) as address, count, startDate, endDate FROM dnssc.domain_table LEFT OUTER JOIN dnssc.ip_table ON ip_table.id = domain_table.ip_table_id ORDER BY count DESC"
        if limit != -1:
            sql + f"limit {limit}"
        self.cursorDict.execute(sql)
        data = self.cursorDict.fetchall()
        return data

    def getCacheFromDb(self, limit=(-1)):
        sql = "SELECT domain, INET_NTOA(address) as address, count FROM dnssc.domain_table LEFT OUTER JOIN dnssc.ip_table ON ip_table.id = domain_table.ip_table_id ORDER BY count DESC"
        if limit != -1:
            sql + f"limit {limit}"
        self.cursorDict.execute(sql)
        data = self.cursorDict.fetchall()
        return data

    def getIpTable(self, ip):
        sql = "SELECT id,count FROM dnssc.ip_table WHERE address = INET_ATON(%s)"
        val = (ip,)
        print(f"ip: {ip}")
        self.cursorDict.execute(sql, val)
        getIpTable = self.cursorDict.fetchone()
        print(getIpTable)
        return getIpTable

    def addIp(self, ip, count=1):
        sql = "INSERT INTO ip_table (address,count,startDate,endDate) VALUES (INET_ATON(%s), %s, now(), now())"
        val = (ip, count)
        self.cursor.execute(sql, val)
        print(self.cursor.rowcount, " : ip가 성공적으로 추가됨.")
        self.conn.commit()
        return

    def addDomain(self, domain, ip_table_id):
        sql2 = "INSERT INTO domain_table (domain,ip_table_id) VALUES(%s,%s)"
        val2 = (domain, (ip_table_id,))
        self.cursor.execute(sql2, val2)
        print(self.cursor.rowcount, " : domain 이 성공적으로 추가됨.")
        self.conn.commit()

    def addCount(self, ip):
        sql = "UPDATE ip_table SET count = count + 1, endDate = now() WHERE ip_table.address = INET_ATON(%s);"
        print(ip)
        self.cursor.execute(sql, (ip,))
        self.conn.commit()

    def findIpByDomain(self, domain):
        sql = "SELECT domain, INET_NTOA(address), ip_table.id, count FROM dnssc.domain_table LEFT OUTER JOIN dnssc.ip_table ON ip_table.id = domain_table.ip_table_id WHERE domain_table.domain = (%s);"
        val = (domain,)
        self.cursor.execute(sql, val)
        data = self.cursor.fetchall()
        return data

    def findDomainByIp(self, ip):
        sql = "SELECT domain, INET_NTOA(address), ip_table.id, count FROM dnssc.domain_table LEFT OUTER JOIN dnssc.ip_table ON ip_table.id = domain_table.ip_table_id WHERE ip_table.address = (INET_ATON(%s));"
        val = (ip,)
        self.cursor.execute(sql, val)
        data = self.cursor.fetchall()
        return data

    def dicFindIpByDomain(self, domain):
        sql = "SELECT domain, INET_NTOA(address) as address, ip_table.id, count FROM dnssc.domain_table LEFT OUTER JOIN dnssc.ip_table ON ip_table.id = domain_table.ip_table_id WHERE domain_table.domain = (%s);"
        val = (domain,)
        self.cursorDict.execute(sql, val)
        data = self.cursorDict.fetchone()
        return data

    def dicFindDomainByIp(self, ip):
        sql = "SELECT domain, INET_NTOA(address) as address, ip_table.id, count FROM dnssc.domain_table LEFT OUTER JOIN dnssc.ip_table ON ip_table.id = domain_table.ip_table_id WHERE ip_table.address = (INET_ATON(%s));"
        val = (ip,)
        self.cursorDict.execute(sql, val)
        data = self.cursorDict.fetchone()
        return data


    def dropTable(self):
        self.cursor.execute("SET foreign_key_checks = 0;")
        self.cursor.execute("DROP TABLE ip_table")
        self.cursor.execute("DROP TABLE domain_table")
        self.cursor.execute("SET foreign_key_checks = 1;")

    def mkIpTable(self):
        self.cursor.execute(
            "CREATE TABLE dnssc.ip_table ("
            "id INT NOT NULL AUTO_INCREMENT,"
            "address INT(4) UNSIGNED NOT NULL,"
            "count INT NOT NULL DEFAULT 0,"
            "startDate timestamp NOT NULL,"
            "endDate timestamp,"
            "UNIQUE INDEX id_UNIQUE (id ASC) VISIBLE,"
            "UNIQUE INDEX address_UNIQUE (address ASC) VISIBLE,"
            "PRIMARY KEY (id));"
        )

        self.cursor.execute(
            "CREATE TABLE dnssc.domain_table ("
            "id INT NOT NULL AUTO_INCREMENT,"
            " domain VARCHAR(255) NOT NULL,"
            " ip_table_id INT NOT NULL,PRIMARY KEY (id),"
            "UNIQUE INDEX id_UNIQUE (id ASC) VISIBLE,"
            "UNIQUE INDEX domain_UNIQUE ( domain ASC) VISIBLE, "
            "CONSTRAINT iptable FOREIGN KEY (ip_table_id) REFERENCES dnssc.ip_table (id) ON DELETE NO ACTION ON UPDATE NO ACTION)"
            "ENGINE = InnoDB;"
        )
        self.conn.commit()

    def get_config(self, cfg):
        return {
            'host': cfg.get('dbConfig', 'host'),
            'user': cfg.get('dbConfig', 'user'),
            'password': cfg.get('dbConfig', 'password'),
            'database': cfg.get('dbConfig', 'database'),
            'charset': cfg.get('dbConfig', 'charset'),
            'use_unicode': cfg.getboolean('dbConfig', 'use_unicode'),
            'port': cfg.getint('dbConfig', 'port')
        }


if __name__ == '__main__':
    msql = mysql()
    cursor = msql.cursor
    try:
        print('데이터베이스가 연결되었습니다.')
        cursor.execute("SHOW DATABASES")
        for x in cursor:
            print(x);

        # msql.addIp("127.0.0.2")

        # cursor.execute(sql, val)
        # print(cursor.rowcount, "Record inserted successfully into Laptop table")
        # print(cursor.fetchall())
        # msql.findIpByDomain("hs.ac.kr")

        # msql.mkIpTable()
        msql.findIpByDomain("hs.ac.kr")
        # msql.cursor.execute(
        #     "CREATE TABLE dnssc.ip_table ("
        #     "id INT NOT NULL AUTO_INCREMENT,"
        #     "address INT(4) UNSIGNED NOT NULL,"
        #     "count INT NOT NULL DEFAULT 0,"
        #     "mytimestamp timestamp NOT NULL,"
        #     "UNIQUE INDEX id_UNIQUE (id ASC) VISIBLE,"
        #     "UNIQUE INDEX address_UNIQUE (address ASC) VISIBLE,"
        #     "PRIMARY KEY (id));"
        # )

        msql.conn.commit()

        print('처리가 완료되었습니다.')
    except MySQLdb.Error as err:
        print('오류 : ', err)

# many ex)
# cursor.executemany("""INSERT INTO breakfast (name, spam, eggs, sausage, price) VALUES (%s, %s, %s, %s, %s)""",
#               [("Spam and Sausage Lover's Plate", 5, 1, 8, 7.95), ("Not So Much Spam Plate", 3, 2, 0, 3.95),
#                ("Don't Wany ANY SPAM! Plate", 0, 4, 3, 5.95)])
# sql_insert = ("insert into actor2 values (1, '길동', '홍', now())")
