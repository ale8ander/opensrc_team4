#!/bin/bash

echo "[1/3] Flask 서버 실행"
osascript -e 'tell app "Terminal" to do script "python3 connecting/flask_testserver.py"'
sleep 1

echo "[2/3] Gesture 핸들러 실행"
osascript -e 'tell app "Terminal" to do script "python3 connecting/gesture_handler.py"'
sleep 1

echo "[3/3] Gesture 트래커 실행"
osascript -e 'tell app "Terminal" to do script "python3 integrated_track_with_connecting/gesture_tracker.py"'
sleep 1

echo "[4/4] 브라우저 열기"
open "http://127.0.0.1:5000/"
