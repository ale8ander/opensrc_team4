import cv2
import json
import mediapipe as mp
import numpy as np
import time
import platform
from collections import deque

from gesture_core import (
    instructions,
    classify_gesture,
    execute_gesture_action
)
from my_gui import show_guidline
from recognizer import SwipeRecognizer
from emoji import overlay_png
from my_socket import send_to_handler

MAX_TRAJECTORY_LENGTH = 20
GESTURE_HOLD_DURATION = 3
SEND_INTERVAL = 0.5

'''
<issue>
- 종료 조건
- OS 판단 => 제대로 동작하는지 확인 필요: completed 
- 사용자가 필요할 때만 킬 수 있게끔 GUI를 구성
- OpenHand 인식률 떨어짐

+ mac일 경우 권한설정 먼저 바꿔줘야함
'''

# 운영체제 확인
def check_OS():
    """
    Check the operating system type.

    Returns:
        int: 1 for Windows, 0 for macOS, -1 for others.

    현재 운영체제(OS) 종류를 확인합니다.

    반환:
        int: Windows는 1, macOS는 0, 기타는 -1 반환
    """
    os_name = platform.system()
    return 1 if os_name == "Windows" else 0 if os_name == "Darwin" else -1

# 메인 루프
def track():
    """
    Main loop to capture webcam input and recognize hand gestures.

    Initializes the camera, processes hand landmarks with MediaPipe,
    recognizes gestures, displays results, and sends socket messages.

    웹캠에서 입력을 받아 손 제스처를 인식하는 메인 루프입니다.

    카메라를 초기화하고, MediaPipe로 손을 인식하여,
    제스처를 분석하고 결과를 표시하며 소켓으로 메시지를 전송합니다.
    """
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
                    if gesture_candidate:
                        last_gesture = gesture_candidate
                        gesture = last_gesture
                        gesture_timestamp = time.time()
                        # 4. 제스처에 따른 키보드 동작 실행
                        execute_gesture_action(gesture, os_name)
                        
                # swipe_text = gesture if gesture and "Swipe" in gesture else ""

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                

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
            frame = overlay_png(frame, gesture, 300, 150)
            cv2.putText(frame, gesture, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            description = instructions.get(gesture, "")
            cv2.putText(frame, description, (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        
        if cooldown_remaining > 0:
            cooldown_timer_text = f"Cooldown: {cooldown_remaining:.1f}s"
            cv2.putText(frame, cooldown_timer_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
            
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