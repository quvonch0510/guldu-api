from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import aiohttp
from parser import search_group_id, BASE_URL

app = FastAPI()

# Mobil ilova va boshqa platformalar uchun CORS ruxsatnomasi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Guldu Dars Jadvali API ishlayapti! 🚀"}

@app.get("/api/dars")
async def get_schedule(group: str = Query("9-24AT", description="Guruh nomi, masalan: 9-24AT")):
    """
    Berilgan guruh nomi bo'yicha jadvalni parser orqali olib,
    React Native ilovasi talab qiladigan JSON formatida qaytaradi.
    """
    try:
        # 1. Guruh ID raqamini parser orqali topamiz
        group_id = await search_group_id(group)
        
        if not group_id:
            return {"error": f"'{group}' guruhi topilmadi"}

        # 2. Guruh jadvali HTML sahifasini yuklab olamiz
        url = f"{BASE_URL}/ll.php"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={"datagroupid": str(group_id)}) as response:
                if response.status != 200:
                    return {"error": "Universitet serveridan ma'lumot olib bo'lmadi"}
                html = await response.text()

        if not html.strip() or "dars jadvali" not in html.lower():
            return []

        # 3. BeautifulSoup yordamida jadvalni qismlarga ajratib JSON qilamiz
        soup = BeautifulSoup(html, 'html.parser')
        classes = []

        cols = soup.find_all('div', class_='col-md-12')
        for col in cols:
            table = col.find('table')
            if table:
                # Dars vaqti va juftlik
                time_th = table.find('th')
                time_text = " ".join(time_th.text.split()) if time_th else ""

                tds = table.find_all('td')
                if len(tds) >= 3:
                    # Fan turi va nomi
                    s_parts = list(tds[1].stripped_strings)
                    s_type = s_parts[0] if len(s_parts) > 1 else "Dars"
                    s_name = " ".join(s_parts[1:]) if len(s_parts) > 1 else "".join(s_parts)

                    # Auditoriya xonasi
                    r_parts = list(tds[2].stripped_strings)
                    room = " ".join(r_parts[1:]) if len(r_parts) > 1 else "".join(r_parts)
                    if not room:
                        room = "Noma'lum"

                    classes.append({
                        "time": time_text or "Vaqti ko'rsatilmagan",
                        "subject": s_name or "Noma'lum fan",
                        "type": s_type,
                        "room": room
                    })

        return classes
    except Exception as e:
        return {"error": str(e)}
