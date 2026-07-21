import os
import bcrypt
import psycopg2
import psycopg2.extras

# Supabase > Project Settings > Database > Connection string (URI) buraya .env'den gelecek
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Supabase Postgres'ine dict-satır döndüren bir bağlantı açar."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    """users tablosunu yoksa oluşturur (uygulama açılışında bir kere çağrılır)."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            plan TEXT NOT NULL DEFAULT 'free',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def hash_password(password: str) -> str:
    """Ham şifreyi bcrypt ile hash'ler."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Girilen şifreyi veritabanındaki hash ile karşılaştırır."""
    return bcrypt.checkpw(password.encode(), hashed.encode())