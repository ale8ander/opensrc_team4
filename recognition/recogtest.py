import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

prev_avg_x = None
gesture = None
last_swipe_time = 0
gesture_display_time = 1.5
cooldown = 2.0
stable_threshold = 0.01

finger_tip_ids = [
    mp_hands.HandLandmark.THUMB_TIP,
    mp_hands.HandLandmark.INDEX_FINGER_TIP,
    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
    mp_hands.HandLandmark.RING_FINGER_TIP,
    mp_hands.HandLandmark.PINKY_TIP
]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    current_time = time.time()

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            # 손가락 끝 x 좌표 평균 계산
            tip_xs = [handLms.landmark[i].x for i in finger_tip_ids]
            avg_x = sum(tip_xs) / len(tip_xs)

            if prev_avg_x is not None:
                dx = avg_x - prev_avg_x
                hand_stable = abs(dx) < stable_threshold

                if current_time - last_swipe_time > cooldown and not hand_stable:
                    if dx > 0.1:
                        gesture = "Swipe Left"
                        last_swipe_time = current_time
                    elif dx < -0.1:
                        gesture = "Swipe Right"
                        last_swipe_time = current_time

            prev_avg_x = avg_x

    cooldown_time_left = cooldown - (current_time - last_swipe_time)
    if cooldown_time_left > 0:
        cooldown_text = f"Cooldown: {cooldown_time_left:.1f} sec"
    else:
        cooldown_text = "Ready for Swipe"

    if gesture and (current_time - last_swipe_time < gesture_display_time):
        cv2.putText(frame, gesture, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 3)
    else:
        gesture = None

    cv2.putText(frame, cooldown_text, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.imshow("Swipe Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()



"""
#아래는 테스트 예정입니다.
import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

prev_avg_x = None
gesture = None
last_swipe_time = 0
last_cross_time = 0
gesture_display_time = 1.5
cooldown = 2.0
stable_threshold = 0.01

finger_tip_ids = [
    mp_hands.HandLandmark.THUMB_TIP,
    mp_hands.HandLandmark.INDEX_FINGER_TIP,
    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
    mp_hands.HandLandmark.RING_FINGER_TIP,
    mp_hands.HandLandmark.PINKY_TIP
]

def cross_gesture_detected(hand_landmarks):
    if len(hand_landmarks) != 2:
        return False
    h1, h2 = hand_landmarks[0], hand_landmarks[1]
    h1_wrist_x = h1.landmark[0].x
    h1_middle_x = h1.landmark[12].x
    h2_wrist_x = h2.landmark[0].x
    h2_middle_x = h2.landmark[12].x

    h1_cross = h1_wrist_x < h2_wrist_x and h1_middle_x > h2_middle_x
    h2_cross = h2_wrist_x < h1_wrist_x and h2_middle_x > h1_middle_x
    return h1_cross or h2_cross

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    current_time = time.time()

    gesture = None

    if result.multi_hand_landmarks:
        # 1. X자 제스처 인식
        if cross_gesture_detected(result.multi_hand_landmarks):
            if current_time - last_cross_time > cooldown:
                gesture = "X Pose Detected"
                last_cross_time = current_time

        # 2. 스와이프 제스처 인식 (오른손만 사용한다고 가정)
        if len(result.multi_hand_landmarks) == 1:
            handLms = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            tip_xs = [handLms.landmark[i].x for i in finger_tip_ids]
            avg_x = sum(tip_xs) / len(tip_xs)

            if prev_avg_x is not None:
                dx = avg_x - prev_avg_x
                hand_stable = abs(dx) < stable_threshold

                if current_time - last_swipe_time > cooldown and not hand_stable:
                    if dx > 0.1:
                        gesture = "Swipe Left"
                        last_swipe_time = current_time
                    elif dx < -0.1:
                        gesture = "Swipe Right"
                        last_swipe_time = current_time

            prev_avg_x = avg_x

        # 모든 손 그리기
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

    # Cooldown 표시
    cooldown_swipe = cooldown - (current_time - last_swipe_time)
    cooldown_cross = cooldown - (current_time - last_cross_time)
    cooldown_text = f"Swipe CD: {max(0, cooldown_swipe):.1f}s | X CD: {max(0, cooldown_cross):.1f}s"

    # 제스처 텍스트 표시
    if gesture:
        cv2.putText(frame, gesture, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 3)

    cv2.putText(frame, cooldown_text, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    cv2.imshow("Gesture Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
"""
