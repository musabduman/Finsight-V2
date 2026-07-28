import os
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from backend.database.schema import UserRegister, UserLogin
from backend.database.db import get_db_connection, hash_password, verify_password

router = APIRouter()
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")


def create_token(email: str) -> str:
    """Kullanıcı için 7 gün geçerli bir oturum token'ı (JWT) üretir."""
    payload = {"sub": email, "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


# ---------------------------
# KAYIT OL (REGISTER)
# ---------------------------
@router.post("/register")
def register(user: UserRegister):
    """Yeni kullanıcı oluşturur; e-posta zaten kayıtlıysa 400 döner."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email=%s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı.")

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (user.name, user.email, hash_password(user.password))
        )
        conn.commit()

        return {
            "success": True,
            "token": create_token(user.email),
            "user": {"name": user.name, "email": user.email, "plan": "free"}
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")
    finally:
        cursor.close()
        conn.close()


# ---------------------------
# GİRİŞ YAP (LOGIN)
# ---------------------------
@router.post("/login")
def login(user: UserLogin):
    """E-posta + şifreyi doğrular, başarılıysa oturum token'ı döner."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT name, email, password, plan FROM users WHERE email=%s",
            (user.email,)
        )
        db_user = cursor.fetchone()

        if not db_user or not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Hatalı e-posta veya şifre!")

        return {
            "success": True,
            "token": create_token(db_user["email"]),
            "user": {"name": db_user["name"], "email": db_user["email"], "plan": db_user["plan"]}
        }
    finally:
        cursor.close()
        conn.close()