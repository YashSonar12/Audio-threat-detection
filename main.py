from __future__ import annotations

import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from pydantic import BaseModel

APP_TITLE = "Audio Threat Detection API"
DEFAULT_KEYWORDS = [
    "attack",
    "bomb",
    "blast",
    "explosion",
    "gun",
    "rifle",
    "pistol",
    "kill",
    "murder",
    "hostage",
    "terror",
    "terrorist",
    "grenade",
    "missile",
    "sniper",
    "fire",
    "raid",
    "ambush",
    "weapon",
    "ammunition",
]
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".webm", ".ogg", ".flac"}
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "analysis_history.json"

app = FastAPI(title=APP_TITLE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class KeywordStat(BaseModel):
    keyword: str
    count: int


class SegmentOut(BaseModel):
    start: float
    end: float
    text: str


class AnalysisResponse(BaseModel):
    filename: str
    language: str
    duration_seconds: Optional[float]
    transcript: str
    highlighted_transcript: str
    matched_keywords: List[KeywordStat]
    total_dangerous_keyword_hits: int
    safety_score: int
    safety_level: str
    segments: List[SegmentOut]


class HistoryItem(BaseModel):
    id: str
    created_at: str
    source_type: str
    filename: str
    language: str
    duration_seconds: Optional[float]
    transcript: str
    matched_keywords: List[KeywordStat]
    total_dangerous_keyword_hits: int
    safety_score: int
    safety_level: str


_model: Optional[WhisperModel] = None


def ensure_history_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def calculate_safety_score(total_hits: int) -> tuple[int, str]:
    score = max(0, 100 - (total_hits * 15))

    if total_hits == 0:
        level = "Safe"
    elif total_hits <= 2:
        level = "Low Risk"
    elif total_hits <= 5:
        level = "Medium Risk"
    elif total_hits <= 8:
        level = "High Risk"
    else:
        level = "Critical"

    return score, level


def read_history() -> List[dict]:
    ensure_history_file()
    try:
        content = HISTORY_FILE.read_text(encoding="utf-8").strip()
        if not content:
            return []

        data = json.loads(content)
        if not isinstance(data, list):
            return []

        normalized_items = []
        for item in data:
            if not isinstance(item, dict):
                continue

            total_hits = int(item.get("total_dangerous_keyword_hits", 0))
            if item.get("safety_score") is None or item.get("safety_level") is None:
                score, level = calculate_safety_score(total_hits)
                item["safety_score"] = score
                item["safety_level"] = level

            normalized_items.append(item)

        return normalized_items
    except Exception:
        return []


def write_history(items: List[dict]) -> None:
    ensure_history_file()
    HISTORY_FILE.write_text(
        json.dumps(items, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_analysis_to_history(result: AnalysisResponse, source_type: str) -> None:
    history = read_history()
    item = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_type": source_type,
        "filename": result.filename,
        "language": result.language,
        "duration_seconds": result.duration_seconds,
        "transcript": result.transcript,
        "matched_keywords": [entry.model_dump() for entry in result.matched_keywords],
        "total_dangerous_keyword_hits": result.total_dangerous_keyword_hits,
        "safety_score": result.safety_score,
        "safety_level": result.safety_level,
    }
    history.insert(0, item)
    write_history(history)


def delete_history_item_by_id(item_id: str) -> bool:
    history = read_history()
    updated = [item for item in history if item.get("id") != item_id]
    if len(updated) == len(history):
        return False
    write_history(updated)
    return True


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        _model = WhisperModel(model_size, device="cpu", compute_type=compute_type)
    return _model


@app.on_event("startup")
def startup_event() -> None:
    ensure_history_file()
    write_history(read_history())


@app.get("/")
def root() -> dict:
    return {
        "message": APP_TITLE,
        "status": "running",
        "default_keywords": DEFAULT_KEYWORDS,
    }


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/keywords")
def keywords() -> dict:
    return {"default_keywords": DEFAULT_KEYWORDS}


@app.get("/history", response_model=List[HistoryItem])
def get_history() -> List[HistoryItem]:
    history = read_history()
    return [HistoryItem(**item) for item in history]


@app.delete("/history")
def clear_history() -> dict:
    write_history([])
    return {"message": "History cleared successfully."}


@app.delete("/history/{item_id}")
def delete_history_item(item_id: str) -> dict:
    deleted = delete_history_item_by_id(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History item not found.")
    return {"message": "History item deleted successfully."}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(
    audio: UploadFile = File(...),
    custom_keywords: Optional[str] = Form(default=None),
) -> AnalysisResponse:
    suffix = Path(audio.filename or "uploaded_audio.wav").suffix.lower()
    if suffix and suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    keywords_to_check = parse_keywords(custom_keywords)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix or ".wav") as tmp:
            temp_path = tmp.name
            content = await audio.read()
            if not content:
                raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")
            tmp.write(content)

        model = get_model()
        segments, info = model.transcribe(temp_path, beam_size=5, vad_filter=True)

        segment_list = []
        full_transcript_parts = []

        for seg in segments:
            text = seg.text.strip()
            if not text:
                continue
            segment_list.append(
                SegmentOut(start=round(seg.start, 2), end=round(seg.end, 2), text=text)
            )
            full_transcript_parts.append(text)

        transcript = " ".join(full_transcript_parts).strip()
        keyword_counts = find_keyword_counts(transcript, keywords_to_check)
        highlighted = highlight_keywords(transcript, [item[0] for item in keyword_counts])
        total_hits = sum(v for _, v in keyword_counts)
        safety_score, safety_level = calculate_safety_score(total_hits)

        result = AnalysisResponse(
            filename=audio.filename or "recorded_audio",
            language=getattr(info, "language", "unknown"),
            duration_seconds=round(getattr(info, "duration", 0.0), 2) if getattr(info, "duration", None) else None,
            transcript=transcript,
            highlighted_transcript=highlighted,
            matched_keywords=[KeywordStat(keyword=k, count=v) for k, v in keyword_counts],
            total_dangerous_keyword_hits=total_hits,
            safety_score=safety_score,
            safety_level=safety_level,
            segments=segment_list,
        )

        save_analysis_to_history(result, source_type="audio")
        return result

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/analyze-demo", response_model=AnalysisResponse)
def analyze_demo_text(payload: dict) -> AnalysisResponse:
    transcript = str(payload.get("transcript", "")).strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required for demo mode.")

    keywords_to_check = parse_keywords(payload.get("custom_keywords"))
    keyword_counts = find_keyword_counts(transcript, keywords_to_check)
    highlighted = highlight_keywords(transcript, [item[0] for item in keyword_counts])
    total_hits = sum(v for _, v in keyword_counts)
    safety_score, safety_level = calculate_safety_score(total_hits)

    result = AnalysisResponse(
        filename="demo_text_input",
        language="en",
        duration_seconds=None,
        transcript=transcript,
        highlighted_transcript=highlighted,
        matched_keywords=[KeywordStat(keyword=k, count=v) for k, v in keyword_counts],
        total_dangerous_keyword_hits=total_hits,
        safety_score=safety_score,
        safety_level=safety_level,
        segments=[SegmentOut(start=0.0, end=0.0, text=transcript)],
    )

    save_analysis_to_history(result, source_type="demo")
    return result


def parse_keywords(custom_keywords: Optional[str]) -> List[str]:
    if not custom_keywords or not str(custom_keywords).strip():
        return DEFAULT_KEYWORDS

    items = [part.strip().lower() for part in re.split(r"[,\n]", str(custom_keywords))]
    cleaned = []
    seen = set()
    for item in items:
        if item and item not in seen:
            cleaned.append(item)
            seen.add(item)
    return cleaned or DEFAULT_KEYWORDS


def find_keyword_counts(transcript: str, keywords: List[str]) -> List[tuple[str, int]]:
    normalized = transcript.lower()
    results = Counter()

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        matches = re.findall(pattern, normalized, flags=re.IGNORECASE)
        if matches:
            results[keyword] = len(matches)

    return sorted(results.items(), key=lambda item: (-item[1], item[0]))


def highlight_keywords(transcript: str, matched_keywords: List[str]) -> str:
    highlighted = transcript
    for keyword in sorted(matched_keywords, key=len, reverse=True):
        pattern = re.compile(rf"\b({re.escape(keyword)})\b", flags=re.IGNORECASE)
        highlighted = pattern.sub(r"<mark>\1</mark>", highlighted)
    return highlighted