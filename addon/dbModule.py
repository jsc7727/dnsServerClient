import json

import MySQLdb
from time import strftime, localtime
from DNS.addon.DbMysql import mysql


def databaseHit(msql: mysql, f, connect, addr):
    try:
        data = msql.hitCount()
        # print(data)
        if data:
            for x in data:
                print(f"domain : {x['domain']} | address : {x['address']} | count : {x['count']} | startDate : "
                      f"{x['startDate']} | endDate : {x['endDate']}")
                x['startDate'] = str(x['startDate'])
                x['endDate'] = str(x['endDate'])
            print()
            sendMsg = bytes(json.dumps(data), "utf-8")
            connect.sendall(sendMsg)
            # f.logWriter(f"domain : {data['domain'][0]} | address : {data['address']} | count: {data['count']}\n", addr)
        else:
            connect.sendall(b"error : domain table is empty")
            f.logWriter(f"error : domain table is empty", addr)
    except MySQLdb.Error as err:
        print('오류 : ', err)


def dbCheck(msql: mysql, recvData, checkIp):
    queryResponse = None
    try:
        if checkIp:
            queryResponse = msql.findDomainByIp(recvData)
            print("ip 임")
        else:
            queryResponse = msql.findIpByDomain(recvData)
            print("domain임")

    except MySQLdb.Error as err:
        print('오류 : ', err)
    return queryResponse


def dicDbCheck(msql: mysql, recvData, checkIp):
    queryResponse = None
    try:
        if checkIp:
            queryResponse = msql.dicFindIpByDomain(recvData)
            print("ip 임")
        else:
            queryResponse = msql.dicFindIpByDomain(recvData)
            print("domain임")
        if queryResponse != None:
            msql.addCount(queryResponse['address'])

    except MySQLdb.Error as err:
        print('오류 : ', err)
    return queryResponse
