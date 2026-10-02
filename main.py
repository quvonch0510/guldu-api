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
        
        classes = []
        
        # 1-usul: Agar jadval table bo'lsa
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    classes.append({
                        "time": cols[0].text.strip(),
                        "subject": cols[1].text.strip(),
                        "type": cols[2].text.strip(),
                        "room": cols[3].text.strip()
                    })
        
        # 2-usul: Agar table topilmasa, sahifadagi barcha qatorlarni yoki class'larni qidirib ko'ramiz
        if not classes:
            # Saytning o'ziga xos tuzilmasini tekshirish uchun topilgan barcha elementlarni qaytaramiz
            # Bu yerda jadval qanday tuzilganini aniqlaymiz
            paragraphs = [p.text.strip() for p in soup.find_all(['div', 'span', 'li']) if p.text.strip()]
            return {"error": "Jadval topilmadi", "html_Snippet": paragraphs[:10]}

        return classes
    except Exception as e:
        return {"error": str(e)}
