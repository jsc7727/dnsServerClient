from DNS.addon.DbMysql import mysql


def addCache(cache, domain, address, count):
    check = True
    for x in cache:
        if x['address'] == address:
            x['domain'].append(domain)
            x['count'] += 1
            check = False
            break
    if check:
        cache.append({'domain': [domain], 'address': address, 'count': count})


def checkCache(cache: list, recvData: str, check: int):
    res = None
    changeCheck = True
    if check:
        for x in cache:
            if x['address'] == recvData:
                res = x
                x['count'] += 1
                changeCheck = False
                break
    else:
        for x in cache:
            if recvData in x['domain']:
                res = x
                x['count'] += 1
                break

    if changeCheck: cache.sort(key=lambda x: x['count'], reverse=True)
    return res


def dbDataConvertForInitCache(data):
    result = []
    for k in data:
        if not result:
            k['domain'] = k['domain'].split()
            result.append(k)
            continue

        check = True
        for x in result:
            if k['address'] == x['address']:
                x['domain'].append(k['domain'])
                check = False
                break

        if check:
            k['domain'] = k['domain'].split()
            result.append(k)
    return result


def initCache(msql: mysql):
    try:
        tp = msql.getCacheFromDb(10)
        cc = dbDataConvertForInitCache(tp)
        print(f"init cache from DB : {cc}")
    except:
        print('init Cache error from cacheModule.py')
    return cc
