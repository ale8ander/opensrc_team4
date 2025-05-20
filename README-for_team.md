# v3.2 변경사항
### 1. 프로그램 흐름이 변경되었습니다.
   
기존:

![Image](https://github.com/user-attachments/assets/3469198f-89d7-457e-a2d8-3f37ebb3d426)

수정: (다음 실행 과정은 프로젝트 과정 중 변동이 있을 수 있으며, 현재의 테스트 코드 전제임을 밝힙니다.)

![Image](https://github.com/user-attachments/assets/ca032ffc-a011-472b-8062-7500034bd6a5)


### 2. connecting 폴더가 추가되었습니다.(내부 파일은 추후 수정 가능합니다.)

#### 2-1. gesture_handle.py 파일이 추가되었습니다.


이 코드는 socket을 이용하여 gesture_tracker.py로부터 전달된 제스처 정보를 수신하고,
이를 flutter_connect.py에서 import한 send_gesture_to_flutter 함수를 호출하여,
Flask 로컬 서버(http://127.0.0.1:5000/) 에 전송하는 중간 역할을 수행합니다.

전송 형식: 

JSON ( ex: {"gesture": "Swipe Left", "is_swipe": true} )
    
    gesture: Fist, Open Hand, Victory / Swipe Left, Swipe Right
    
    is_swipe: 스와이프 여부를 판단하며, true 일 때만 스와이프 결과를 전송합니다.


#### 2-2. flutter_connect.py 파일이 추가되었습니다.

제스처 텍스트를 Flask 로컬 서버로 전송하는 함수를 작성하였습니다.
gesture_handler.py에서 호출되어 인식된 제스처를 HTTP POST 방식으로 서버에 전달하고, 서버는 이를 웹 브라우저에 출력하거나 처리할 수 있도록 합니다.
결론적으로 ,이 함수는 제스처 데이터를 웹 서버에 전달하는 역할을 합니다. 호출하지 않으면 사용할 수 없습니다. 


#### 2-3. flask_testserver.py 파일이 추가되었습니다.

원활한 전송 확인을 위한 로컬 테스트 서버입니다. 0.5초마다 갱신됩니다.
출력 화면은 다음과 같습니다.

![Image](https://github.com/user-attachments/assets/ff045ad9-3c2b-4f63-927b-5b64948e280f)


### 3. integrated_track_with_connect 폴더가 추가되었습니다.
   
이 폴더는 suggestion용 폴더이며, 이상이 없을 시 이 폴더를 기존의 integrated_track 폴더로 대체할 수 있습니다.(추후 테스트 시 bat 내부 파일 경로 수정 필요.)

#### 3-1. gesture_tracker.py 파일 내용이 추가가되었습니다.

- line 2: import json
- line 13~20: gesture 전송 함수 send_to_handler
- line 96~114: gesture 전송 process


### 4. opensrc_team4 폴더에 run_all.bat 파일이 추가되었습니다.
 
코드 테스트(내부 명시된 코드를 순차적으로 실행해야 함)를 위한 임시 실행 파일입니다. 추후 삭제, 수정 등등이 가능합니다. 그렇게 중요하진 않습니다.

더블클릭으로 실행 가능하며, 자동으로 cmd 창이 여러 개 뜨며 각각 코드를 실행합니다. 가장 첫 cmd 창을 종료하면 종료됩니다.


# issue

1. GUI
2. OS에 따른 키설정 구별
