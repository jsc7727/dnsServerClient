# Dns with Python

1. Project 명
Small DNS 구현
 
2. 처리 과정
클라이언트가 서버에 접속하여 query를 요청하면 결과를 클라이언트에게 전송함.
 
3. 구현시 고려 사항
1) 클라이언트의 query는 domain name이나 IP address 형식으로 구성됨.
2) domain entry는 <netdb.h>의 hostent 구조체 형식에 기초하며 필요에 따라
member를 추가할 수 있음.
3) 각 서버는 자신의 DNS 테이블을 유지, 관리하여야 함.
4) 내부 테이블에 없는 경우 외부 DNS를 이용하여 처리 후 내부 테이블 update.
5) 잘못된 입력이나 존재하지 않는 domain 또는 IP 주소의 경우 error handling 함.
6) 각 domain에 대한 hit 빈도수 관리(일별/월별/분기별 등)
 
4. 평가시 고려 사항
1) DNS 기능 완성도 및 결과의 정확성
2) DNS 테이블의 유지 관리 정도
3) 적절한 search algorithm 활용도
4) Domain hit 빈도수 출력 여부
 
5. 가산점 부분
1) Program의 conciseness & documentation
2) 자주 찾는 domain에 대한 caching 기능 제공
 예) 많은 hit수를 갖는 domain을 테이블의 앞에 두면 search time이 줄어듬
3) 클라이언트의 정보 관리(Log 파일 등)
4) 예외 경우의 에러 처리

# dns server
1. make file DNS\addon\mysqlConfig.conf  
    ```editorconfig
    [dbConfig]
    host : 127.0.0.1
    user: root
    password: root
    database: database
    charset: utf8
    use_unicode: True
    port: 3306
    ```  
   
2. install mysqlClient [download](https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient)  
```pip install (download version)```  

3. python ./server.py


# dns client

1. python ./client.py