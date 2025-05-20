import requests

FLUTTER_SERVER_URL = "http://localhost:5000/gesture"

def send_gesture_to_flutter(gesture: str):
    try:
        response = requests.post(
            FLUTTER_SERVER_URL,
            json={"gesture": gesture},
            timeout=2
        )
        if response.status_code == 200:
            print(f"'{gesture}' 전송 성공")
        else:
            print(f"[!] '{gesture}' 전송 실패 - 상태코드: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[X] 전송 오류 발생: {e}")
