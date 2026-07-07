import re
import time
from typing import Any, Dict, List, Optional

import requests

from app.config import settings


ARABIC_RE = re.compile(r"[\u0600-\u06ff]")
LATIN_RE = re.compile(r"[A-Za-z]")
DIGIT_RE = re.compile(r"\d")
LETTER_RE = re.compile(r"[A-Za-z\u0600-\u06ff]")


def _bbox_from_polygon(points: List[float]) -> tuple[int, int, int, int]:
    xs = points[0::2]
    ys = points[1::2]
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))


def _area(bbox: tuple[int, int, int, int]) -> int:
    x1, y1, x2, y2 = bbox
    return max(0, x2 - x1) * max(0, y2 - y1)


def _language_for(text: str, azure_language: Optional[str]) -> str:
    if ARABIC_RE.search(text):
        return "ar"
    if LATIN_RE.search(text):
        return "en"
    if azure_language in {"ar", "en"}:
        return azure_language
    return "en"


def _average_word_confidence(words: List[Dict[str, Any]]) -> float:
    scores = [
        float(word["confidence"])
        for word in words
        if isinstance(word.get("confidence"), (int, float))
    ]
    return sum(scores) / len(scores) if scores else 1.0


def _azure_read(image_path: str) -> Dict[str, Any]:
    if not settings.AZURE_OCR_ENDPOINT or not settings.AZURE_OCR_KEY:
        raise RuntimeError("AZURE_OCR_ENDPOINT and AZURE_OCR_KEY must be set.")

    analyze_url = (
        settings.AZURE_OCR_ENDPOINT.rstrip("/")
        + "/vision/v3.2/read/analyze"
    )
    headers = {
        "Ocp-Apim-Subscription-Key": settings.AZURE_OCR_KEY,
        "Content-Type": "application/octet-stream",
    }

    with open(image_path, "rb") as image_file:
        response = requests.post(
            analyze_url,
            headers=headers,
            data=image_file.read(),
            timeout=settings.AZURE_OCR_TIMEOUT,
        )
    response.raise_for_status()

    operation_url = response.headers["Operation-Location"]

    for _ in range(settings.AZURE_OCR_MAX_POLLS):
        result = requests.get(
            operation_url,
            headers={"Ocp-Apim-Subscription-Key": settings.AZURE_OCR_KEY},
            timeout=settings.AZURE_OCR_TIMEOUT,
        )
        result.raise_for_status()
        payload = result.json()
        status = payload.get("status", "").lower()

        if status == "succeeded":
            return payload
        if status == "failed":
            raise RuntimeError("Azure OCR failed.")

        time.sleep(settings.AZURE_OCR_POLL_SECONDS)

    raise TimeoutError("Azure OCR timed out.")


def extract_detections(image_path: str) -> List[Dict[str, Any]]:
    payload = _azure_read(image_path)
    detections = []

    for page in payload.get("analyzeResult", {}).get("readResults", []):
        page_language = page.get("language")

        for line in page.get("lines", []):
            text = line.get("text", "").strip()
            polygon = line.get("boundingBox") or []

            if not text or len(polygon) < 8:
                continue

            words = []
            for word in line.get("words", []):
                word_text = word.get("text", "").strip()
                if not word_text:
                    continue
                words.append({
                    "text": word_text,
                    "confidence": float(word.get("confidence", 1.0)),
                    "language": _language_for(word_text, page_language),
                })

            bbox = _bbox_from_polygon(polygon)
            score = _average_word_confidence(words)

            detections.append({
                "bbox": bbox,
                "text": text,
                "score": score,
                "area": _area(bbox),
                "lang": _language_for(text, page_language),
                "words": words,
            })

    return detections


def compute_ranks(detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not detections:
        return detections

    max_area = max(d["area"] for d in detections)

    for detection in detections:
        area_norm = detection["area"] / max_area if max_area else 0
        detection["rank"] = (
            settings.SCORE_WEIGHT * detection["score"]
            + settings.AREA_WEIGHT * area_norm
        )

    return detections


def best_of(detections: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not detections:
        return None

    return max(detections, key=lambda detection: detection["rank"])


def has_digits(text: str) -> bool:
    return bool(DIGIT_RE.search(text))


def has_letters(text: str) -> bool:
    return bool(LETTER_RE.search(text))


def has_arabic(text: str) -> bool:
    return bool(ARABIC_RE.search(text))


def has_english(text: str) -> bool:
    return bool(LATIN_RE.search(text))
