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
    # Extra patterns for JS-rendered content
    "reviewReply",
    "ownerResponse",
    "owner_response",
    "replyText",
    "\"reply\"",
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
        "country_code": "us",
        "keep_headers": "true",
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

@app.post("/debug-review")
def debug_review(data: CheckRequest):
    url = data.url

    payload = {
        "api_key": SCRAPER_API_KEY,
        "url": url,
        "render": "true",
        "country_code": "us",
        "keep_headers": "true",
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

    text = response.text

    # Search for the word "response" and grab surrounding context
    idx = text.lower().find("response")
    context_around_response = text[max(0, idx-100):idx+200] if idx != -1 else "NOT FOUND"

    # Also search for "reply"
    idx2 = text.lower().find("reply")
    context_around_reply = text[max(0, idx2-100):idx2+200] if idx2 != -1 else "NOT FOUND"

    found_phrases = [p for p in OWNER_REPLY_PHRASES if p.lower() in text.lower()]

    return {
        "found_phrases": found_phrases,
        "page_length": len(text),
        "contains_consent": "consent.google.com" in text.lower(),
        "context_around_response": context_around_response,
        "context_around_reply": context_around_reply,
    }
