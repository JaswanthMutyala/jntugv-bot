import requests, hashlib, json, os
from bs4 import BeautifulSoup

URLS = {
    "JNTU-GV Notices": "https://jntugv.edu.in/notice",
    "Exams Portal":    "https://exams.jntugv.edu.in/",
}
TG_TOKEN   = os.environ["TG_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]
CACHE_FILE = "cache.json"

def get_hash(url):
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
    for t in soup(["script", "style", "meta"]):
        t.decompose()
    return hashlib.md5(soup.get_text().encode()).hexdigest()

def notify(text):
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={"chat_id": TG_CHAT_ID, "text": text}
    )

# Load cache (committed back to repo after each run)
if os.path.exists(CACHE_FILE):
    cache = json.load(open(CACHE_FILE))
else:
    cache = {}

alerts = []
for name, url in URLS.items():
    h = get_hash(url)
    if url not in cache:
        cache[url] = h
    elif h != cache[url]:
        alerts.append(f"🔔 {name} updated!\n{url}")
        cache[url] = h

# Save cache so next run can compare
with open(CACHE_FILE, "w") as f:
    json.dump(cache, f, indent=2)

# Send alerts
for a in alerts:
    notify(a)

if not alerts:
    print("No changes detected.")   
