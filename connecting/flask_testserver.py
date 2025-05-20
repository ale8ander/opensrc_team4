from flask import Flask, request, render_template_string

app = Flask(__name__)

# 상태 변수
last_gesture = "아직 없음"
swipe_gesture = "없음"

@app.route('/gesture', methods=['POST'])
def handle_gesture():
    global last_gesture, swipe_gesture
    data = request.json
    gesture = data.get("gesture", "None")
    last_gesture = gesture
    if "Swipe" in gesture:
        swipe_gesture = gesture
    print(f"[받음] {gesture}")
    return {"status": "ok"}

@app.route('/')
def show_gesture():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>제스처 상태 보기</title>
        <meta http-equiv="refresh" content="0.5"> <!--0.5초 간격으로 refresh됩니다.-->
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 60px; }
            .box {
                margin: 20px auto;
                padding: 20px;
                width: 400px;
                background: #f0f0f0;
                border-radius: 12px;
                box-shadow: 0 0 10px rgba(0,0,0,0.15);
            }
            .title { font-size: 1.2em; margin-bottom: 10px; }
            .content { font-size: 2em; color: #333; }
        </style>
    </head>
    <body>
        <div class="box">
            <div class="title">전체 제스처</div>
            <div class="content">{{ gesture }}</div>
        </div>
        <div class="box">
            <div class="title">스와이프 전용</div>
            <div class="content">{{ swipe }}</div>
        </div>
    </body>
    </html>
    """, gesture=last_gesture, swipe=swipe_gesture)

if __name__ == "__main__":
    print("HTML 테스트 서버 실행 중... http://localhost:5000")
    app.run(port=5000)
