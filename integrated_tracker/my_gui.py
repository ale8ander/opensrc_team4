import cv2
from gesture_core import instructions

# 화면 우측 가이드 라인 제공
def show_guidline(frame):
    frame_width = frame.shape[1]
    
    for i, (gesture_name, description) in enumerate(instructions.items()):
        line = f"{gesture_name}: {description}"
        text_size, _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        text_width = text_size[0]
        x = frame_width - text_width - 70
        y = 30 + (i + 1) * 30
        if i == 0:
            header = "<Guideline>"
            header_size, _ = cv2.getTextSize(header, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
            header_width = header_size[0]
            header_x = frame_width - header_width - 70
            cv2.putText(frame, header, (header_x, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
