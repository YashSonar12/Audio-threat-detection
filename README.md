# Audio Threat Detection System

A college-ready defense-inspired project that lets a user upload or record audio, converts it into text, detects dangerous keywords, counts each keyword, and displays the analysis in a dashboard.

## Project Structure

- `backend/` → FastAPI + Faster-Whisper transcription API
- `frontend/` → React + Vite user interface

---

## Main Features

- Upload audio files like WAV, MP3, WEBM, M4A
- Record audio directly in the browser
- Convert speech to text using Whisper
- Detect dangerous keywords from transcript
- Count each dangerous keyword
- Highlight detected keywords in the transcript
- Demo backup mode using direct transcript text

---

## 1) Local Setup Guide

### Prerequisites

Install these first:

- Python 3.10 or newer
- Node.js 18 or newer
- Git
- FFmpeg

### Install FFmpeg

#### Windows
1. Download FFmpeg build from the official FFmpeg website.
2. Extract it.
3. Add the `bin` folder path to **Environment Variables > Path**.
4. Open a new terminal and run:
   ```bash
   ffmpeg -version
   ```

#### Ubuntu / Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

---

## 2) Backend Setup

Open terminal in the `backend` folder:

```bash
cd backend
python -m venv venv
```

### Activate virtual environment

#### Windows
```bash
venv\Scripts\activate
```

#### macOS / Linux
```bash
source venv/bin/activate
```

### Install packages

```bash
pip install -r requirements.txt
```

### Run backend server

```bash
uvicorn main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

Test it in browser:

```text
http://127.0.0.1:8000/docs
```

---

## 3) Frontend Setup

Open a second terminal in the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

```text
http://127.0.0.1:5173
```

---

## 4) How to Run the Project

1. Start backend first.
2. Start frontend second.
3. Open `http://127.0.0.1:5173`
4. Upload an audio file or click **Start Recording**.
5. Add or edit dangerous keywords if needed.
6. Click **Analyze Audio**.
7. View transcript, highlighted words, and keyword counts.

---

## 5) Quickstart Demo Guide for Presentation

Use this flow in front of your teacher or panel:

### Demo Script

1. Introduce the project:
   - “This project is an Audio Threat Detection System for defense-oriented monitoring.”
   - “It accepts recorded or uploaded audio and converts speech into text.”
   - “Then it checks whether any dangerous or suspicious words were spoken.”

2. Show the interface sections:
   - Audio Input
   - Dangerous Keywords
   - Transcript Output
   - Threat Analysis

3. Demo path A: real audio
   - Upload a short audio clip with words like: attack, bomb, gun, hostage
   - Click **Analyze Audio**
   - Show transcript generation
   - Show detected keywords and counts

4. Demo path B: instant backup demo
   - Paste this into the **Quick Demo Backup** box:
     ```
     The suspect planned an attack and mentioned a bomb twice. The bomb was hidden near the road, and one man carried a gun.
     ```
   - Click **Run Demo Text Analysis**
   - Explain that the same analysis pipeline works even when you want a fast classroom demo

5. Final explanation:
   - “This can help security teams monitor suspicious voice messages or intercepted communications.”
   - “It can be extended to real-time streams, multilingual surveillance, and alert systems.”

---

## 6) Sample Viva / Presentation Lines

### Problem Statement
Existing audio surveillance often produces raw voice data, but security teams need fast textual analysis to identify threats quickly.

### Objective
To create a system that transcribes audio and automatically identifies dangerous keywords for defense-related threat analysis.

### Technologies Used
- React.js
- FastAPI
- Faster-Whisper
- HTML/CSS/JavaScript
- Browser MediaRecorder API

### Future Scope
- Real-time microphone stream analysis
- SMS/email alerts
- Multi-language support
- Severity score for threat level
- Database storage of evidence logs

---

## 7) Troubleshooting

### Issue: `ffmpeg not found`
Install FFmpeg and ensure it is added to PATH.

### Issue: slow first transcription
The first run downloads the Whisper model, so it may take some time only once.

### Issue: microphone not working
Use HTTPS or localhost, and allow browser microphone permission.

### Issue: CORS error
Make sure backend is running on port 8000 before opening frontend.

---

## 8) Suggested Audio for Demo

Record a 10–15 second sample like this:

> “There may be an attack tonight. One person mentioned a bomb and another carried a gun.”

This helps show multiple keyword hits clearly.

---

## 9) Important Note

This project is for academic, research, and defensive monitoring demonstration only.
