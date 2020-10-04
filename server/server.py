import json
import re
import socket
from time import strftime, localtime

import MySQLdb

from DNS.addon.DbMysql import mysql
from DNS.addon.RecModule import file
port = 45678
errorPrint = 1

def checkCash(cash: list, recvData: str, check: int):
    res = None
    if check:
        for x in cash:
            if x['address'] == recvData:
                res = x
    else:
        for x in cash:
            if x['domain'] == recvData:
                res = x
    return res


def domainHit(msql: mysql):
    data = msql.hitCount(10)
    # print(data)
    if data:
        for x in data:
            print(f"domain : {x['domain']} | address : {x['address']} | count : {x['count']}")
        print()
        sendMsg = bytes(json.dumps(data), "utf-8")
        connect.sendall(sendMsg)
        logWriter(addr, f"domain : {x['domain']} | address : {x['address']} | count : {x['count']}\n")
    else:
        connect.sendall(b"error : domain table is empty")
        logWriter(addr, f"error : domain table is empty")


def errorHandler(addr, connect, errorMsg):
    connect.sendall(bytes(f"error : {errorMsg}", 'utf-8'))
    logWriter(addr, f"error : {errorMsg}")


def getDataByWeb(check):
    result = None
    print("getDataByWeb")
    try:
        if check:
            res = socket.gethostbyaddr(recvData)
            print(f"domain : {res}\n")
            result = res[0]
        else:
            res = socket.gethostbyname(recvData)
            print(f"ip : {res}\n")
            result = res  # 에러 나는 입력값일 경우 timeout 적용해야함.
    except:
        result = "error"
        print("error\n")
    return result


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


def logWriter(address, logMsg):
    log = file("log.txt", 'a+')
    if address == "":
        log.write(f"{addTime()} | {logMsg}")
    else:
        log.write(f"{addTime()} | {address} |{logMsg}")
    log.f.close()


def addTime():
    return strftime("%Y-%m-%d %a %H:%M:%S ", localtime())


def checkIpDomain(data):
    rexCheckIp = re.compile('[0-9]+.[0-9]+.[0-9]+.[0-9]+')
    resIp = rexCheckIp.match(data)
    print(resIp)
    if resIp == None:
        rexCheckDomain = re.compile("^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}")
        resDomain = rexCheckDomain.match(data)
        print(resDomain)
        if resDomain == None:
            return -1

    return resIp and 1 or 0


if __name__ == '__main__':
    test = 1
    host = ''  # Symbolic name meaning all available interfaces
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    msql = mysql()

    logWriter("", f"create socket localhost {port}---------------------\n\n")
    # SOCK_STREAM = TCP
    # SOCK_DGRAM = UDP
    s.bind((host, port))
    s.listen(10)
    #cash = []
    while True:
        connect, addr = s.accept()
        print(f"Connected by {addr}")
        logWriter(addr, f"Connected\n")
        try:
            while True:
                cash = []
                print(f"cash : {cash}")
                list = msql.hitCount(10)
                for x in list:
                    cash.append(x)
                print(cash)
                result = ""
                recvData = str(connect.recv(1024), 'utf-8')

                if not recvData:
                    break
                logWriter(addr, f"recv data \"{recvData}\"\n")

                # domain hit 문자열을 받을 경우
                if recvData == "domain hit":
                    domainHit(msql)
                    continue

                # ip or domain 확인하기
                # ex) (-1 or 0 or 1) checkIpDomain(check data)
                # ip = 1 | domain = 0 | 둘다 아니면 -1
                check = checkIpDomain(recvData)

                # ip or domain 이 아닐 경우
                if check == -1:
                    errorHandler(addr, connect, "recvData is't ip or domain type\n")
                    continue

                checkCashRes = checkCash(cash, recvData, check)
                print(f"check Cash : {checkCashRes}\n")
                if checkCashRes != None:
                    print("==== cash hit ====\n")
                    print(cash,end='\n')
                    msql.addCount(checkCashRes['address'])
                    result = check and checkCashRes['domain'] or checkCashRes['address']
                else:
                    # 받은 데이터로 db에서 체크함.
                    # ex) (string) dbCheck(msql: mysql, recvData: str, check: int)
                    queryResponse = dbCheck(msql, recvData, check)
                    print(f"queryResponse : {queryResponse}\n")
                    if queryResponse:
                        result = queryResponse[0][not check]
                        msql.addCount(queryResponse[0][1])
                    else:
                        result = getDataByWeb(check)
                        print(result)

                        if result == "error":
                            errorHandler(addr, connect, "not found ip or domain by web");
                            continue

                        # domain은 여러개가 가능하므로 해당 ip가 있는지 확인후 있다면 테이블에 맞춰 도메인만 추가해준다.
                        ip = check and recvData or result
                        domain = not check and recvData or result
                        ipId = msql.getIpTableId(ip)
                        if ipId != None:
                            ipId = msql.getIpTableId(ip)
                            msql.addDomain(domain, ipId)
                        else:
                            msql.addIp(result)
                            ipId = msql.getIpTableId(ip)
                            msql.addDomain(domain, ipId)

                if result:
                    connect.sendall(bytes(result, 'utf-8'))
                    logWriter(addr, f"\"{recvData}\" = \"{result}\"\n")
        except socket.error as error:
            print("error : ", error)
        logWriter(addr, f"Disconnected\n\n")
        connect.close()
