import os
import cv2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

emoji_img_paths = {
    "Swipe Right": os.path.join(BASE_DIR, "emojis/swipe_right.png"),
    "Swipe Left": os.path.join(BASE_DIR, "emojis/swipe_left.png"),
    "Fist": os.path.join(BASE_DIR, "emojis/fist.png"),
    "Open Hand": os.path.join(BASE_DIR, "emojis/open_hand.png"),
    "Victory": os.path.join(BASE_DIR, "emojis/victory.png")
}

emoji_cache = {
    name: cv2.imread(path, cv2.IMREAD_UNCHANGED)
    for name, path in emoji_img_paths.items()
    if os.path.exists(path)
}

# background image 위에 투명하게 합성
def overlay_png(background, gesture, x, y):
    """
    Overlay a transparent PNG emoji onto the background image at the specified (x, y) position.

    Args:
        background (numpy.ndarray): Background image.
        gesture (str): Name of the gesture corresponding to the emoji.
        x (int): X-coordinate of the top-left corner for overlay.
        y (int): Y-coordinate of the top-left corner for overlay.

    Returns:
        numpy.ndarray: Image with the emoji overlaid.

    배경 이미지 위의 지정된 (x, y) 위치에 투명한 PNG 이모지를 합성합니다.

    인자:
        background (numpy.ndarray): 배경 이미지
        gesture (str): 이모지로 사용할 제스처 이름
        x (int): 합성할 위치의 좌측 상단 x좌표
        y (int): 합성할 위치의 좌측 상단 y좌표

    반환:
        numpy.ndarray: 이모지가 합성된 이미지
    """
    overlay = emoji_cache.get(gesture)
    if overlay is None or overlay.shape[2] != 4:
        return background
    
    h, w = overlay.shape[:2]
    if y + h > background.shape[0] or x + w > background.shape[1]:
        return background

    alpha_overlay = overlay[:, :, 3] / 255.0
    alpha_background = 1.0 - alpha_overlay

    for c in range(0, 3):
        background[y : y + h, x : x + w, c] = (
            alpha_overlay * overlay[:, :, c]
            + alpha_background * background[y : y + h, x : x + w, c]
        )
    return background


def overlay_face_with_emoji(frame, face_detections):
    """
    Overlay an emoji onto each detected face in the frame.

    Args:
        frame (numpy.ndarray): Video frame to overlay emojis onto.
        face_detections: Face detection result containing bounding boxes of detected faces.

    Returns:
        None: The function modifies the input frame in place.

    프레임 내에서 감지된 얼굴마다 이모지를 합성합니다.

    인자:
        frame (numpy.ndarray): 이모지를 합성할 비디오 프레임
        face_detections: 감지된 얼굴의 bounding box 정보를 포함하는 얼굴 인식 결과

    반환:
        None: 입력 프레임 자체를 수정합니다.
    """
    # 얼굴 인식
    if face_detections.detections:
        for detection in face_detections.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            x = max(0, int(bboxC.xmin * iw))
            y = max(0, int(bboxC.ymin * ih))
            w = int(bboxC.width * iw)
            h = int(bboxC.height * ih)

            x2 = min(iw, x + w)
            y2 = min(ih, y + h)

            # emoji 합성
            face_img_path = os.path.join(BASE_DIR, "emojis/kissing.png")
            emoji_img = cv2.imread(face_img_path, cv2.IMREAD_UNCHANGED)
            if emoji_img is not None:
                emoji_resized = cv2.resize(emoji_img, (x2 - x, y2 - y))
                
                alpha_s = emoji_resized[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s

                for c in range(0, 3):
                    frame[y:y2, x:x2, c] = (alpha_s * emoji_resized[:, :, c] +
                                            alpha_l * frame[y:y2, x:x2, c])    