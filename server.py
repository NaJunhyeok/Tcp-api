import socket
import threading
import requests
from urllib.parse import quote_plus, unquote, urlencode
from datetime import *

import warnings
warnings.filterwarnings(action='ignore')

url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"

serviceKey = "" # 공공데이터 포털에서 생성된 본인의 서비스 키를 복사 / 붙여넣기
serviceKeyDecoded = unquote(serviceKey, 'UTF-8') # 공데이터 포털에서 제공하는 서비스키는 이미 인코딩된 상태이므로, 디코딩하여 사용해야 함

location = {'서울':[60,127],'부산':[98,76],'인천':[55,124],'대구':[89,90],'대전':[67,100],'광주':[58,74],'울산':[102,84],'제주':[52,38],'청주':[69,107],'충주':[76,114]}

def api(input):
    now = datetime.now()
    today = datetime.today().strftime("%Y%m%d")
    y = date.today() - timedelta(days=1)
    yesterday = y.strftime("%Y%m%d")
    nx = location[input][0] # 위도와 경도를 x,y좌표로 변경
    ny = location[input][1]

    if now.minute<45: # base_time와 base_date 구하는 함수
        if now.hour==0:
            base_time = "2330"
            base_date = yesterday
        else:
            pre_hour = now.hour-1
            if pre_hour<10:
                base_time = "0" + str(pre_hour) + "30"
            else:
                base_time = str(pre_hour) + "30"
            base_date = today
    else:
        if now.hour < 10:
            base_time = "0" + str(now.hour) + "30"
        else:
            base_time = str(now.hour) + "30"
        base_date = today
    queryParams = '?' + urlencode({ quote_plus('serviceKey') : serviceKeyDecoded, quote_plus('base_date') : base_date,
                                    quote_plus('base_time') : base_time, quote_plus('nx') : nx, quote_plus('ny') : ny,
                                    quote_plus('dataType') : 'json', quote_plus('numOfRows') : '60'}) #페이지로 안나누고 한번에 받아오기 위해 numOfRows=60으로 설정해주었다
                                    

    # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)
    res = requests.get(url + queryParams, verify=False) # verify=False이거 안 넣으면 에러남ㅜㅜ
    items = res.json().get('response').get('body').get('items') #데이터들 아이템에 저장
    #print(items)# 테스트

    weather_data = dict()

    for item in items['item']:
        # 기온
        if item['category'] == 'T1H':
            weather_data['tmp'] = item['fcstValue']
        # 습도
        if item['category'] == 'REH':
            weather_data['hum'] = item['fcstValue']
        # 하늘상태: 맑음(1) 구름많은(3) 흐림(4)
        if item['category'] == 'SKY':
            weather_data['sky'] = item['fcstValue']
        # 1시간 동안 강수량
        if item['category'] == 'RN1':
            weather_data['rain'] = item['fcstValue']

    print("response: "+input+'의 날씨 정보 ')
    print("===>",weather_data)
    return str(weather_data)

cli_socks = []             #client list
cli_msg = []               #client들이 보내는 메세지

class Client:
    def __init__(self,sock):
        self.sock = sock
        self.done = False
        self.rcvd_th = None

    def go(self):
        self.rcvd_th = threading.Thread(target=self.recv_and_send)
        self.rcvd_th.start()
        self.rcvd_th.join()
        print('client closed')

    def recv_and_send(self):
        while True:
            recv_msg = self.sock.recv(2048).decode()
            if recv_msg == 'exit':
                print('클라이언트가 나갔습니다.')
                break
            else:
                send_msg = api(recv_msg)
                self.sock.send(send_msg.encode())
        cli_socks.remove(self.sock)
        self.sock.close()

def clientstart(*sock):
    cli_socks.append(sock[0])
    client = Client(sock[0])
    client.go()
    print('Client is done')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost',9999))
sock.listen(5)
sock.settimeout(5)

while True:
    try:
        try:
            cli_sock, _ = sock.accept()
        except socket.timeout:
            pass
    except KeyboardInterrupt:
        break

    th = threading.Thread(target=clientstart,args=(cli_sock,))
    th.start()

sock.close()



