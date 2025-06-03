import cv2
import json
import mediapipe as mp
import time
import platform
from collections import deque

from gesture_core import (
    instructions,
    update_trajectory,
    draw_trajectory_on_frame,
    process_hand_gesture
)
from my_gui import show_guidline
from recognizer import SwipeRecognizer
from emoji import overlay_png
#from my_socket import send_to_handler

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


#def send_gesture_via_socket(gesture, is_swipe, last_sent, last_time):
    """
    Send the gesture result via socket if conditions are met.

    Args:
        gesture (str): The name of the gesture to send.
        is_swipe (bool): Whether the gesture is a swipe gesture.
        last_sent (str): The last gesture that was sent.
        last_time (float): Timestamp of the last socket transmission.

    Returns:
        tuple: (updated last_sent, updated last_time)

    제스처가 전송 조건을 만족하면 소켓으로 전송하고, 전송 이력을 업데이트합니다.

    반환:
        tuple: (전송한 제스처, 전송 시각)
    """
#    now = time.time()
#    if gesture and gesture != "No Hands" and (now - last_time) > SEND_INTERVAL:
#        payload = {
#            "gesture": gesture,
#            "is_swipe": is_swipe
#        }
#        send_to_handler(json.dumps(payload))
#        return gesture, now
#    return last_sent, last_time




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
        if not ret: #프레임 읽기 실패 시 종료
            break
	
	# 영상 좌우 반전 및 RGB로 색상 변환 (MediaPipe 처리를 위해)
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
            	# 손의 중심 좌표 계산 및 궤적 리스트에 추가
                update_trajectory(trajectory, hand_landmarks.landmark, frame.shape)
                 # 이동 경로 시각화
                draw_trajectory_on_frame(frame, trajectory)
		
		# 현재 손 제스처 분석 및 실행
                gesture, gesture_timestamp = process_hand_gesture(
                    hand_landmarks.landmark,
                    trajectory,
                    gesture_timestamp,
                    GESTURE_HOLD_DURATION,
                    os_name
                )
		
		# 인식된 제스처 기록 (마지막 제스처 업데이트)
                if gesture:
                    last_gesture = gesture
                    
		# 손 랜드마크 연결선 시각화
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # 소켓 전송 (일반 제스처)
        #last_sent, last_time = send_gesture_via_socket(gesture, False, last_sent, last_time)

        # 소켓 전송 (스와이프 제스처)
        #if swipe_text:
        #    last_sent, last_time = send_gesture_via_socket(swipe_text, True, last_sent, last_time)

    
        # 결과 화면 출력
        if gesture:
            frame = overlay_png(frame, gesture, 300, 150)
            cv2.putText(frame, gesture, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            description = instructions.get(gesture, "")
            cv2.putText(frame, description, (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    
        cooldown_remaining = GESTURE_HOLD_DURATION - (time.time() - gesture_timestamp)
        if cooldown_remaining > 0:
            cooldown_timer_text = f"Cooldown: {cooldown_remaining:.1f}s"
            cv2.putText(frame, cooldown_timer_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

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
