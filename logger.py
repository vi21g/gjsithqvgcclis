import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("chat_logs")
LOG_DIR.mkdir(exist_ok=True)


def log_conversation(user_id: int, username: str, question: str, answer: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "username": username,
        "question": question,
        "answer": answer,
    }

    log_file = LOG_DIR / f"{user_id}.jsonl"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error writing log: {e}")
