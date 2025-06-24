import requests
import sqlite3
import json
from pathlib import Path

OPENPHISH_URL = "https://openphish.com/feed.txt"
PHISHTANK_URL = "http://data.phishtank.com/data/online-valid.json"
USER_BLOCKLIST_DIR = Path("config/user_blocklist")
DATA_DIR = Path("data")
BLOCKLIST_CACHE = DATA_DIR / "blocklist_cache.db"

def load_user_blocklist():
    blocklist = set()
    USER_BLOCKLIST_DIR.mkdir(exist_ok=True)
    for file in USER_BLOCKLIST_DIR.glob("*.txt"):
        try:
            with open(file, "r") as f:
                blocklist.update(line.strip() for line in f if line.strip())
        except Exception:
            pass
    return blocklist

def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(BLOCKLIST_CACHE)
    conn.execute("CREATE TABLE IF NOT EXISTS blocklist (url TEXT PRIMARY KEY)")
    return conn

def fetch_blocklist():
    blocklist = set()
    
    # OpenPhish
    try:
        response = requests.get(OPENPHISH_URL, timeout=5)
        blocklist.update(response.text.splitlines())
    except Exception:
        pass
    
    # PhishTank
    try:
        response = requests.get(PHISHTANK_URL, timeout=5)
        data = json.loads(response.text)
        blocklist.update(entry["url"] for entry in data)
    except Exception:
        pass
    
    # User blocklist
    blocklist.update(load_user_blocklist())
    
    # Cache in SQLite
    conn = init_db()
    conn.executemany("INSERT OR IGNORE INTO blocklist (url) VALUES (?)", [(url,) for url in blocklist])
    conn.commit()
    
    # Load cached blocklist
    blocklist.update(url for (url,) in conn.execute("SELECT url FROM blocklist"))
    conn.close()
    
    return blocklist