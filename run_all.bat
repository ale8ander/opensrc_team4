@echo off
echo [1/3] Flask test server running
start cmd /k python connecting\flask_testserver.py
timeout /t 1 >nul

echo [2/3] Gesture handler running
start cmd /k python connecting\gesture_handler.py
timeout /t 1 >nul

echo [3/3] Gesture tracker running
start cmd /k python integrated_tracker\main.py
timeout /t 1 >nul

echo [4/4] 브라우저에서 결과 창 열기
start http://127.0.0.1:5000/

echo ✅ 실행 완료
pause
