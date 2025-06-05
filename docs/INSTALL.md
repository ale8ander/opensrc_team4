# Installation Guide

**This guide will help you install and run the project on your local machine.**

#### 1. Prerequisites

- Python 3.10 (recommended), or any version below 3.12.

> Note 1: MediaPipe does not currently support Python 3.12 or higher.
Note 2: Important: When installing Python, make sure to check the box: `Add Python to PATH`.
  
  [Download Python](https://www.python.org/downloads/release/python-3100/)

#### 2. Clone the Repository

If you have Git installed:

```bash
git clone https://github.com/ale8ander/opensrc_team4.git
cd opensrc_team4
```

Or download the ZIP:

1. Click the green `Code` button on this page.
2. Select `Download ZIP`.
3. Extract the ZIP file.
4. Open your terminal and navigate to the extracted folder.

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

```plainText

//requirements.txt
opencv-python
mediapipe
numpy
pyautogui
```

#### 4. Run the Project

```bash
python integrated_tracker/main.py
```

## Notes for macOS Users

For macOS users:

- Go to **System Preferences** → **Security & Privacy** → **Camera**.
- Allow access for **"Terminal"** or **"Python"**.
- Without this permission, the webcam will not work.

## 6. Recommended Terminal

We recommend using:

- Windows: `cmd`
- macOS: `Terminal`

## Troubleshooting

If you encounter any issues during installation, please check the following:

- Is Python correctly added to your PATH?
- Are all required packages installed?
- Is your webcam working and accessible by the system?
- On macOS, did you grant camera permission to Terminal or Python?

## Still Need Help?

If you are having trouble with installation, please refer to this document or open an [Issue](https://github.com/ale8ander/opensrc_team4/issues).
