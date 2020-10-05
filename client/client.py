import json
import socket

HOST = 'localhost'  # The remote host
PORT = 12345  # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
while True:
    data = ""
    try:
        byteQuery = bytes(input(), 'utf-8')
        type(byteQuery)
        if not byteQuery:
            print("다시 입력하세요", end="\n")
            continue
        elif byteQuery == b'getDb':
            print("root domain hit\n")
            s.sendall(byteQuery)
            data = s.recv(1024)
            dictData = json.loads(str(data, 'utf-8'))
            for x in dictData:
                print(f"domain : {x['domain']} | address : {x['address']} | count : {x['count']} | "
                      f"startDate : {x['startDate']} | endDate : {x['endDate']}")
            print()
            continue
        elif byteQuery == b'quit' and b'q':
            break
        print(f"input data : {byteQuery}\n")
        s.sendall(byteQuery)
        data = s.recv(1024)
        print('Received', repr(data))
    except:
        print(data)
s.close()
