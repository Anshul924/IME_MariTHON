from .regex_extract import extract_dates, extract_times
from .nlp_events import detect_event
from .delays import detect_delay
import json, pandas as pd, os

OUT_DIR = "backend/data"

def process_line(line: str):
    event = detect_event(line)
    times = extract_times(line)
    dates = extract_dates(line)
    delay_info = detect_delay(line)

    # pick first detected date/time if multiple
    time = times[0] if times else None
    date = dates[0] if dates else None

    return {
        "event": event,
        "date": date,
        "time": time,
        "delay": delay_info["delay"],
        "reason": delay_info["reason"],
        "raw_line": line
    }

def export_json(data, file_id: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{file_id}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

def export_csv(data, file_id: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{file_id}.csv")
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return path
