from fastapi import FastAPI
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import time

app = FastAPI()

class CheckRequest(BaseModel):
    url: str

@app.get("/")
def health():
    return {"status": "running"}

@app.post("/check-review")
def check_review(data: CheckRequest):
    url = data.url
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process"
            ]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="en-US"
        )
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(3)
            text = page.locator("body").inner_text(timeout=30000)
        finally:
            browser.close()
    
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
