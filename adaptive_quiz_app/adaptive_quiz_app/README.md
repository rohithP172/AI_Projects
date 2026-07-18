# Adaptive Quiz App

This is a simple adaptive quiz web application built using Flask. It adapts question difficulty based on user performance.

## How It Works
- Starts with medium-level questions.
- If the user gets 2 right, difficulty increases to hard.
- If 2 wrong, it drops to easy.

## Run Instructions
```bash
pip install -r requirements.txt
python app.py
```
