from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Mobil ilova to'siqsiz ulanishi uchun CORS ruxsatnomasi
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
        # HTML'ni saytdan tortib olish
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        classes = []
        table = soup.find('table')
        
        if not table:
            return {"error": "Jadval topilmadi yoki sayt strukturasi o'zgargan"}

        rows = table.find_all('tr')
        
        # Birinchi sarlavha qatorini tashlab ketamiz (rows[1:])
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4:
                classes.append({
                    "time": cols[0].text.strip(),
                    "subject": cols[1].text.strip(),
                    "type": cols[2].text.strip(),
                    "room": cols[3].text.strip()
                })
        
        # Toza JSON formatida qaytarish
        return classes
    except Exception as e:
        return {"error": str(e)}