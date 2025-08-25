from datetime import datetime
from typing import List, Dict, Optional

def _dt(date: Optional[str], time: Optional[str]):
    if not date or not time:
        return None
    return datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

def hours_between(start: datetime, end: datetime) -> float:
    return round((end - start).total_seconds() / 3600.0, 2)

def generate_summary(events: List[Dict]):
    # Normalize ordering by datetime if possible, else keep input order
    def key(e):
        d = _dt(e.get("date"), e.get("time"))
        return d or datetime.max
    ev = sorted(events, key=key)

    arrival = next((e for e in ev if e.get("event") == "arrival"), None)
    sailing = next((e for e in ev if e.get("event") == "sailing"), None)
    loading_start = next((e for e in ev if e.get("event") == "loading_start"), None)
    loading_end = next((e for e in ev if e.get("event") == "loading_end"), None)

    # Rough delay calculation: count stop→resume spans where possible; else 0.5h per delay event
    delay_hours = 0.0
    last_stop_dt = None
    for e in ev:
        if e.get("event") in ("loading_stop",) and e.get("date") and e.get("time"):
            last_stop_dt = _dt(e["date"], e["time"])
        if last_stop_dt and e.get("event") in ("loading_resume", "loading_end") and e.get("date") and e.get("time"):
            resume_dt = _dt(e["date"], e["time"])
            delay_hours += hours_between(last_stop_dt, resume_dt)
            last_stop_dt = None
    # Fallback small penalty if we saw a stop but never a resume/end
    if last_stop_dt:
        delay_hours += 0.5

    total_stay_hours = None
    if arrival and sailing and arrival.get("date") and arrival.get("time") and sailing.get("date") and sailing.get("time"):
        total_stay_hours = hours_between(_dt(arrival["date"], arrival["time"]), _dt(sailing["date"], sailing["time"]))

    cargo_ops_hours = None
    if loading_start and loading_end and loading_start.get("date") and loading_start.get("time") and loading_end.get("date") and loading_end.get("time"):
        cargo_ops_hours = hours_between(_dt(loading_start["date"], loading_start["time"]), _dt(loading_end["date"], loading_end["time"]))

    laytime_used = None
    if cargo_ops_hours is not None:
        laytime_used = round(cargo_ops_hours - delay_hours, 2)

    # Build a simple narrative
    parts = []
    if arrival:
        parts.append(f"Arrived {arrival.get('date')} {arrival.get('time')}")
    if loading_start:
        parts.append(f"Loading started {loading_start.get('date')} {loading_start.get('time')}")
    if loading_end:
        parts.append(f"Loading completed {loading_end.get('date')} {loading_end.get('time')}")
    if sailing:
        parts.append(f"Sailed {sailing.get('date')} {sailing.get('time')}")
    parts.append(f"Total delays: {delay_hours} hrs")

    summary = ". ".join([p for p in parts if p]) + "."

    return {
        "summary": summary,
        "metrics": {
            "total_port_stay_hours": total_stay_hours,
            "cargo_operation_hours": cargo_ops_hours,
            "delay_hours": delay_hours,
            "laytime_used": laytime_used
        }
    }
