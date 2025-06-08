import cv2
import time
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

def check_user_inactivity(frame, last_active, USER_INACTIVITY_TIME):
    """
    Check if user has been inactive for more than 30 seconds and display Restart/Quit buttons.

    Args:
        frame (ndarray): Current video frame.
        last_active (float): Timestamp of the last user interaction.

    Returns:
        tuple: Coordinates of restart and quit buttons for click detection.

    사용자가 30초 이상 아무런 동작을 하지 않았는지 확인하고,
    'Restart' 및 'Quit' 버튼을 화면에 표시합니다.

    반환:
        tuple: 클릭 감지를 위한 Restart 및 Quit 버튼의 좌표
    """
    now = time.time()
    # Display remaining time until inactivity if still active
    remaining_time = max(0, USER_INACTIVITY_TIME - (now - last_active))
    cv2.putText(frame, f"Inactive in: {remaining_time:.1f}s", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (100, 255, 255), 2)

    if now - last_active > USER_INACTIVITY_TIME:
        h, w, _ = frame.shape
        
        # Restart 버튼 그리기
        r_x1 = int(w * 0.4)
        r_x2 = int(w * 0.5)
        r_y1 = int(h * 0.45)
        r_y2 = int(h * 0.55)

        # 박스 그리기
        cv2.rectangle(frame, (r_x1, r_y1), (r_x2, r_y2), (0, 200, 0), -1)
        
        # 텍스트 크기 계산
        text = "Restart"
        font_scale = 1
        thickness = 2
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_width, text_height = text_size
        
        # 중앙 정렬
        text_x = r_x1 + (r_x2 - r_x1 - text_width) // 2
        text_y = r_y1 + (r_y2 - r_y1 + text_height) // 2
        
        
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

        # ==========
        
        # Quit 버튼 그리기
        q_x1 = int(w * 0.55)
        q_x2 = int(w * 0.65)
        q_y1 = int(h * 0.45)
        q_y2 = int(h * 0.55)
        
        # 박스 그리기
        cv2.rectangle(frame, (q_x1, q_y1), (q_x2, q_y2), (0, 0, 200), -1)
        
        # 텍스트 크기 계산
        text = "Quit"
        font_scale = 1
        thickness = 2
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_width, text_height = text_size
        
        # 중앙 정렬
        text_x = q_x1 + (q_x2 - q_x1 - text_width) // 2
        text_y = q_y1 + (q_y2 - q_y1 + text_height) // 2
        
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

        # 버튼 좌표와 비활성화 시간 반환
        return (r_x1, r_y1, r_x2, r_y2), (q_x1, q_y1, q_x2, q_y2), now - last_active
    return None, None, 0

def draw_quit_button(frame):
    """
    Draw a clickable 'Quit' button on the frame.

    Args:
        frame (ndarray): The image frame to draw the button on.

    화면 우측 상단에 'Quit' 버튼을 그려 마우스 클릭으로 종료할 수 있도록 합니다.
    """
    h, w, _ = frame.shape

    x1 = int(w * 0.90)
    x2 = int(w * 0.98)
    y1 = int(h * 0.90)
    y2 = int(h * 0.98)

    # 박스 그리기
    cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 50, 255), -1)

    # 텍스트 크기 계산
    text = "Quit"
    font_scale = 1
    thickness = 2
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    text_width, text_height = text_size

    # 중앙 정렬
    text_x = x1 + (x2 - x1 - text_width) // 2
    text_y = y1 + (y2 - y1 + text_height) // 2 

    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

    return (x1, y1, x2, y2)