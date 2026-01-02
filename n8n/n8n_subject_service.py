import requests

N8N_URL = "http://localhost:5678/webhook/subject-list"

def load_subjects_from_n8n(page=1, per_page=9, category="", level=""):
    payload = {
        "page": page,
        "per_page": per_page,
        "category": category,
        "level": level
    }

    res = requests.post(N8N_URL, json=payload, timeout=5)
    res.raise_for_status()

    data = res.json()

    # 🔥 FIX CỐT LÕI
    if isinstance(data, list):
        data = data[0] if data else {}

    return data
