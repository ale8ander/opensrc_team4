import socket
import json

from flutter_connect import send_gesture_to_flutter

# 스와이프 제스처 추적용
last_swipe = None

def start_handler():
    global last_swipe

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 9999))
        s.listen()
        print("gesture_handler is running...")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()

                try:
                    payload = json.loads(data)
                    gesture = payload.get("gesture", "None")
                    is_swipe = payload.get("is_swipe", False)
                except Exception as e:
                    # 기존 형식일 경우 (JSON 아님)
                    gesture = data
                    is_swipe = "Swipe" in gesture

                print(f"[전체 제스처] {gesture}")
                if is_swipe:
                    last_swipe = gesture
                    print(f"[스와이프 제스처] {last_swipe}")

                send_gesture_to_flutter(gesture)

if __name__ == "__main__":
    start_handler()
