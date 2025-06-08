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
