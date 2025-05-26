import pyautogui

instructions = {
        "Victory": "Close Tab",
        "Fist": "Refresh",
        "Open Hand": "Go Back"
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
def classify_gesture(landmarks, trajectory):
    """
    Classify the hand gesture based on finger landmarks and trajectory.

    Args:
        landmarks (List): List of hand landmarks.
        trajectory (deque): Recent movement trajectory of the hand.

    Returns:
        str or None: The name of the gesture, or None if not recognized.

    손가락 위치와 이동 경로를 기반으로 손 제스처를 분류합니다.

    인자:
        landmarks (List): 손 랜드마크 리스트
        trajectory (deque): 최근 손의 이동 경로

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

    if finger_count == 0:
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
    keymap = {
        # "Swipe Right": ('alt', 'tab') if os_name else ('command', 'tab'),
        # "Swipe Left": ('alt', 'shift', 'tab') if os_name else ('command', 'shift', 'tab'),
        # "Scroll Up": 300,
        # "Scroll Down": -300,
        "Victory": ('alt', 'f4') if os_name else ('command', 'w'),
        "Fist": ('ctrl', 'r') if os_name else ('command', 'r'), 
        "Open Hand": ('alt', 'left') if os_name else ('command', '['),
    }

    if gesture in keymap:
        pyautogui.hotkey(*keymap[gesture])
    # elif "Scroll" in gesture: # 해당 부분 logic 사용 시 수정 필요
    #    pyautogui.scroll(keymap[gesture])