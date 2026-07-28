from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.database.db import init_db
from backend.database.auth import router as auth_router
from backend.ai.llm import router as chat_router
from backend.information.stocks import router as stocks_router

app = FastAPI(
    title="FinSight API",
    description="BIST hisse analiz asistanı — RAG tabanlı",
    version="2.0.0",
)

# CORS: Vercel frontend + yerel geliştirme
# Render deploy sonrası ALLOWED_ORIGINS env variable ile kısıtlayabilirsin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Uygulama ayağa kalkarken tabloları oluştur. DB yoksa sessizce geç."""
    try:
        init_db()
        print("✅ Veritabanı bağlantısı başarılı.")
    except Exception as e:
        print(f"⚠️  DB init başarısız (şimdilik sorun değil): {e}")


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(stocks_router, prefix="/stocks", tags=["stocks"])


@app.get("/")
def health():
    """Sağlık kontrolü — Render uptime check için."""
    return {"status": "ok", "message": "FinSight API çalışıyor 🚀"}