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
    return landmarks[tip].y < landmarks[pip].y

# 손 모양으로 제스처 분류
# 원래 scroll, swipe 기능까지 구현했으나, mediapipe 인식 한계 상 가위, 바위, 보로 한정함
def classify_gesture(landmarks, trajectory):
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