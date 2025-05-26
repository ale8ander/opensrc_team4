import socket

# 소켓 전송
def send_to_handler(gesture):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 9999))
            s.sendall(gesture.encode())
    except:
        pass