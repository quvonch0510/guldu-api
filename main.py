from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Bot loyihangizdagi parser.py funksiyalarini ulash uchun
# (Agar parser.py bitta papkada bo'lsa)
from parser import get_schedule_text, search_group_id

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
async def get_schedule(group: str = "9-24AT"):
    """
    Standart bo'yicha guruh nomini qabul qiladi va parser yordamida
    to'g'ridan-to'g'ri GulDU bazasidan toza ma'lumot qaytaradi.
    """
    try:
        # Guruh ID raqamini topamiz (xuddi botdagi kabi)
        group_id = await search_group_id(group)
        
        if not group_id:
            return {"error": f"'{group}' guruhi topilmadi"}

        # Bot foydalanadigan parser orqali jadvalni matn yoki massiv shaklida olamiz
        # Agar parseringiz JSON qaytarsa uni to'g'ridan-to'g'ri ishlatamiz
        from parser import get_schedule_json # Agar parser.py da shunday funksiya bo'lsa
        
        # Yoki mavjud get_schedule_text dan foydalanamiz
        schedule_text = await get_schedule_text(group_id, group, "haftalik")
        
        return {"group": group, "schedule": schedule_text}
    except Exception as e:
        return {"error": str(e)}
