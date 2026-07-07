import re
import string

from app.config import settings
from app.core.ocr_pipeline import extract_detections, has_arabic, has_english


TOKEN_RE = re.compile(r"[A-Za-z\u0600-\u06ff][A-Za-z\u0600-\u06ff\-]*|\d+(?:[.,]\d+)?")
LEADING_NUMBER_RE = re.compile(r"^\s*\d")

ARABIC_NOISE_WORDS = {
    "اقراص", "أقراص", "قرص", "قرصا", "قرصاً", "كبسول", "كبسولة",
    "كبسولات", "كبسوله", "شراب", "حقن", "حقنة", "امبول", "أمبول",
    "امبولات", "أمبولات", "فيال", "فيالات", "نقط", "نقطة", "قطرة",
    "قطرات", "كريم", "مرهم", "جل", "لبوس", "لبوسات", "فوار", "بودرة",
    "كيس", "اكياس", "أكياس", "عبوة", "عبوه", "شريط", "شرائط",
    "سبراي", "بخاخ", "محلول", "معلق", "للفم", "للعين", "للاطفال",
    "للأطفال", "مجم", "جم", "جرام", "مل", "ميكروجرام", "وحدة",
    "دولية", "مضغ", "استحلاب", "مغلفة", "مغلفه",
}
ARABIC_NOISE_NORMALIZED = {word.lower() for word in ARABIC_NOISE_WORDS}

ENGLISH_NOISE_WORDS = {
    "tab", "tabs", "tablet", "tablets", "cap", "caps", "capsule",
    "capsules", "syrup", "cream", "ointment", "gel", "vial", "amp",
    "amps", "ampoule", "ampoules", "injection", "injectable", "drop",
    "drops", "spray", "sachet", "sachets", "pack", "packs", "strip",
    "strips", "piece", "pieces", "mg", "mcg", "g", "gm", "ml", "iu",
    "i.u", "oral", "susp", "suspension", "solution", "powder", "dose",
    "doses", "chewable", "dispersible", "effervescent", "lozenges",
    "f.c", "fc", "coated", "scored",
}


def _clean_token(token):
    return token.strip(string.punctuation + "،؛؟«»٪").lower()


def _is_noise_token(token):
    cleaned = _clean_token(token)

    if not cleaned or any(char.isdigit() for char in cleaned):
        return True

    return (
        cleaned in ENGLISH_NOISE_WORDS
        or cleaned in ARABIC_NOISE_NORMALIZED
    )


def _unique_tokens(tokens):
    seen = set()
    unique = []

    for token in tokens:
        key = _clean_token(token)
        if key in seen:
            continue
        seen.add(key)
        unique.append(token)

    return unique


def _clean_medicine_name(text):
    tokens = TOKEN_RE.findall(text)
    name_tokens = [
        token
        for token in tokens
        if not _is_noise_token(token)
    ]
    name_tokens = _unique_tokens(name_tokens)
    return " ".join(name_tokens).strip()


def _clean_display_text(text):
    return " ".join(text.split()).strip()


def _find_largest_leading_number_text(detections):
    numbered_detections = [
        detection
        for detection in detections
        if LEADING_NUMBER_RE.search(detection["text"])
    ]

    if not numbered_detections:
        return None

    best = max(numbered_detections, key=lambda detection: detection["area"])
    return _clean_display_text(best["text"])


def _append_leading_number_text(name, leading_number_text):
    if not name or not leading_number_text:
        return name

    if _clean_display_text(name).lower() == leading_number_text.lower():
        return name

    return f"{name} {leading_number_text}"


def _candidate_language(text):
    if has_arabic(text):
        return "ar"
    if has_english(text):
        return "en"
    return None


def _rank_candidates(candidates):
    if not candidates:
        return []

    max_area = max(candidate["area"] for candidate in candidates) or 1

    for candidate in candidates:
        area_norm = candidate["area"] / max_area
        candidate["rank"] = (0.8 * area_norm) + (0.2 * candidate["confidence"])

    return sorted(candidates, key=lambda candidate: candidate["rank"], reverse=True)


def _build_candidates(detections):
    candidates = []

    for detection in detections:
        text = _clean_medicine_name(detection["text"])
        language = _candidate_language(text)

        if not text or not language:
            continue

        candidates.append({
            "text": text,
            "language": language,
            "confidence": detection["score"],
            "area": detection["area"],
        })

    return candidates


def match_medicine(image_path: str):
    detections = extract_detections(image_path)
    candidates = _build_candidates(detections)
    leading_number_text = _find_largest_leading_number_text(detections)

    arabic_candidates = [
        candidate
        for candidate in candidates
        if (
            candidate["language"] == "ar"
            and candidate["confidence"] >= settings.ARABIC_CONFIDENCE_THRESHOLD
        )
    ]
    ranked_arabic = _rank_candidates(arabic_candidates)

    if ranked_arabic:
        best = ranked_arabic[0]
        text = _append_leading_number_text(best["text"], leading_number_text)
        return text, best["language"], best["confidence"]

    english_candidates = [
        candidate
        for candidate in candidates
        if candidate["language"] == "en"
    ]
    ranked_english = _rank_candidates(english_candidates)

    if ranked_english:
        best = ranked_english[0]
        text = _append_leading_number_text(best["text"], leading_number_text)
        return text, best["language"], best["confidence"]

    ranked_any = _rank_candidates(candidates)
    if ranked_any:
        best = ranked_any[0]
        text = _append_leading_number_text(best["text"], leading_number_text)
        return text, best["language"], best["confidence"]

    return None, None, None
