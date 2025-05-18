import os
import cv2
import mediapipe as mp
import numpy as np
from collections import deque

# MediaPipe 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# 손 궤적 저장
trajectory = deque(maxlen=10)

# 이모지 매핑
emoji_map = {
    "Swipe Right": "👉",
    "Swipe Left": "👈",
    "Fist": "✊",
    "Open Hand": "🖐️",
    "Victory": "✌️"
}

emoji_img_paths = {
    "Swipe Right": "emojis/swipe_right.png",
    "Swipe Left": "emojis/swipe_left.png",
    "Fist": "emojis/fist.png",
    "Open Hand": "emojis/open_hand.png",
    "Victory": "emojis/victory.png"
}

gesture = None

# 웹캠 연결
cap = cv2.VideoCapture(0)
cv2.namedWindow("Hand Gesture Tracking", cv2.WINDOW_NORMAL)  # 창 닫기 활성화

# 손 중심 좌표 구하는 함수
def get_hand_center(landmarks, shape):
    h, w, _ = shape
    cx = int(np.mean([lm.x * w for lm in landmarks]))
    cy = int(np.mean([lm.y * h for lm in landmarks]))
    return (cx, cy)

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

def overlay_png(background, overlay, x, y):
    h, w = overlay.shape[:2]
    if y + h > background.shape[0] or x + w > background.shape[1]:
        return background

    alpha_overlay = overlay[:, :, 3] / 255.0
    alpha_background = 1.0 - alpha_overlay

    for c in range(0, 3):
        background[y:y+h, x:x+w, c] = (alpha_overlay * overlay[:, :, c] +
                                       alpha_background * background[y:y+h, x:x+w, c])
    return background

# 메인 루프
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture = None  # 초기화

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # 중심 궤적 저장
            center = get_hand_center(hand_landmarks.landmark, frame.shape)
            trajectory.append(center)

            # 궤적 시각화
            for i in range(1, len(trajectory)):
                cv2.line(frame, trajectory[i - 1], trajectory[i], (255, 0, 0), 2)

            # 스와이프 판단
            if len(trajectory) >= 5:
                dx = trajectory[-1][0] - trajectory[0][0]
                if abs(dx) > 80:
                    gesture = "Swipe Right" if dx > 0 else "Swipe Left"

            # 손 모양 제스처 인식
            pose = classify_hand_pose(hand_landmarks.landmark)
            if pose:
                gesture = pose  # 손 모양이 우선순위

            # 랜드마크 그리기
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # 화면에 제스처 + 이모지 표시
    if gesture:
        cv2.putText(frame, gesture, (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
        emoji_path = emoji_img_paths.get(gesture)
        if emoji_path and os.path.exists(emoji_path):
            emoji_img = cv2.imread(emoji_path, cv2.IMREAD_UNCHANGED)
            if emoji_img is not None and emoji_img.shape[2] == 4:
                frame = overlay_png(frame, emoji_img, 300, 150)

    cv2.imshow("Hand Gesture Tracking", frame)

    # 종료 조건
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty("Hand Gesture Tracking", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()