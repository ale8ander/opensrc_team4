import cv2
import os
import mediapipe as mp
import time
import platform
from collections import deque

from gesture_core import (
    instructions,
    update_trajectory,
    draw_trajectory_on_frame,
    process_hand_gesture,
    update_fingertip_trajectory
)

from my_gui import (
    show_guidline,
    check_user_inactivity,
    draw_quit_button,
    show_intro_image
)

from recognizer import SwipeRecognizer
from emoji import (
    overlay_png,
    overlay_face_with_emoji
)
#from my_socket import send_to_handler

MAX_TRAJECTORY_LENGTH = 20
GESTURE_HOLD_DURATION = 3
SEND_INTERVAL = 0.5
USER_INACTIVITY_TIME = 10


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

    # macOS 권한 체크 경고 (권한 없을 경우만 출력)
    if os_name == 0:
        test_cam = cv2.VideoCapture(0)
        if not test_cam.isOpened():
            print("\n[Permission Warning]")
            print("웹캠 권한이 macOS에서 차단되어 있을 수 있습니다.")
            print("시스템 환경설정 > 보안 및 개인정보 보호 > 카메라에서 Python 또는 터미널 앱에 권한을 부여하세요.\n")
        test_cam.release()
    
    #intro show
    show_intro_image("../icon/start.jpg")
    
    # MediaPipe 및 카메라 초기화
    mp_hands = mp.solutions.hands
    hands = None
    cap = None

    try:
        hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        mp_drawing = mp.solutions.drawing_utils

        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.7)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("카메라를 열 수 없습니다.")
            return

        cv2.namedWindow("Hand Gesture Tracking", cv2.WINDOW_NORMAL)
        
        # 제스처 인식 상태 초기화
        trajectory = deque(maxlen=MAX_TRAJECTORY_LENGTH) # 손 이동 궤적 저장용
        swipe_recognizer = SwipeRecognizer()
        last_sent = None
        last_time = 0
        last_gesture = None
        gesture_timestamp = 0
        cooldown_remaining = 0
        is_pointing = False

        gesture = "Start"
        swipe_text = ""

        last_active = time.time()
        restart_flag = [False]
        exit_flag = [False]

        quit_box = None
        restart_box = None

        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                if quit_box:
                    x1, y1, x2, y2 = quit_box
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        exit_flag[0] = True
                if restart_box:
                    rx1, ry1, rx2, ry2 = restart_box
                    if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                        restart_flag[0] = True

        cv2.setMouseCallback("Hand Gesture Tracking", mouse_callback)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: #프레임 읽기 실패 시 종료
                break

            # 영상 좌우 반전 및 RGB로 색상 변환 (MediaPipe 처리를 위해)
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            face_results = face_detection.process(rgb)
            overlay_face_with_emoji(frame, face_results)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    # 이전 제스처가 포인팅이었는지 확인
                    was_pointing = is_pointing

                    # 현재 손 제스처 분석 및 실행
                    gesture, gesture_timestamp = process_hand_gesture(
                        hand_landmarks.landmark,
                        trajectory,
                        gesture_timestamp,
                        GESTURE_HOLD_DURATION,
                        os_name,
                        last_gesture
                    )

                    # 포인팅 상태 업데이트
                    is_pointing = (gesture == "Pointing")

                    # 포인팅 상태가 변경되면 궤적 초기화
                    if was_pointing != is_pointing:
                        trajectory.clear()

                    # 궤적 업데이트
                    if is_pointing:
                        update_fingertip_trajectory(trajectory, hand_landmarks.landmark, frame.shape)
                    else:
                        update_trajectory(trajectory, hand_landmarks.landmark, frame.shape)
                    
                    # 이동 경로 시각화
                    draw_trajectory_on_frame(frame, trajectory)

                    # 인식된 제스처 기록 (마지막 제스처 업데이트)
                    if gesture:
                        last_gesture = gesture
                        last_active = time.time()

                    # 손 랜드마크 연결선 시각화
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            else:
                # 손이 감지되지 않으면 상태 초기화
                trajectory.clear()
                is_pointing = False
                gesture = None

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
                total_bar_length = 300
                filled_length = int((cooldown_remaining / GESTURE_HOLD_DURATION) * total_bar_length)

                bar_x, bar_y = 50, 230
                bar_height = 20

                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + total_bar_length, bar_y + bar_height), (100, 100, 100), -1)
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled_length, bar_y + bar_height), (255, 255, 0), -1)
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + total_bar_length, bar_y + bar_height), (255, 255, 255), 2)

            show_guidline(frame)
                    
            # 'Quit' 버튼 그리기
            quit_box = draw_quit_button(frame)

            # Check user inactivity and show Restart/Quit if needed
            restart_box, quit_box_inactive, inactive_duration = check_user_inactivity(frame, last_active, USER_INACTIVITY_TIME)
            if quit_box_inactive:
                # Turn off webcam frame (blackout)
                frame[:] = 0
                # Draw restart and quit buttons on black background
                restart_box, quit_box, _ = check_user_inactivity(frame, last_active, USER_INACTIVITY_TIME)

            cv2.imshow("Hand Gesture Tracking", frame)

            if exit_flag[0]:
                break
            if restart_flag[0]:
                cap.release()
                cv2.destroyAllWindows()
                track()
                return

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            if cv2.getWindowProperty("Hand Gesture Tracking", cv2.WND_PROP_VISIBLE) < 1:
                break

    finally:
        # 자원 해제
        if hands:
            hands.close()  # MediaPipe 리소스 해제
        if cap:
            cap.release()  # 카메라 해제

        cv2.destroyAllWindows()  # 모든 창 닫기



if __name__ == "__main__":
    track()
