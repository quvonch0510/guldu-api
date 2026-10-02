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
    base_url = "https://data.guldu.uz/dars" # yoki asosiy sayt manzili
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Fakultetlar ro'yxatidan "Axborot texnologiyalari..." havolasini qidiramiz
        faculty_link = None
        for a in soup.find_all('a', href=True):
            if "Axborot texnologiyalari" in a.text or "fizika-matematika" in a.text:
                faculty_link = a['href']
                break
        
        # Agar havolani topa olmasa, yoki sahifa tuzilishi boshqacha bo'lsa
        # To'g'ridan-to'g'ri shu sahifaning o'zida table bor-yo'qligini tekshiramiz
        table = soup.find('table')
        
        if not table and faculty_link:
            # Agar fakultet havolasiga o'tish kerak bo'lsa
            if not faculty_link.startswith('http'):
                faculty_link = "https://data.guldu.uz/" + faculty_link.lstrip('/')
            
            fac_response = requests.get(faculty_link, headers=headers)
            fac_soup = BeautifulSoup(fac_response.text, 'html.parser')
            table = fac_soup.find('table')

        classes = []
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
        
        if not classes:
            return {"error": "Fakultet jadvali topilmadi, guruh havolasini aniqlash kerak"}

        return classes
    except Exception as e:
        return {"error": str(e)}
