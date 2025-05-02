import time

class SwipeRecognizer:
    def __init__(self, cooldown=2.0, movement_threshold=0.1, stability_threshold=0.01):
        self.cooldown = cooldown
        self.movement_threshold = movement_threshold
        self.stability_threshold = stability_threshold

        self.prev_avg_x = None
        self.last_swipe_time = 0
        self.last_gesture = None

    def update(self, tip_xs):
        """
        tip_xs: 엄지~소지 손가락 끝 5개의 x 좌표 리스트 (0.0 ~ 1.0)
        return: (gesture: str or None, cooldown_time_left: float)
        """
        current_time = time.time()

        if len(tip_xs) != 5:
            return "Error: Invalid number of coordinates", 0

        avg_x = sum(tip_xs) / 5  # 손가락 끝들의 x 좌표 평균

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

        # 제스처가 감지되었을 경우, 해당 제스처를 반환
        if gesture:
            self.last_gesture = gesture
            return f"Detected gesture: {gesture}", 0
        
        # 쿨다운이 남아있을 경우, 쿨다운 시간 반환
        cooldown_time_left = self.cooldown - (current_time - self.last_swipe_time)
        return f"Cooldown time left: {cooldown_time_left:.2f} seconds", cooldown_time_left
