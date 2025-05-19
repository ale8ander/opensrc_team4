import cv2
import mediapipe as mp
import numpy as np
import time
import pyautogui
from collections import deque

from recognizer import SwipeRecognizer, classify_hand_pose
from emoji import emoji_cache, overlay_png


def detect_scroll(trajectory, threshold=50):
    if len(trajectory) < 5:
        return None
    dy = trajectory[-1][1] - trajectory[0][1]
    if abs(dy) > threshold:
        return "Scroll Down" if dy > 0 else "Scroll Up"
    return None


def track():
    # MediaPipe 초기화
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_drawing = mp.solutions.drawing_utils

    # 카메라 설정 및 준비
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Hand Gesture Tracking", cv2.WINDOW_NORMAL)

    trajectory = deque(maxlen=10)
    swipe_recognizer = SwipeRecognizer()

    finger_tip_ids = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
    ]

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        gesture = None

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                h, w, _ = frame.shape
                center = (
                    int(np.mean([lm.x * w for lm in hand_landmarks.landmark])),
                    int(np.mean([lm.y * h for lm in hand_landmarks.landmark]))
                )
                trajectory.append(center)

                for i in range(1, len(trajectory)):
                    cv2.line(frame, trajectory[i - 1], trajectory[i], (255, 0, 0), 2)

                tip_xs = [hand_landmarks.landmark[i].x for i in finger_tip_ids]
                swipe_gesture = swipe_recognizer.detect(tip_xs)
                hand_pose = classify_hand_pose(hand_landmarks.landmark)
                scroll_gesture = detect_scroll(trajectory)

                # 손 모양 우선, 없으면 스크롤, 없으면 스와이프
                gesture = hand_pose or scroll_gesture or swipe_gesture

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            gesture = "No Hands"

        # 동작 실행 처리
        if gesture == "Swipe Right":
            pyautogui.hotkey('alt', 'tab')
        elif gesture == "Swipe Left":
            pyautogui.hotkey('alt', 'shift', 'tab')
        elif gesture == "Scroll Up":
            pyautogui.scroll(300)
        elif gesture == "Scroll Down":
            pyautogui.scroll(-300)
        elif gesture == "Fist":
            pyautogui.hotkey('command', 'w')
        elif gesture == "Victory":
            pyautogui.hotkey('command', '[')

        # 화면 출력 처리
        if gesture:
            cv2.putText(frame, gesture, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            frame = overlay_png(frame, gesture, 300, 150)

            cooldown = swipe_recognizer.get_cooldown_remaining()
            cooldown_text = f"Cooldown: {cooldown:.1f}s" if cooldown > 0 else "Ready for swipe"
            cv2.putText(frame, cooldown_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        cv2.imshow("Hand Gesture Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("Hand Gesture Tracking", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    track()
