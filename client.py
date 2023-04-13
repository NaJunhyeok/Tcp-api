import socket
import threading
import time
import ast

SERVER_IP = 'localhost'
SERVER_PORT = 9999
location_list = ['서울','부산','인천','대구','대전','광주','울산','제주','청주', '충주']
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))
print('------ 연결 중 ------')
sock.settimeout(5)
time.sleep(3)

while True:
    print("위치 리스트 : 서울, 부산, 인천, 대구, 대전, 광주, 울산, 제주, 청주, 충주 ")
    msg = input('위치 입력 : ')
    if msg == 'exit':
        print('종료합니다.')
        break
    if msg not in location_list:
        print('잘못된 위치 정보입니다. 다시 입력해주세요')
        print("위치 리스트 : 서울, 부산, 인천, 대구, 대전, 광주, 울산, 제주, 청주, 충주 ")
        msg = input('위치 입력 : ')
        sock.send(msg.encode())
    else:
        sock.send(msg.encode())

    return_msg = sock.recv(2048).decode()
    return_to_dict = ast.literal_eval(return_msg)
    rain = return_to_dict['rain']
    sky_present = ''

    if return_to_dict['sky'] == '1':
        sky_present = '맑음'
    elif return_to_dict['sky'] == '3':
        sky_present = '구름 많음'
    elif return_to_dict['sky'] == '4':
        sky_present = '흐림'

    tmp = return_to_dict['tmp']
    hum = return_to_dict['hum']

    print(msg+' 날씨 정보  => 강수량 : '+rain+'/ 하늘 상태 : '+sky_present+'/ 기온 : '+tmp+'도'+'/ 습도 : '+hum+'\n')

sock.close()

