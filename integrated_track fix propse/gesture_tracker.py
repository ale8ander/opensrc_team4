import cv2
import mediapipe as mp
import numpy as np
import os
import time
from collections import deque

from recognizer import SwipeRecognizer, classify_hand_pose
from emoji import emoji_cache, overlay_png


def track():
    # MediaPipe 초기화
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils

    # 실행 시작
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Hand Gesture Tracking", cv2.WINDOW_NORMAL)

    trajectory = deque(maxlen=10)
    swipe_recognizer = SwipeRecognizer()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        gesture = None
        swipe_text = ""  # 스와이프 방향 텍스트 초기화

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # 중심 궤적 저장
                h, w, _ = frame.shape
                cx = int(np.mean([lm.x * w for lm in hand_landmarks.landmark]))
                cy = int(np.mean([lm.y * h for lm in hand_landmarks.landmark]))
                trajectory.append((cx, cy))

                # 궤적 시각화
                for i in range(1, len(trajectory)):
                    cv2.line(frame, trajectory[i - 1], trajectory[i], (255, 0, 0), 2)

                # 손 모양 판단
                hand_pose = classify_hand_pose(hand_landmarks.landmark)

                # Open Hand일 때만 스와이프 판단
                swipe_gesture = None
                if hand_pose == "Open Hand":
                    swipe_gesture = swipe_recognizer.detect(cx)

                # 손 모양이 우선, 없으면 스와이프
                gesture = hand_pose if hand_pose else swipe_gesture

                # 손이 펼쳐졌고 스와이프 방향이 감지되면 출력용 변수 설정
                if hand_pose == "Open Hand" and swipe_gesture:
                    swipe_text = swipe_gesture

                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )
        else:
            gesture = "No Hands"

        # 화면에 제스처, 스와이프 방향, 쿨다운 표시
        if gesture:
            # 손 모양 또는 스와이프 표시
            cv2.putText(
                frame, gesture, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2
            )
            frame = overlay_png(frame, gesture, 300, 150)

            # 스와이프 방향 표시 (손 모양이 Open Hand인 경우만)
            if swipe_text:
                cv2.putText(
                    frame,
                    swipe_text,
                    (50, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2,
                )

            # 쿨다운 표시
            cooldown_remaining = swipe_recognizer.get_cooldown_remaining()
            cooldown_msg = (
                f"Cooldown: {cooldown_remaining:.1f}s"
                if cooldown_remaining > 0
                else "Ready for swipe"
            )
            cv2.putText(
                frame,
                cooldown_msg,
                (50, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 255),
                2,
            )

        cv2.imshow("Hand Gesture Tracking", frame)

        # 종료 조건
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("Hand Gesture Tracking", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    track()
