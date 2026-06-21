from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY", "")

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
        "render": "true",        # renders JavaScript
        "country_code": "de"     # use German IP for German reviews
    }

    response = requests.get(
        "https://api.scraperapi.com/",
        params=payload,
        timeout=120
    )

    text = response.text

    owner_reply_exists = any([
        "Response from the owner" in text,
        "Antwort vom Inhaber" in text,
        "Risposta del titolare" in text,
        "Réponse du propriétaire" in text
    ])

    return {
        "owner_reply": owner_reply_exists,
        "status": "OWNER RESPONSE FOUND" if owner_reply_exists else "RESPONSE REMOVED",
        "url": url
    }
