import pyautogui
import numpy as np

instructions = {
    "Victory": "Close Tab",
    "Fist": "Refresh",
    "Open Hand": "Go Back",
    "Swipe Right": "Tab Change",
    "Swipe Left": "Tab Change",
    "Swipe Ready": "Prepare to Swipe"
}


# 벡터 각도 계산
def angle_between(v1, v2):
    """
    Calculate the angle between two 3D vectors.

    Args:
        v1 (np.ndarray): First vector.
        v2 (np.ndarray): Second vector.

    Returns:
        float: Angle in radians between the two vectors.

    두 3D 벡터 간의 각도를 계산합니다.

    인자:
        v1 (np.ndarray): 첫 번째 벡터
        v2 (np.ndarray): 두 번째 벡터

    반환:
        float: 두 벡터 사이의 각도(라디안)
    """
    unit_v1 = v1 / np.linalg.norm(v1)
    unit_v2 = v2 / np.linalg.norm(v2)
    dot = np.dot(unit_v1, unit_v2)
    return np.arccos(np.clip(dot, -1.0, 1.0))

# 손가락이 펴졌는지 (관절 간 각도 기준)
def is_finger_straight(mcp, pip, tip, landmarks):
    """
    Determine whether a specific finger is extended.

    Args:
        mcp (int): Index of the metacarpophalangeal joint landmark.
        pip (int): Index of the proximal interphalangeal joint landmark.
        tip (int): Index of the fingertip landmark.
        landmarks (List): List of hand landmarks from MediaPipe.

    Returns:
        bool: True if the finger is extended, False otherwise.

    특정 손가락이 펴져 있는지를 판단합니다.

    인자:
        mcp (int): 손가락 시작 관절의 랜드마크 인덱스
        pip (int): 손가락 중간 관절의 랜드마크 인덱스
        tip (int): 손끝 랜드마크 인덱스
        landmarks (List): MediaPipe에서 추출한 손 랜드마크 리스트

    반환:
        bool: 손가락이 펴져 있으면 True, 아니면 False
    """
    a = np.array([
        landmarks[pip].x - landmarks[mcp].x,
        landmarks[pip].y - landmarks[mcp].y,
        landmarks[pip].z - landmarks[mcp].z
    ])
    b = np.array([
        landmarks[tip].x - landmarks[pip].x,
        landmarks[tip].y - landmarks[pip].y,
        landmarks[tip].z - landmarks[pip].z
    ])
    angle = angle_between(a, b)
    return angle < np.pi / 6  # 30도 이하

# 엄지가 펴졌는지
def is_thumb_straight(landmarks):
    """
    Determine whether the thumb is extended.

    Args:
        landmarks (List): List of hand landmarks from MediaPipe.

    Returns:
        bool: True if the thumb is extended, False otherwise.

    엄지손가락이 펴져 있는지를 판단합니다.

    인자:
        landmarks (List): MediaPipe에서 추출한 손 랜드마크 리스트

    반환:
        bool: 엄지가 펴져 있으면 True, 아니면 False
    """
    return landmarks[4].z < landmarks[3].z - 0.02

# 손바닥 방향 판단 (법선 벡터 기반)
def get_palm_direction(landmarks):
    """
    Determine the palm's facing direction relative to the camera.

    Args:
        landmarks (List): List of hand landmarks from MediaPipe.

    Returns:
        str: 'front', 'side', or 'back' depending on orientation.

    손바닥이 카메라를 향하는 방향을 판단합니다.

    인자:
        landmarks (List): MediaPipe에서 추출한 손 랜드마크 리스트

    반환:
        str: 손바닥 방향 ('front', 'side', 'back')
    """
    points = np.asarray([
        [landmarks[0].x, landmarks[0].y, landmarks[0].z],
        [landmarks[5].x, landmarks[5].y, landmarks[5].z],
        [landmarks[17].x, landmarks[17].y, landmarks[17].z]
    ])

    v1 = points[0] - points[2]  # 0 - 17
    v2 = points[1] - points[2]  # 5 - 17

    normal_vector = np.cross(v1, v2)
    normal_vector /= np.linalg.norm(normal_vector)

    camera_direction = np.array([0, 0, -1])
    dot = np.dot(normal_vector, camera_direction)
    angle = np.arccos(np.clip(dot, -1.0, 1.0))

    if angle < np.pi / 6:
        return 'back'
    elif angle < np.pi / 3:
        return 'side'
    else:
        return 'front'

# 손 모양으로 제스처 분류
def classify_gesture(landmarks, trajectory):
    """
    Classify the current hand gesture based on finger states and hand trajectory.

    Args:
        landmarks (List): List of hand landmarks from MediaPipe.
        trajectory (deque): List of recent hand center x-y positions.

    Returns:
        str or None: Detected gesture name, or None if no gesture is recognized.

    손 모양과 이동 경로를 기반으로 제스처를 분류합니다.

    인자:
        landmarks (List): MediaPipe에서 추출한 손 랜드마크 리스트
        trajectory (deque): 손 중심의 최근 이동 궤적 좌표 리스트

    반환:
        str 또는 None: 인식된 제스처 이름, 인식되지 않으면 None
    """

    fingers_extended = [
        is_finger_straight(5, 6, 8, landmarks),    # index
        is_finger_straight(9, 10, 12, landmarks),  # middle
        is_finger_straight(13, 14, 16, landmarks), # ring
        is_finger_straight(17, 18, 20, landmarks)  # pinky
    ]
    thumb_extended = is_thumb_straight(landmarks)
    num_extended = sum(fingers_extended)

    palm_direction = get_palm_direction(landmarks)

    if num_extended >= 4 and thumb_extended:
        if palm_direction == 'front' and landmarks[9].y > landmarks[20].y:
            return "Open Hand"
        elif palm_direction == 'side' and landmarks[9].y < landmarks[17].y:
            if len(trajectory) >= 5:
                xs = [pt[0] for pt in trajectory]
                cumulative_dx = sum(abs(xs[i] - xs[i - 1]) for i in range(1, len(xs)))
                direction = 'right' if xs[-1] > xs[0] else 'left'
                if cumulative_dx > 100:
                    return "Swipe Right" if direction == 'right' else "Swipe Left"
            return "Swipe Ready"
        elif palm_direction in ['side', 'front'] and landmarks[9].y < landmarks[20].y:
            if len(trajectory) >= 5:
                xs = [pt[0] for pt in trajectory]
                cumulative_dx = sum(abs(xs[i] - xs[i - 1]) for i in range(1, len(xs)))
                direction = 'right' if xs[-1] > xs[0] else 'left'
                if cumulative_dx > 100:
                    return "Swipe Right" if direction == 'right' else "Swipe Left"
            return "Swipe Ready"

    if palm_direction == 'front':
        if fingers_extended[0] and fingers_extended[1] and sum(fingers_extended) <= 2:
            return "Victory"
        if num_extended == 0 and not thumb_extended:
            return "Fist"

    return None

# 제스처에 따른 키보드 동작
def execute_gesture_action(gesture, os_name):
    """
    Execute a keyboard shortcut based on the recognized gesture and operating system.

    Args:
        gesture (str): Recognized gesture name.
        os_name (int): OS flag (1 for Windows, 0 for macOS).

    인식된 제스처와 운영체제에 따라 키보드 단축키를 실행합니다.

    인자:
        gesture (str): 인식된 제스처 이름
        os_name (int): 운영체제 플래그 (1: Windows, 0: macOS)
    """
    keymap = {
        "Victory": ('alt', 'f4') if os_name else ('command', 'w'),
        "Fist": ('ctrl', 'r') if os_name else ('command', 'r'),
        "Open Hand": ('alt', 'left') if os_name else ('command', '['),
        "Swipe Right": ('alt', 'tab') if os_name else ('command', 'tab'),
        "Swipe Left": ('alt', 'shift', 'tab') if os_name else ('command', 'shift', 'tab'),
    }

    if gesture in keymap:
        try:
            pyautogui.hotkey(*keymap[gesture])
        except pyautogui.FailSafeException:
            print("마우스가 화면 구석에 있어서 Fail-safe 트리거됨.")
