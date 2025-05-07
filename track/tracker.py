import cv2
import mediapipe as mp
import numpy as np
from collections import deque

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# 손 이동 궤적 저장 (최근 10프레임)
trajectory = deque(maxlen=10)

# 웹캠
cap = cv2.VideoCapture(0)

def get_hand_center(landmarks, shape):
    h, w, _ = shape
    cx = int(np.mean([lm.x * w for lm in landmarks]))
    cy = int(np.mean([lm.y * h for lm in landmarks]))
    return (cx, cy)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # 손 중심 좌표 계산
            center = get_hand_center(hand_landmarks.landmark, frame.shape)
            trajectory.append(center)

            # 궤적 그리기
            for i in range(1, len(trajectory)):
                cv2.line(frame, trajectory[i - 1], trajectory[i], (255, 0, 0), 2)

            # 제스처 판단
            if len(trajectory) >= 5:
                dx = trajectory[-1][0] - trajectory[0][0]
                if abs(dx) > 80:  # 이동 거리 기준
                    if dx > 0:
                        gesture = "Swipe Right"
                    else:
                        gesture = "Swipe Left"
                    cv2.putText(frame, gesture, (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Gesture Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()