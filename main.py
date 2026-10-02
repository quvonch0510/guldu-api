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
        
        # Sahifadagi barcha jadvallarni (table) qidirib topamiz
        tables = soup.find_all('table')
        
        classes = []
        
        # Har bir jadvalni ko'rib chiqamiz
        for table in tables:
            # Jadval oldidagi matnda "Axborot texnologiyalari" bor-yo'qligini tekshiramiz
            parent_text = table.parent.get_text() if table.parent else ""
            
            # Agar IT fakultetiga oid jadval topilsa yoki sahifada umuman jadval ko'p bo'lmasa
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
            if classes:
                break # Kerakli jadval topilsa, siklni to'xtatamiz

        # Agar maxsus shart bo'yicha topilmasa, sahifadagi birinchi topilgan jadvalni olib ko'ramiz
        if not classes and tables:
            rows = tables[0].find_all('tr')
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
            return {"error": "Sahifadan mos jadval topilmadi", "tables_found": len(tables)}

        return classes
    except Exception as e:
        return {"error": str(e)}
