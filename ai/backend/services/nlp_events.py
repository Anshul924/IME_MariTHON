import spacy

# Try loading a custom model if present; else None
try:
    _NLP = spacy.load("backend/models/sof_event_model")
except Exception:
    _NLP = None

EVENT_KEYWORDS = {
    "arrival": ["arrived", "arrival", "anchorage", "anchored"],
    "pilot": ["pilot boarded", "pilot on board"],
    "berth": ["berthed", "berthing", "gangway"],
    "loading_start": ["loading commenced", "cargo operations started", "hoses connected"],
    "loading_stop": ["loading stopped", "operations halted", "loading suspended"],
    "loading_resume": ["loading resumed"],
    "loading_end": ["loading completed", "ops finished", "operations finished", "loading finished"],
    "discharge_start": ["discharge commenced"],
    "discharge_end": ["discharge completed"],
    "sailing": ["vessel sailed", "departure"],
    "shifting": ["shifting operations", "unmooring commenced", "shifted"]
}

def _keyword_detect(line: str) -> str:
    s = line.lower()
    for cat, phrases in EVENT_KEYWORDS.items():
        for p in phrases:
            if p in s:
                return cat
    return "unknown"

def detect_event(line: str) -> str:
    # Prefer model if available
    if _NLP is not None:
        doc = _NLP(line)
        if doc.ents:
            # Return the first entity label; map to canonical categories if desired
            return doc.ents[0].label_
    # Fallback: keywords
    return _keyword_detect(line)
