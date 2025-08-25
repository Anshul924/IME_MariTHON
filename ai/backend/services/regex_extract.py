import re
import dateparser

# Patterns are permissive to catch many formats
TIME_REGEX = re.compile(r"\b(\d{1,2})[:.](\d{2})\s*(am|pm|hrs|HRS)?\b", re.IGNORECASE)
DATE_REGEX = re.compile(
    r"\b(\d{1,2}[\/\-\. ](?:[A-Za-z]{3,9}|\d{1,2})[\/\-\. ]\d{2,4})\b"
)

def normalize_time(t: str):
    dt = dateparser.parse(t)
    if not dt:
        return None
    return dt.strftime("%H:%M")

def normalize_date(d: str):
    dt = dateparser.parse(d)
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d")

def extract_times(line: str):
    matches = []
    for m in TIME_REGEX.finditer(line):
        raw = m.group(0)
        norm = normalize_time(raw)
        if norm:
            matches.append(norm)
    return matches

def extract_dates(line: str):
    matches = []
    for m in DATE_REGEX.finditer(line):
        raw = m.group(0)
        norm = normalize_date(raw)
        if norm:
            matches.append(norm)
    return matches
