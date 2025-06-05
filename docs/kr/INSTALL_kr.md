# 설치 가이드

**이 문서는 프로젝트를 로컬 환경에 설치하고 실행하는 방법을 안내합니다.**

## 1. 사전 준비

* Python 3.10 (권장), 또는 3.12 미만 버전 사용
  [Python 다운로드](https://www.python.org/downloads/release/python-3100/)

**주의사항:**

* MediaPipe는 현재 Python 3.12 이상 버전을 지원하지 않습니다.
* Python 설치 시 반드시 `Add Python to PATH` 옵션을 체크하세요.

---

## 2. 레포지토리 클론

Git이 설치되어 있는 경우:

```bash
git clone https://github.com/ale8ander/opensrc_team4.git
cd opensrc_team4
```

Git이 없는 경우 ZIP 다운로드:

1. 페이지 상단의 초록색 `Code` 버튼 클릭
2. `Download ZIP` 선택
3. ZIP 파일 압축 해제
4. 터미널을 열고 해당 폴더로 이동

---

## 3. 의존성 패키지 설치

```bash
pip install -r requirements.txt
```

### requirements.txt 내용

```txt
opencv-python
mediapipe
numpy
pyautogui
```

---

## 4. 프로젝트 실행

```bash
python integrated_tracker/main.py
```

---

## macOS 사용자 참고사항

macOS 사용자의 경우:

* **시스템 환경설정** → **보안 및 개인정보 보호** → **카메라** 항목으로 이동
* **"Terminal"** 또는 **"Python"** 에 카메라 접근 권한을 허용하세요.
* 권한이 없으면 웹캠이 정상적으로 작동하지 않습니다.

---

## 5. 권장 터미널

권장하는 터미널:

* Windows: `cmd`
* macOS: `Terminal`

---

## 문제 해결 (Troubleshooting)

설치 과정에서 문제가 발생할 경우 다음 사항을 확인하세요:

* Python이 PATH에 올바르게 추가되어 있나요?
* 모든 필수 패키지가 정상적으로 설치되었나요?
* 웹캠이 시스템에서 정상적으로 인식되고 사용 가능한 상태인가요?
* macOS 사용자는 Terminal 또는 Python에 카메라 권한을 부여했나요?

---

## 추가 지원

설치에 어려움을 겪고 있다면 본 문서를 참고하거나 [Issue](https://github.com/ale8ander/opensrc_team4/issues)를 등록해 주세요.
