DELAY_KEYWORDS = {
    "weather": ["rain", "storm", "bad weather"],
    "shift": ["shift change"],
    "strike": ["strike", "union"],
    "congestion": ["waiting for berth", "awaiting berth", "port congestion"],
    "ops": ["idle", "halted", "suspended", "stopped"]
}

def detect_delay(line: str):
    s = line.lower()
    for reason, words in DELAY_KEYWORDS.items():
        for w in words:
            if w in s:
                return {"delay": True, "reason": reason}
    return {"delay": False, "reason": None}
