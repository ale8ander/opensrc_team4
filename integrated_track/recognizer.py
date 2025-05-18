import time

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

    def get_cooldown_remaining(self):
        return max(0.0, self.cooldown - (time.time() - self.last_swipe_time))


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
    elif (
        landmarks[8].y < landmarks[6].y
        and landmarks[12].y < landmarks[10].y
        and landmarks[16].y > landmarks[14].y
        and landmarks[20].y > landmarks[18].y
    ):
        return "Victory"
    else:
        return None

