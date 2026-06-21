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
    "Svar från ägaren",
    "Svar fra ejeren",
    "Vastaus omistajalta",
    "Resposta do proprietário",
    "Odpowiedź właściciela",
    "Ответ владельца",
    "Yanıt: İşletme sahibi",
    "オーナーからの返信",
    "来自业主的回复",
    "來自業主的回覆",
    "업주의 답변",
    "Réponse de l'établissement",
    "owner response",
    "Owner's response",
]

class CheckRequest(BaseModel):
    url: str

@app.get("/")
def health():
    return {"status": "running"}

@app.post("/check-review")
def check_review(data: CheckRequest):
    url = data.url

    payload = {
        "api_key": SCRAPER_API_KEY,
        "url": url,
        "render": "true",
        "country_code": "de"
    }

    response = requests.get(
        "https://api.scraperapi.com/",
        params=payload,
        timeout=120
    )

    text = response.text
    text_lower = text.lower()

    owner_reply_exists = any(
        phrase.lower() in text_lower for phrase in OWNER_REPLY_PHRASES
    )

    return {
        "owner_reply": owner_reply_exists,
        "status": "OWNER RESPONSE FOUND" if owner_reply_exists else "RESPONSE REMOVED",
        "url": url
    }

# DEBUG endpoint - remove after testing
@app.post("/debug-review")
def debug_review(data: CheckRequest):
    url = data.url

    payload = {
        "api_key": SCRAPER_API_KEY,
        "url": url,
        "render": "true",
        "country_code": "de"
    }

    response = requests.get(
        "https://api.scraperapi.com/",
        params=payload,
        timeout=120
    )

    text = response.text

    # Check which phrases are found
    found_phrases = [p for p in OWNER_REPLY_PHRASES if p.lower() in text.lower()]

    return {
        "found_phrases": found_phrases,
        "page_length": len(text),
        "contains_review_word": "review" in text.lower(),
        "contains_response": "response" in text.lower(),
        "first_2000_chars": text[:2000]
    }
