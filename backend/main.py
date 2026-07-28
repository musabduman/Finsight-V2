from dotenv import load_dotenv
load_dotenv()  # DATABASE_URL, JWT_SECRET vb. .env'den okunsun diye db.py import edilmeden önce çalışmalı

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <-- YENİ EKLENDİ

from backend.database.db import init_db
from backend.database.auth import router as auth_router
from backend.ai.llm import router as chat_router

app = FastAPI(title="FinSight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # prod'da buraya kendi frontend domain'ini yaz
    allow_methods=["*"],
    allow_headers=["*"],
)

# <-- YENİ EKLENDİ: Frontend klasörünü statik dosya olarak dışarı açıyoruz
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.on_event("startup")
def on_startup():
    """Uygulama ayağa kalkarken Supabase'de users tablosunu yoksa oluşturur."""
    init_db()


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])


@app.get("/")
def health():
    """Basit sağlık kontrolü."""
    return {
        "status": "ok", 
        "message": "FinSight API çalışıyor. Arayüz için /frontend/finsight-v2.html adresine gidin."
    }