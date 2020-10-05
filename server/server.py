import re
import socket

from DNS.addon.DbMysql import mysql
from DNS.addon.RecModule import file
from DNS.addon.cacheModule import checkCache, initCache, addCache
from DNS.addon.dbModule import dicDbCheck, databaseHit

port = 12345


def errorHandler(addr, f, connect, errorMsg):
    connect.sendall(bytes(f"error : {errorMsg}", 'utf-8'))
    f.logWriter(f"error : {errorMsg}", addr)


def getDataByWeb(recvData, check):
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


def checkIpDomain(data):
    rexCheckIp = re.compile('[0-9]+.[0-9]+.[0-9]+.[0-9]+')
    resIp = rexCheckIp.match(data)
    #print(resIp)
    if resIp is None:
        rexCheckDomain = re.compile("^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}")
        resDomain = rexCheckDomain.match(data)
        #print(resDomain)
        if resDomain is None:
            return -1

    return resIp and 1 or 0


def recvSend_serv(msql: mysql, f: file, connect, addr, cache):
    try:
        while True:
            cache = cache[:10]
            print(f"main start , cache : {cache}")
            result = ""
            recvData = str(connect.recv(1024), 'utf-8')

            if not recvData:
                break
            f.logWriter(f"recv data \"{recvData}\"\n", addr)

            # getDb 문자열을 받을 경우
            if recvData == "getDb":
                databaseHit(msql,f, connect, addr)
                continue

            # ip or domain 확인하기
            # ex) (-1 or 0 or 1) checkIpDomain(check data)
            # ip = 1 | domain = 0 | 둘다 아니면 -1
            check = checkIpDomain(recvData)

            # ip or domain 이 아닐 경우
            if check == -1:
                errorHandler(addr, f, connect, "recvData is't ip or domain type\n")
                continue

            checkCacheRes = checkCache(cache, recvData, check)
            if checkCacheRes is not None:
                print("==== cache hit ====")
                print(f"{checkCacheRes['domain']} : {checkCacheRes['address']} in {cache}\n")
                msql.addCount(checkCacheRes['address'])
                result = check and checkCacheRes['domain'] or checkCacheRes['address']

            else:
                # 받은 데이터로 db에서 체크함.
                # ex) (string) dbCheck(msql: mysql, recvData: str, check: int)

                # ip and address init
                ip = ""
                domain = ""
                count = ""

                queryResponse = dicDbCheck(msql, recvData, check)
                print(f"queryResponse : {queryResponse}\n")
                if queryResponse:
                    result = check and queryResponse['domain'] or queryResponse['address']
                    ip = queryResponse['address']
                    domain = queryResponse['domain']
                    count = queryResponse['count']
                else:
                    result = getDataByWeb(recvData, check)
                    #print(result)

                    if result == "error":
                        errorHandler(addr, f, connect, "not found ip or domain by web\n")
                        continue

                    # domain은 여러개가 가능하므로 해당 ip가 있는지 확인후 있다면 테이블에 맞춰 도메인만 추가해준다.
                    ip = check and recvData or result
                    domain = not check and recvData or result
                    ipTable = msql.getIpTable(ip)
                    if ipTable != None:
                        msql.addDomain(domain, ipTable['id'])
                        msql.addCount(ip)
                        count = ipTable['count']
                    else:
                        msql.addIp(ip)
                        ipTable = msql.getIpTable(ip)
                        msql.addDomain(domain, ipTable['id'])
                        count = ipTable['count']
                addCache(cache,domain,ip,count)
                #cache.append({'domain': [domain], 'address': ip,'count': count})

            if result:
                if type(result) == list:
                    result = " | ".join(result)
                connect.sendall(bytes(result, 'utf-8'))
                f.logWriter(f"\"{recvData}\" = \"{result}\"\n", addr)
    except socket.error as error:
        print("error : ", error)


if __name__ == '__main__':
    test = 1
    host = ''  # Symbolic name meaning all available interfaces
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    msql = mysql()
    f = file("log.txt", 'a+')

    f.logWriter(f"create socket localhost {port}---------------------\n")
    # SOCK_STREAM = TCP
    # SOCK_DGRAM = UDP
    s.bind((host, port))
    s.listen(10)
    cache = initCache(msql)
    while True:
        connect, addr = s.accept()
        f.logWriter(f"Connected\n", addr)
        try:
            recvSend_serv(msql, f, connect, addr, cache)
        except socket.error as error:
            print("error : ", error)
        f.logWriter(f"Disconnected\n\n", addr)
        connect.close()
