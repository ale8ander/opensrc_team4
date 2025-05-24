import cv2
import json
import mediapipe as mp
import numpy as np
import time
import platform
import pyautogui
import socket
from collections import deque

from recognizer import SwipeRecognizer
from emoji import emoji_cache, overlay_png


'''
- 3초 지연 기능 수정
- 사용자가 필요할 때만 킬 수 있게끔 GUI를 구성

- 전체 리팩토링
- 이후 모듈화
- README 수정
- OS 판단 => 제대로 동작하는지 확인 필요: completed 
+ mac일 경우 권한설정 먼저 바꿔줘야함
'''

MAX_TRAJECTORY_LENGTH = 20 
GESTURE_HOLD_DURATION = 3

def classify_gesture(landmarks, trajectory):
    def is_extended(tip, pip):
        return landmarks[tip].y < landmarks[pip].y

    fingers = {
        'index': (8, 6),
        'middle': (12, 10),
        'ring': (16, 14),
        'pinky': (20, 18)
    }

    extended_fingers = [name for name, (tip, pip) in fingers.items() if is_extended(tip, pip)]

    thumb_extended = landmarks[4].x > landmarks[3].x
    finger_count = len(extended_fingers)

    # ----- 손 모양 기반 -----
    if finger_count == 0:
        return "Fist" # 뒤로가기
    # elif finger_count >= 4:
    #    gesture = "Open Hand"
    elif 'index' in extended_fingers and 'middle' in extended_fingers and 'ring' not in extended_fingers:
        gesture = "Victory" # 창 닫기
    # elif 'ring' in extended_fingers and 'pinky' in extended_fingers and 'index' not in extended_fingers:
    #    gesture = "Arrow Left"   
    # elif is_x_sign(landmarks):
    #   gesture = "X Sign"
    else:
        gesture = None

    # 이동 기반 
    if len(trajectory) >= 5:
        dx = trajectory[-1][0] - trajectory[0][0]
        dy = trajectory[-1][1] - trajectory[0][1]
        if abs(dx) > 80 and abs(dx) > abs(dy):
            return "Swipe Right" if dx > 0 else "Swipe Left"
        elif abs(dy) > 80 and abs(dy) > abs(dx):
            return "Scroll Down" if dy > 0 else "Scroll Up"

    return gesture

'''
def is_x_sign(landmarks):
    # 손가락 두 개가 교차되었는지 간단한 조건 (index 중간 좌표와 middle이 가까움)
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    distance = abs(index_tip.x - middle_tip.x)
    return distance < 0.03 and index_tip.y < landmarks[6].y and middle_tip.y < landmarks[10].y
'''


def detect_scroll(trajectory, threshold=50):
    if len(trajectory) < 5:
        return None
    dy = trajectory[-1][1] - trajectory[0][1]
    if abs(dy) > threshold:
        return "Scroll Down" if dy > 0 else "Scroll Up"
    return None
# OS 확인
def check_OS():
    os_name = platform.system()
    print(os_name)
    if os_name == "Windows":
        return 1
    elif os_name == "Darwin":  # MacOS
        return 0
    else:
        return -1  # Linux 또는 기타

# OS예 따른 gesture 선택
def execute_gesture_action(gesture, os_name):
    if gesture == "Swipe Right":
        pyautogui.hotkey('alt', 'tab') if os_name else pyautogui.hotkey('command', 'tab')
    elif gesture == "Swipe Left":
        pyautogui.hotkey('alt', 'shift', 'tab') if os_name else pyautogui.hotkey('command', 'shift', 'tab')
    elif gesture == "Scroll Up":
        pyautogui.scroll(300)
    elif gesture == "Scroll Down":
        pyautogui.scroll(-300)
    elif gesture == "Victory": # x-sign 대체
        pyautogui.hotkey('alt', 'f4') if os_name else pyautogui.hotkey('command', 'w')
    elif gesture == "Fist": # Arrow 대체
        pyautogui.hotkey('alt', 'left') if os_name else pyautogui.hotkey('command', '[')

# guideline 출력
def show_guidline(frame):
    frame_width = frame.shape[1]

    instructions = [
        "Fist: Go Back",
        "Victory: Close Tab",
        "Swipe Right: Tab Change ",
        "Swipe Left: Tab Change",
        "Scroll Down: ",
        "Scroll Up: "
    ]
    for i, line in enumerate(instructions):
        # 글자 크기 측정 (폰트, 스케일, 두께)
        text_size, _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        text_width = text_size[0]
            
        x = frame_width - text_width - 50  # 우측 정렬 
        y = 30 + i * 30 
            
        cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX,  1.2, (0, 0, 255), 2)

# 제스처 전송 함수 (소켓 클라이언트)
def send_to_handler(gesture):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 9999))  # handler 서버 주소/포트
            s.sendall(gesture.encode())
    except:
        pass  # handler가 안 켜졌을 경우 무시


def track():
    os_name = check_OS()
    
    # gesture 시간 조절 관련 변수
    last_gesture = None
    gesture_timestamp = 0
    
    # MediaPipe 초기화
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils

    # 실행 시작
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Hand Gesture Tracking", cv2.WINDOW_NORMAL)

    trajectory = deque(maxlen=10)
    swipe_recognizer = SwipeRecognizer()
    last_sent = None
    last_time = 0
    send_interval = 0.5  # 0.5초 간격 제한

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        gesture = None
        swipe_text = ""

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                h, w, _ = frame.shape
                
                # 중심 좌표 계산
                cx = int(np.mean([lm.x * w for lm in hand_landmarks.landmark]))
                cy = int(np.mean([lm.y * h for lm in hand_landmarks.landmark]))
                trajectory.append((cx, cy))
                
                # trajectory 길이 제한
                if len(trajectory) > MAX_TRAJECTORY_LENGTH:
                    trajectory.pop(0)
                
                # 궤적 그리기
                for i in range(1, len(trajectory)):
                    cv2.line(frame, trajectory[i - 1], trajectory[i], (255, 0, 0), 2)

                # 제스처 분류
                gesture_candidate = classify_gesture(hand_landmarks.landmark, trajectory)

                if gesture_candidate and gesture_candidate != last_gesture:
                    last_gesture = gesture_candidate
                    gesture_timestamp = time.time()  # 시간 기록

                # 현재 표시할 제스처: GESTURE_HOLD_DURATION => 이 부분 미동작
                if time.time() - gesture_timestamp < GESTURE_HOLD_DURATION:
                    gesture = last_gesture
                else:
                    gesture = "No Gesture"
                    
                if gesture is not None and "Swipe" in gesture:
                    swipe_text = gesture
                else:
                    swipe_text = ""

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                execute_gesture_action(gesture, os_name)

        now = time.time()

        # 일반 제스처 전송 (No Hands 제외)
        if gesture and gesture != "No Hands" and (now - last_time) > send_interval:
            payload = {
            "gesture": gesture,
            "is_swipe": False
            }
            send_to_handler(json.dumps(payload))
            last_time = now  # 공통 쿨다운 타이머

        # 스와이프 제스처는 따로 전송
        if swipe_text and (swipe_text != last_sent or (now - last_time) > send_interval):
            swipe_payload = {
                "gesture": swipe_text,
                "is_swipe": True
            }
            send_to_handler(json.dumps(swipe_payload))
            last_sent = swipe_text  # 마지막 전송된 스와이프 갱신

        # 화면 출력 처리
        if gesture:
            cv2.putText(frame, gesture, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            frame = overlay_png(frame, gesture, 300, 150)

            if swipe_text:
                cv2.putText(frame, swipe_text, (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            cooldown_remaining = swipe_recognizer.get_cooldown_remaining()
            cooldown_msg = f"Cooldown: {cooldown_remaining:.1f}s" if cooldown_remaining > 0 else "Ready for swipe"
            cv2.putText(frame, cooldown_msg, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        
        show_guidline(frame)
        
        cv2.imshow("Hand Gesture Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("Hand Gesture Tracking", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    track()
