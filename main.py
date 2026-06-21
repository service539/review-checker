from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY", "")

OWNER_REPLY_PHRASES = [
    "Response from the owner",
    "Antwort vom Inhaber",
    "Risposta del titolare",
    "Réponse du propriétaire",
    "Respuesta del propietario",
    "Reactie van de eigenaar",
    "Resposta do proprietário",
    "Odpowiedź właściciela",
    "Ответ владельца",
    "オーナーからの返信",
    "来自业主的回复",
    "업주의 답변",
]

class CheckRequest(BaseModel):
    url: str

def scrape_page(url: str) -> str:
    payload = {
        "api_key": SCRAPER_API_KEY,
        "url": url,
        "render": "true",
        "country_code": "us",
        "keep_headers": "true",
        "wait": 8000,  # wait 8 seconds for JS to fully render
        "wait_for": "div[data-review-id]",  # wait for review elements
    }

    headers = {
        "Cookie": "CONSENT=YES+; SOCS=CAESEwgDEgk0OTc5NzA4MjQaAmVuIAEaBgiA_LysBg",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(
        "https://api.scraperapi.com/",
        params=payload,
        headers=headers,
        timeout=120
    )
    return response.text

@app.get("/")
def health():
    return {"status": "running"}

@app.post("/check-review")
def check_review(data: CheckRequest):
    text = scrape_page(data.url)
    text_lower = text.lower()

    owner_reply_exists = any(
        phrase.lower() in text_lower for phrase in OWNER_REPLY_PHRASES
    )

    return {
        "owner_reply": owner_reply_exists,
        "status": "OWNER RESPONSE FOUND" if owner_reply_exists else "RESPONSE REMOVED",
        "url": data.url
    }

@app.post("/debug-review")
def debug_review(data: CheckRequest):
    text = scrape_page(data.url)

    idx = text.lower().find("response")
    context_around_response = text[max(0, idx-100):idx+300] if idx != -1 else "NOT FOUND"

    idx2 = text.lower().find("reply")
    context_around_reply = text[max(0, idx2-100):idx2+300] if idx2 != -1 else "NOT FOUND"

    idx3 = text.lower().find("owner")
    context_around_owner = text[max(0, idx3-100):idx3+300] if idx3 != -1 else "NOT FOUND"

    found_phrases = [p for p in OWNER_REPLY_PHRASES if p.lower() in text.lower()]

    return {
        "found_phrases": found_phrases,
        "page_length": len(text),
        "contains_consent": "consent.google.com" in text.lower(),
        "context_around_response": context_around_response,
        "context_around_reply": context_around_reply,
        "context_around_owner": context_around_owner,
    }
