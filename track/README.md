### fucntions
- 실시간 웹캠 영상에서 손의 중심 좌표 추적
- 최근 10 프레임의 중심 좌표를 저장해서 궤적 그림
- 손이 좌우로 많이 이동하면 스와이프 제스처로 판단
- 판단 결과는 화면에 텍스트로 표시됨</br></br>
- 부가 기능: emojis 출력

### configuration (차후 Docker에 넣기)
'''
pip install mediapipe opencv-python numpy
'''
 You should use Python 3.7~3.11

### structure

get_hand_center: 손 중심 좌표 계산 함수
window가 꺼질 때까지 해당 함수 무한 반복

emojis 출력 관련 함수: classify_hand_pose, overlay_png

### Quit
'q' key or just close window

### Problem
- GUI issue: 창닫기 버튼 비활성화(OpenCV-Macbook 호환 문제)
