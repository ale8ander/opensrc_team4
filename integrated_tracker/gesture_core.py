import pyautogui
import time
import numpy as np
import cv2

instructions = {
        "Victory": "Close Tab",
        "Fist": "Refresh",
        "Open Hand": "Go Back",
        "Pointing": "Ready to Swipe",
        "Swipe Right": "Next Tab",
        "Swipe Left": "Previous Tab",
        "Scroll Up": "Scroll Up",
        "Scroll Down": "Scroll Down",
        "Thumb Up": "Quit"
        # "Swipe Right": "Tab Change",
        # "Swipe Left": "Tab Change",
        # "Scroll Down" : "",
        # "Scroll Up" : ""
    }

# 손가락 펼쳐졌는지 판단
def is_extended(tip, pip, landmarks):
    """
    Determine whether a specific finger is extended.

    Args:
        tip (int): Index of the fingertip landmark.
        pip (int): Index of the proximal interphalangeal joint landmark.
        landmarks (List): List of hand landmarks from MediaPipe.

    Returns:
        bool: True if the finger is extended, False otherwise.

    특정 손가락이 펴져 있는지를 판단합니다.

    인자:
        tip (int): 손끝 랜드마크 인덱스
        pip (int): 손가락 중간 관절의 랜드마크 인덱스
        landmarks (List): MediaPipe에서 추출한 손 랜드마크 리스트

    반환:
        bool: 손가락이 펴져 있으면 True, 아니면 False
    """
    return landmarks[tip].y < landmarks[pip].y

# 손 모양으로 제스처 분류
# 원래 scroll, swipe 기능까지 구현했으나, mediapipe 인식 한계 상 가위, 바위, 보로 한정함
def classify_gesture(landmarks, trajectory, last_gesture=None):
    """
    Classify the hand gesture based on finger landmarks and trajectory.

    Args:
        landmarks (List): List of hand landmarks.
        trajectory (deque): Recent movement trajectory of the hand.
        last_gesture (str, optional): The last recognized gesture. Defaults to None.

    Returns:
        str or None: The name of the gesture, or None if not recognized.

    손가락 위치와 이동 경로를 기반으로 손 제스처를 분류합니다.

    인자:
        landmarks (List): 손 랜드마크 리스트
        trajectory (deque): 최근 손의 이동 경로
        last_gesture (str, optional): The last recognized gesture. Defaults to None.

    반환:
        str 또는 None: 인식된 제스처 이름, 또는 인식되지 않으면 None
    """
    fingers = {
        'index': (8, 6),
        'middle': (12, 10),
        'ring': (16, 14),
        'pinky': (20, 18)
    }

    extended_fingers = [name for name, (tip, pip) in fingers.items() if is_extended(tip, pip, landmarks)]
    thumb_extended = landmarks[4].x > landmarks[3].x
    finger_count = len(extended_fingers)

    # Priority check for scroll gesture after pointing to avoid conflict with Fist
    if last_gesture == "Pointing" and finger_count == 0:
        if len(trajectory) >= 5:
            start_y = trajectory[0][1]
            end_y = trajectory[-1][1]
            dy = end_y - start_y
            
            start_x = trajectory[0][0]
            end_x = trajectory[-1][0]
            dx = end_x - start_x

            # Check for significant vertical movement
            if abs(dy) > abs(dx) and abs(dy) > 30:
                return "Scroll Down" if dy > 0 else "Scroll Up"

    if finger_count == 1 and 'index' in extended_fingers:
        if len(trajectory) >= 10:
            dx = trajectory[-1][0] - trajectory[0][0]
            dy = trajectory[-1][1] - trajectory[0][1]
            if abs(dx) > 60 and abs(dx) > abs(dy):
                return "Swipe Right" if dx > 0 else "Swipe Left"
            if abs(dy) > 60 and abs(dy) > abs(dx):
                return "Scroll Down" if dy > 0 else "Scroll Up"
        return "Pointing"
    # Add Thumb Up gesture detection
    elif thumb_extended and finger_count == 0:
        return "Thumb Up"
    elif finger_count == 0:
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


# 제스처에 따른 키보드 동작
def execute_gesture_action(gesture, os_name):
    """
    Execute a system action based on the gesture and OS.

    Args:
        gesture (str): The recognized gesture name.
        os_name (int): Operating system code (1: Windows, 0: macOS).

    제스처와 운영체제에 따라 시스템 동작을 수행합니다.

    인자:
        gesture (str): 인식된 제스처 이름
        os_name (int): 운영체제 코드 (1: Windows, 0: macOS)
    """
    if gesture == "Scroll Up":
        pyautogui.scroll(100)
        return
    if gesture == "Scroll Down":
        pyautogui.scroll(-100)
        return

    keymap = {
        "Swipe Right": ('ctrl', 'tab') if os_name else ('command', 'shift', ']'),
        "Swipe Left": ('ctrl', 'shift', 'tab') if os_name else ('command', 'shift', '['),
        "Victory": ('alt', 'f4') if os_name else ('command', 'w'),
        "Fist": ('ctrl', 'r') if os_name else ('command', 'r'), 
        "Open Hand": ('alt', 'left') if os_name else ('command', '['),
        "Thumb Up": ('command', 'q') if os_name == 0 else ('alt', 'f4'),
    }

    if gesture in keymap:
        pyautogui.hotkey(*keymap[gesture])

def update_trajectory(trajectory, hand_landmarks, frame_shape):
    """
    Calculate the center of the hand based on landmarks and append it to the trajectory.

    Args:
        trajectory (deque): A deque storing recent hand center positions.
        hand_landmarks (List[Landmark]): List of 21 hand landmark points.
        frame_shape (tuple): Shape of the frame (height, width, channels).

    Returns:
        tuple: The calculated center (cx, cy) of the hand.

    손 랜드마크를 기반으로 손 중심 좌표를 계산하여 trajectory에 저장합니다.

    반환:
        tuple: 손 중심 좌표 (cx, cy)
    """
    h, w, _ = frame_shape
    cx = int(np.mean([lm.x * w for lm in hand_landmarks]))
    cy = int(np.mean([lm.y * h for lm in hand_landmarks]))
    trajectory.append((cx, cy))
    return cx, cy


def update_fingertip_trajectory(trajectory, hand_landmarks, frame_shape):
    """
    Calculate the position of the index fingertip and append it to the trajectory.

    Args:
        trajectory (deque): A deque storing recent hand center positions.
        hand_landmarks (List[Landmark]): List of 21 hand landmark points.
        frame_shape (tuple): Shape of the frame (height, width, channels).

    Returns:
        tuple: The calculated center (cx, cy) of the hand.

    검지손가락 랜드마크를 기반으로 손가락 위치를 계산하여 trajectory에 저장합니다.

    반환:
        tuple: 손가락 위치 좌표 (cx, cy)
    """
    h, w, _ = frame_shape
    fingertip = hand_landmarks[8] # Index finger tip
    cx = int(fingertip.x * w)
    cy = int(fingertip.y * h)
    trajectory.append((cx, cy))
    return cx, cy


def draw_trajectory_on_frame(frame, trajectory):
    """
    Draw the trajectory of hand movement on the frame.

    Args:
        frame (np.ndarray): The current video frame.
        trajectory (deque): A deque containing past hand positions.

    손 이동 궤적을 프레임 위에 선으로 시각화합니다.
    """
    for i in range(1, len(trajectory)):
        cv2.line(frame, trajectory[i - 1], trajectory[i], (255, 0, 0), 2)


def should_update_gesture(gesture_timestamp, hold_duration):
    """
    Check if the cooldown period for gesture recognition has passed.

    Args:
        gesture_timestamp (float): Timestamp of the last recognized gesture.
        hold_duration (float): Cooldown duration in seconds.

    Returns:
        bool: True if gesture can be updated, False otherwise.

    이전 제스처 인식 이후 쿨다운 시간이 지났는지를 확인합니다.

    반환:
        bool: 제스처 갱신 가능 여부
    """
    cooldown_remaining = hold_duration - (time.time() - gesture_timestamp)
    return cooldown_remaining <= 0


def process_hand_gesture(hand_landmarks, trajectory, gesture_timestamp, hold_duration, os_name, last_gesture=None):
    """
    Determine the gesture from current hand data and handle cooldown logic.

    Args:
        hand_landmarks (List[Landmark]): List of current hand landmarks.
        trajectory (deque): Stored hand movement trajectory.
        gesture_timestamp (float): Timestamp of last gesture recognition.
        hold_duration (float): Cooldown duration in seconds.
        os_name (int): OS identifier (1: Windows, 0: macOS, -1: others)
        last_gesture (str, optional): The last recognized gesture. Defaults to None.

    Returns:
        tuple: (gesture to display, updated gesture_timestamp)

    현재 손 상태로부터 제스처를 판단하고, 쿨다운 조건을 충족하면 제스처를 실행합니다.
    그렇지 않으면 이전 제스처를 유지합니다.
    """
    gesture_candidate = classify_gesture(hand_landmarks, trajectory, last_gesture)

    if should_update_gesture(gesture_timestamp, hold_duration):
        if gesture_candidate and gesture_candidate != "Pointing":
            gesture_timestamp = time.time()
            execute_gesture_action(gesture_candidate, os_name)
            return gesture_candidate, gesture_timestamp
        elif gesture_candidate == "Pointing":
            # Don't reset timestamp for pointing, to allow quick swipes
            return gesture_candidate, gesture_timestamp

    return last_gesture, gesture_timestamp
