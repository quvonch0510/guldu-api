from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Guldu API ishlayapti!"}

@app.get("/api/dars")
def get_schedule():
    url = "https://data.guldu.uz/dars"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sahifadagi barcha havolalarni yig'ib ko'rsatamiz
        links_info = []
        for a in soup.find_all('a', href=True):
            links_info.append({
                "text": a.text.strip()[:30], 
                "href": a['href']
            })
        
        return {
            "error": "Fakultet havolasini aniqlash uchun", 
            "links": links_info[:20]
        }
        
    except Exception as e:
        return {"error": str(e)}
