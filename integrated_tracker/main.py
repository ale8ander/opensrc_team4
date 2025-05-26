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

MAX_TRAJECTORY_LENGTH = 20
GESTURE_HOLD_DURATION = 3
SEND_INTERVAL = 0.5

'''
- 3초 지연 기능 수정 => 타이머 기능? cooldown?

- 전체 리팩토링
- 이후 모듈화
- README 수정
- OS 판단 => 제대로 동작하는지 확인 필요: completed 
- 사용자가 필요할 때만 킬 수 있게끔 GUI를 구성
+ mac일 경우 권한설정 먼저 바꿔줘야함
'''

# 손가락 펼쳐졌는지 판단
def is_extended(tip, pip, landmarks):
    return landmarks[tip].y < landmarks[pip].y

# 손 모양으로 제스처 분류
# 원래 scroll, swipe 기능까지 구현했으나, mediapipe 인식 한계 상 가위, 바위, 보로 한정함
def classify_gesture(landmarks, trajectory):
    fingers = {
        'index': (8, 6),
        'middle': (12, 10),
        'ring': (16, 14),
        'pinky': (20, 18)
    }

    extended_fingers = [name for name, (tip, pip) in fingers.items() if is_extended(tip, pip, landmarks)]
    thumb_extended = landmarks[4].x > landmarks[3].x
    finger_count = len(extended_fingers)

    if finger_count == 0:
        return "Fist"
    elif finger_count >= 4 and thumb_extended:
        return "Open Hand"
    elif 'index' in extended_fingers and 'middle' in extended_fingers and 'ring' not in extended_fingers:
        return "Victory"

    '''
    if len(trajectory) >= 5:
        dx = trajectory[-1][0] - trajectory[0][0]
        dy = trajectory[-1][1] - trajectory[0][1]
        if abs(dx) > 80 and abs(dx) > abs(dy):
             return "Swipe Right" if dx > 0 else "Swipe Left"
        if abs(dy) > 80 and abs(dy) > abs(dx):
            return "Scroll Down" if dy > 0 else "Scroll Up"
    '''
    
    return None


# 운영체제 확인
def check_OS():
    os_name = platform.system()
    return 1 if os_name == "Windows" else 0 if os_name == "Darwin" else -1

# 제스처에 따른 키보드 동작
def execute_gesture_action(gesture, os_name):
    keymap = {
        # "Swipe Right": ('alt', 'tab') if os_name else ('command', 'tab'),
        # "Swipe Left": ('alt', 'shift', 'tab') if os_name else ('command', 'shift', 'tab'),
        # "Scroll Up": 300,
        # "Scroll Down": -300,
        "Victory": ('alt', 'f4') if os_name else ('command', 'w'),
        "Fist": ('ctrl', 'r') if os_name else ('command', 'r'), 
        "Open Hand": ('alt', 'left') if os_name else ('command', '['),
    }

    if gesture in keymap:
        pyautogui.hotkey(*keymap[gesture])
    # elif "Scroll" in gesture: # 이거 로직 나중에 수정 필요
    #    pyautogui.scroll(keymap[gesture])

# 화면 우측 가이드 라인 제공
def show_guidline(frame):
    frame_width = frame.shape[1]
    instructions = [
        "Victory: Close Tab",
        "Fist: F5",
        "Open Hand: Go Back"
        # "Swipe Right: Tab Change ",
        # "Swipe Left: Tab Change",
        # "Scroll Down:",
        # "Scroll Up:"
    ]
    for i, line in enumerate(instructions):
        text_size, _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        text_width = text_size[0]
        x = frame_width - text_width - 50
        y = 30 + i * 30
        cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)

# 소켓 전송
def send_to_handler(gesture):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 9999))
            s.sendall(gesture.encode())
    except:
        pass

# 메인 루프
def track():
    # OS 확인
    os_name = check_OS()
    
    # MediaPipe 및 카메라 초기화
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils

    # 웹캠 켜기
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Hand Gesture Tracking", cv2.WINDOW_NORMAL)

    # 제스처 인식 상태 초기화
    trajectory = deque(maxlen=MAX_TRAJECTORY_LENGTH) # 손 이동 궤적 저장용
    swipe_recognizer = SwipeRecognizer()
    last_sent = None
    last_time = 0
    last_gesture = None
    gesture_timestamp = 0
    cooldown_remaining = 0
    
    gesture = "Start"
    swipe_text = ""

    while cap.isOpened(): 
        ret, frame = cap.read()
        if not ret: # 프레임 읽기 실패 시 종료
            break
        # 영상 처리 및 손 인식
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            # 손이 인식된 경우
            for hand_landmarks in result.multi_hand_landmarks:
                # 1. 손 중심좌표 계산해서 trajectory에 저장
                h, w, _ = frame.shape
                cx = int(np.mean([lm.x * w for lm in hand_landmarks.landmark]))
                cy = int(np.mean([lm.y * h for lm in hand_landmarks.landmark]))
                trajectory.append((cx, cy))
                # 이동 경로 시각화
                for i in range(1, len(trajectory)):
                    cv2.line(frame, trajectory[i - 1], trajectory[i], (255, 0, 0), 2)

                # 2. 제스처 판단 & 유지 조건
                gesture_candidate = classify_gesture(hand_landmarks.landmark, trajectory)

                # 3. 제스처가 인식된 후 3초 동안 새로운 제스처를 받지 않음
                cooldown_remaining = GESTURE_HOLD_DURATION - (time.time() - gesture_timestamp)
                if cooldown_remaining <= 0:
                    if gesture_candidate and gesture_candidate != last_gesture:
                        last_gesture = gesture_candidate
                        gesture = last_gesture
                        gesture_timestamp = time.time()
                        
                swipe_text = gesture if gesture and "Swipe" in gesture else ""

                # 4. 제스처에 따른 키보드 동작 실행
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                execute_gesture_action(gesture, os_name)

        # 소켓 전송
        now = time.time()
        if gesture and gesture != "No Hands" and (now - last_time) > SEND_INTERVAL:
            payload = {"gesture": gesture, "is_swipe": False}
            send_to_handler(json.dumps(payload))
            last_time = now

        if swipe_text and (swipe_text != last_sent or (now - last_time) > SEND_INTERVAL):
            swipe_payload = {"gesture": swipe_text, "is_swipe": True}
            send_to_handler(json.dumps(swipe_payload))
            last_sent = swipe_text
        
        # 결과 화면 출력
        if gesture:
            cv2.putText(frame, gesture, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)

        if cooldown_remaining > 0:
            cooldown_timer_text = f"Cooldown: {cooldown_remaining:.1f}s"
            cv2.putText(frame, cooldown_timer_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

            # frame = overlay_png(frame, gesture, 300, 150)
            # if swipe_text:
            #     cv2.putText(frame, swipe_text, (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            #cooldown_msg = f"Cooldown: {swipe_recognizer.get_cooldown_remaining():.1f}s" \
            #     if swipe_recognizer.get_cooldown_remaining() > 0 else "Ready for swipe"
            # cv2.putText(frame, cooldown_msg, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        # 가이드 라인 표시
        show_guidline(frame)
        cv2.imshow("Hand Gesture Tracking", frame)
        
        # 종료 처리
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("Hand Gesture Tracking", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    track()