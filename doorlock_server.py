import datetime
import socketserver
import threading
import time
import queue
import pymysql
import serial
import mail_check

HOST = '192.168.0.39' # 서버의 ip를 열음. (이 서버의 ip로 클라이언트가 접속을 해야 한다), 그전에 ping을 먼저 확인하도록.
PORT = 9900     		 # 포트번호 (같아야 함)
lock = threading.Lock()  # syncronized 동기화 진행하는 스레드 생성
chatTime=datetime.datetime.now()

user_name=""

class database: # 데이터 베이스 쿼리문 클래스
    con = pymysql.connect(host="localhost", user='root', password='0000', db="door_lock_db", charset='utf8')
    cur = con.cursor()

    # 로그인 아이디 비밀번호 회원가입 함수
    def member_insert(self,mem_name,mem_id,mem_pw): #멤버 테이블 추가 함수
        ppl = f"""INSERT INTO member VALUES(NULL,'{mem_name}','{mem_id}','{mem_pw}','0000','0','0','0','0',NULL); """
        self.cur.execute(ppl)
        self.con.commit()

    # 문열림 DB
    def open_insert(self,open_id):
        ppl = f"insert into open values('{open_id}','0','0','0','0','0','0','0');"
        self.cur.execute(ppl)
        self.con.commit()

    # 문닫힘 DB
    def warning_insert(self,warning_id):
        ppl = f"insert into warning values('{warning_id}','0','0','0','0','0','0','0');"
        self.cur.execute(ppl)
        self.con.commit()

    # db 아이디 비밀번호 호출 함수
    def member_id_pw(self):
        ppl = f"""select * from member;"""
        self.cur.execute(ppl)
        data = self.cur.fetchall()
        return data

    def open_data(self):
        ppl = f"select * from open;"
        self.cur.execute(ppl)
        data = self.cur.fetchall()
        return data

    def warning_data(self):
        ppl = f"select * from warning;"
        self.cur.execute(ppl)
        data = self.cur.fetchall()
        return data

    # db 데이터변경
    def member_update_data(self,table_name,change_data,user_id):
        ppl = f"update member set member_{table_name} = '{change_data}' where member_id = '{user_id}'"
        self.cur.execute(ppl)
        self.con.commit()

    def open_update_data(self,today,change_data,user_id):
        ppl = f"update open set open_{today} = '{change_data}' where open_id = '{user_id}'"
        self.cur.execute(ppl)
        self.con.commit()

    def warning_update_data(self,today,change_data,user_id):
        ppl = f"update warning set warning_{today} = '{change_data}' where warning_id = '{user_id}'"
        self.cur.execute(ppl)
        self.con.commit()

class Date :

    now = datetime.datetime.now()

    year = now.year
    month = now.month
    day = now.day

    date = datetime.date(year,month,day)

    weekday = date.weekday()

    def check_day(self):
        if self.weekday == 0 :
            return "mon"
        elif self.weekday == 1 :
            return "tue"
        elif self.weekday == 2 :
            return "wed"
        elif self.weekday == 3 :
            return "thu"
        elif self.weekday == 4 :
            return "fri"
        elif self.weekday == 5 :
            return "sat"
        else :
            return "sun"

sql_data = database()
today = Date()

class UserManager:  # 사용자관리 및 채팅 메세지 전송을 담당하는 클래스
    user = None
    def __init__(self):
        self.users = {}  # 사용자의 등록 정보를 담을 사전 {사용자 이름:(소켓,주소),...}

    def addUser(self, username, conn, addr):  # 사용자 ID를 self.users에 추가하는 함수
        if username in self.users:  # 이미 등록된 사용자라면
            conn.send('이미 등록된 사용자입니다.\n'.encode())
            return None

        # 새로운 사용자를 등록함
        lock.acquire()  # 스레드 동기화를 막기위한 락
        self.users[username] = (conn, addr)
        lock.release()  # 업데이트 후 락 해제

        return username

    def removeUser(self, username):  # 사용자를 제거하는 함수
        if username not in self.users:
            return
        del self.users[username]

    def messageHandler(self,username, msg):  # 전송한 msg를 처리하는 부분

        split_data = msg.split("*")

        if "/이메일인증" in msg :
            num = 1
            split_data = msg.split("*")
            check_code = mail_check.randomCode(num)
            for i in sql_data.member_id_pw() :
                if i[2] == split_data[2] :
                    return username.send("/이미 존재하는 아이디".encode())
            mail_check.check_email(split_data[1],split_data[2],check_code)
            self.email_code = check_code
            return username.send("/메일 전송 완료".encode())

        elif "/게스트 비밀번호 변경" in msg :
            print("게스트 비밀번호 :",split_data)
            return username.send("/게스트 비밀번호 변경 성공".encode())

        elif '/로그인' in msg:
            for i in sql_data.member_id_pw() :
                if split_data[1] == i[2] :
                    if split_data[2] == i[3] :
                        if i[9] == None :
                            login_data = "/로그인성공"+'*'+i[2]+'*'+i[4]+'*'+i[5]+'*'+i[6]+'*'+i[7]+'*'+i[8]
                            return username.send(login_data.encode())
                        else :
                            login_data = "/로그인성공"+'*'+i[2]+'*'+i[4]+'*'+i[5]+'*'+i[6]+'*'+i[7]+'*'+i[8]+'*'+i[9]
                            return username.send(login_data.encode())
                    else :
                        return username.send("/로그인실패".encode())
            return username.send("/로그인실패".encode())

        elif '/회원가입' in msg :
            if split_data[3] != self.email_code :
                return username.send("/인증번호 같지않음".encode())

            else :
                for i in sql_data.member_id_pw() :
                    if split_data[2] == i[2] :
                        return username.send("/중복 아이디".encode())

                sql_data.member_insert(split_data[1],split_data[2],split_data[4])
                sql_data.open_insert(split_data[2])
                sql_data.warning_insert(split_data[2])
                return username.send("/회원가입 성공".encode())

        elif "/etiquette" in msg :
            sql_data.member_update_data(split_data[0][1:],split_data[2],split_data[1])
            send_data = split_data[0][1:] + "*" + split_data[2]
            return username.send(send_data.encode())

        elif "/safe_record" in msg :
            sql_data.member_update_data(split_data[0][1:],split_data[2],split_data[1])
            send_data = split_data[0][1:] + "*" + split_data[2]
            return username.send(send_data.encode())

        elif "/fake_num" in msg :
            sql_data.member_update_data(split_data[0][1:],split_data[2],split_data[1])
            send_data = split_data[0][1:] + "*" + split_data[2]
            return username.send(send_data.encode())

        elif "/random_num" in msg :
            sql_data.member_update_data(split_data[0][1:],split_data[2],split_data[1])
            send_data = split_data[0][1:] + "*" + split_data[2]
            return username.send(send_data.encode())

        elif "/door_pw" in msg :
            sql_data.member_update_data(split_data[0][1:],split_data[2],split_data[1])
            send_data = "/도어락 비밀번호 변경 성공" + "*" + split_data[2]
            return username.send(send_data.encode())

        elif "/guest_pw" in msg :
            sql_data.member_update_data(split_data[0][1:],split_data[2],split_data[1])
            send_data = "/게스트 비밀번호 설정 완료" + "*" + split_data[2]
            return username.send(send_data.encode())

        elif "/Graph Data" in msg :

            send_data = ""

            for i in sql_data.open_data() :
                if split_data[1] == i[0] :
                    send_data = "/Graph" + "*" + i[1] + "*" + i[2] + "*" + i[3] + "*" + i[4] + "*" + i[5] + "*" + i[6] + "*" + i[7] + "*"
            for j in sql_data.warning_data() :
                if split_data[1] == j[0] :
                    send_data += j[1] + "*" + j[2] + "*" + j[3] + "*" + j[4] + "*" + j[5] + "*" + j[6] + "*" + j[7]
                    return username.send(send_data.encode())

        elif "/open" in msg :
            for i in sql_data.open_data() :
                if split_data[0] == i[0] :
                    if today.check_day() == "mon" :
                        mon_count = int(i[1]) + 1
                        return sql_data.open_update_data(today.check_day(),mon_count,split_data[0])
                    elif today.check_day() == "tue" :
                        tue_count = int(i[2]) + 1
                        return sql_data.open_update_data(today.check_day(),tue_count,split_data[0])
                    elif today.check_day() == "wed" :
                        wed_count = int(i[3]) + 1
                        return sql_data.open_update_data(today.check_day(),wed_count,split_data[0])
                    elif today.check_day() == "thu" :
                        thu_count = int(i[4]) + 1
                        return sql_data.open_update_data(today.check_day(),thu_count,split_data[0])
                    elif today.check_day() == "fri" :
                        fri_count = int(i[5]) + 1
                        return sql_data.open_update_data(today.check_day(),fri_count,split_data[0])
                    elif today.check_day() == "sat" :
                        sat_count = int(i[6]) + 1
                        return sql_data.open_update_data(today.check_day(),sat_count,split_data[0])
                    else :
                        sun_count = int(i[7]) + 1
                        return sql_data.open_update_data(today.check_day(),sun_count,split_data[0])

        elif "/warning" in msg :
            for i in sql_data.warning_data() :
                if split_data[0] == i[0] :
                    if today.check_day() == "mon" :
                        mon_count = int(i[1]) + 1
                        return sql_data.warning_update_data(today.check_day(),mon_count,split_data[0])
                    elif today.check_day() == "tue" :
                        tue_count = int(i[2]) + 1
                        return sql_data.warning_update_data(today.check_day(),tue_count,split_data[0])
                    elif today.check_day() == "wed" :
                        wed_count = int(i[3]) + 1
                        return sql_data.warning_update_data(today.check_day(),wed_count,split_data[0])
                    elif today.check_day() == "thu" :
                        thu_count = int(i[4]) + 1
                        return sql_data.warning_update_data(today.check_day(),thu_count,split_data[0])
                    elif today.check_day() == "fri" :
                        fri_count = int(i[5]) + 1
                        return sql_data.warning_update_data(today.check_day(),fri_count,split_data[0])
                    elif today.check_day() == "Sat" :
                        sat_count = int(i[6]) + 1
                        return sql_data.warning_update_data(today.check_day(),sat_count,split_data[0])
                    else :
                        sun_count = int(i[7]) + 1
                        return sql_data.warning_update_data(today.check_day(),sun_count,split_data[0])

        elif "/나가기" in msg:
            self.removeUser(self.user)

    def sendMessageToAll(self, msg):
        for conn, addr in self.users.values():
            conn.send(msg.encode())

class MyTcpHandler(socketserver.BaseRequestHandler):
    userman = UserManager()

    def handle(self):  # 클라이언트가 접속시 클라이언트 주소 출력
        print('[%s] 연결됨' % self.client_address[0])
        try:
            while True:
                msg = self.request.recv(1024)
                print("메시지입니다 :",msg.decode())
                self.userman.messageHandler(self.request, msg.decode())

        except Exception as e:
            print(e)

        print('[%s] 접속종료' % self.client_address[0])
        self.userman.removeUser(user_name)

class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def runServer():
    print('+++ 스마트도어락 서버 오픈.')
    try:
        server = ChatingServer((HOST, PORT), MyTcpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('--- 스마트도어락 서버 종료.')
        server.shutdown()
        server.server_close()

runServer()