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
    """users ve news_events (pgvector dahil) tablolarını yoksa oluşturur."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
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
    # Her satır: bir haber + o günkü teknik sinyal + haberden sonraki fiyat tepkisi (label) + embedding
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news_events (
            id SERIAL PRIMARY KEY,
            ticker TEXT NOT NULL,
            published_at TIMESTAMPTZ NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            source TEXT NOT NULL,
            technical_signal TEXT,
            price_change_pct NUMERIC,
            embedding VECTOR(1024),
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


def _vec_literal(vec: list) -> str:
    """Python float listesini pgvector'un beklediği '[0.1,0.2,...]' metin formatına çevirir."""
    return "[" + ",".join(str(x) for x in vec) + "]"


def save_news_event(event: dict):
    """Bir haber + teknik sinyal + embedding kaydını news_events tablosuna yazar."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO news_events
            (ticker, published_at, title, content, source, technical_signal, price_change_pct, embedding)
        VALUES
            (%(ticker)s, %(published_at)s, %(title)s, %(content)s, %(source)s,
             %(technical_signal)s, %(price_change_pct)s, %(embedding)s::vector)
    """, {**event, "embedding": _vec_literal(event["embedding"])})
    conn.commit()
    cur.close()
    conn.close()


def search_similar_events(embedding: list, ticker: str = None, k: int = 3):
    """Verilen embedding'e pgvector cosine mesafesiyle (<=>) en yakın k geçmiş olayı döner."""
    conn = get_db_connection()
    cur = conn.cursor()
    vec = _vec_literal(embedding)
    base_query = """
        SELECT ticker, published_at, title, technical_signal, price_change_pct,
               1 - (embedding <=> %s::vector) AS similarity
        FROM news_events
        {filter}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    if ticker:
        cur.execute(base_query.format(filter="WHERE ticker=%s"), (vec, ticker, vec, k))
    else:
        cur.execute(base_query.format(filter=""), (vec, vec, k))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows