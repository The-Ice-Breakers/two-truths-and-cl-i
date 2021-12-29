import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostbyname('localhost'),8000))

while True:
    msg = s.recv(1024)
    print(msg.decode('utf-8'))
    #print('listening')

# myhostname = socket.gethostname()
# print(myhostname)

# ip = socket.gethostbyname("localhost")
# print(ip)