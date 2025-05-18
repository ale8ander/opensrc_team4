import cv2
import mediapipe as mp
import numpy as np
import os
import time
from collections import deque

# 스와이프 인식 클래스
class SwipeRecognizer:
    def __init__(self, cooldown=2.0, movement_threshold=0.1, stability_threshold=0.01):
        self.cooldown = cooldown
        self.movement_threshold = movement_threshold
        self.stability_threshold = stability_threshold
        self.prev_avg_x = None
        self.last_swipe_time = 0

    def detect(self, tip_xs):
        current_time = time.time()
        if len(tip_xs) != 5:
            return None

        avg_x = sum(tip_xs) / 5
        gesture = None
        dx = 0

        if self.prev_avg_x is not None:
            dx = avg_x - self.prev_avg_x
            hand_stable = abs(dx) < self.stability_threshold
            cooldown_remaining = self.cooldown - (current_time - self.last_swipe_time)

            if cooldown_remaining <= 0 and not hand_stable:
                if dx > self.movement_threshold:
                    gesture = "Swipe Left"
                    self.last_swipe_time = current_time
                elif dx < -self.movement_threshold:
                    gesture = "Swipe Right"
                    self.last_swipe_time = current_time

        self.prev_avg_x = avg_x
        return gesture

# MediaPipe 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# 이모지 설정 
emoji_img_paths = {
    "Swipe Right": "emojis/swipe_right.png",
    "Swipe Left": "emojis/swipe_left.png",
    "Fist": "emojis/fist.png",
    "Open Hand": "emojis/open_hand.png",
    "Victory": "emojis/victory.png"
}

# 손 모양 제스처 분류 함수 
def classify_hand_pose(landmarks):
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    extended = 0
    for tip, pip in zip(finger_tips, finger_pips):
        if landmarks[tip].y < landmarks[pip].y:
            extended += 1

    thumb_extended = landmarks[4].x > landmarks[3].x

    if extended == 0:
        return "Fist"
    elif extended >= 4:
        return "Open Hand"
    elif landmarks[8].y < landmarks[6].y and landmarks[12].y < landmarks[10].y \
         and landmarks[16].y > landmarks[14].y and landmarks[20].y > landmarks[18].y:
        return "Victory"
    else:
        return None

# PNG 이미지 오버레이 함수
def overlay_png(background, overlay, x, y):
    h, w = overlay.shape[:2]
    if y + h > background.shape[0] or x + w > background.shape[1]:
        return background

    alpha_overlay = overlay[:, :, 3] / 255.0
    alpha_background = 1.0 - alpha_overlay

    for c in range(0, 3):
        background[y:y+h, x:x+w, c] = (
            alpha_overlay * overlay[:, :, c] + alpha_background * background[y:y+h, x:x+w, c]
        )
    return background

# 실행 시작
cap = cv2.VideoCapture(0)
cv2.namedWindow("Hand Gesture Tracking", cv2.WINDOW_NORMAL)

trajectory = deque(maxlen=10)
swipe_recognizer = SwipeRecognizer()

finger_tip_ids = [
    mp_hands.HandLandmark.THUMB_TIP,
    mp_hands.HandLandmark.INDEX_FINGER_TIP,
    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
    mp_hands.HandLandmark.RING_FINGER_TIP,
    mp_hands.HandLandmark.PINKY_TIP
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
            # 중심 궤적 저장
            h, w, _ = frame.shape
            cx = int(np.mean([lm.x * w for lm in hand_landmarks.landmark]))
            cy = int(np.mean([lm.y * h for lm in hand_landmarks.landmark]))
            trajectory.append((cx, cy))

            # 궤적 시각화
            for i in range(1, len(trajectory)):
                cv2.line(frame, trajectory[i - 1], trajectory[i], (255, 0, 0), 2)

            # 손가락 tip 좌표 수집
            tip_xs = [hand_landmarks.landmark[i].x for i in finger_tip_ids]

            # 스와이프 제스처 판단
            swipe_gesture = swipe_recognizer.detect(tip_xs)

            # 손 모양 판단
            hand_pose = classify_hand_pose(hand_landmarks.landmark)

            # 제스처 결정 (손 모양이 우선)
            gesture = hand_pose if hand_pose else swipe_gesture

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # 화면에 표시
    if gesture:
        cv2.putText(frame, gesture, (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
        emoji_path = emoji_img_paths.get(gesture)
        if emoji_path and os.path.exists(emoji_path):
            emoji_img = cv2.imread(emoji_path, cv2.IMREAD_UNCHANGED)
            if emoji_img is not None and emoji_img.shape[2] == 4:
                frame = overlay_png(frame, emoji_img, 300, 150)

    cv2.imshow("Hand Gesture Tracking", frame)

    if cv2.waitKey(33) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty("Hand Gesture Tracking", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()