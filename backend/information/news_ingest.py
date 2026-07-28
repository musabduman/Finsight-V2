import yfinance as yf
from datetime import datetime
from backend.database.db import save_news_event
from backend.ai.embeddings import embed_text

TICKERS = ["THYAO", "AKBNK", "EREGL", "ASTOR"]  # takip listesini burada büyüt


def fetch_price_history(ticker: str, period: str = "6mo"):
    """Yahoo'dan (.IS suffix'iyle) günlük OHLCV fiyat verisini çeker."""
    return yf.Ticker(f"{ticker}.IS").history(period=period)


def detect_breakout(hist, window: int = 20, vol_multiplier: float = 2.0):
    """Son günü, hacim eşliğinde N-günlük ortalamayı kırıp kırmadığına göre etiketler."""
    if len(hist) < window + 1:
        return None
    avg_close = hist["Close"].iloc[-window - 1:-1].mean()
    avg_vol = hist["Volume"].iloc[-window - 1:-1].mean()
    last = hist.iloc[-1]
    if last["Volume"] < avg_vol * vol_multiplier:
        return None
    if last["Close"] > avg_close * 1.03:
        return "breakout_up"
    if last["Close"] < avg_close * 0.97:
        return "breakout_down"
    return None


def price_change_pct(hist, days: int = 3):
    """Son N günün toplam getirisini yüzde olarak döner; RAG'daki 'sonra ne oldu' etiketi budur."""
    if len(hist) < days + 1:
        return None
    start, end = hist["Close"].iloc[-days - 1], hist["Close"].iloc[-1]
    return round(float((end - start) / start * 100), 2)


def fetch_news(ticker: str):
    """yfinance'in Yahoo haber akışını çeker. NOT: BIST kapsamı zayıf, ileride KAP/TR kaynak eklenmeli."""
    return yf.Ticker(f"{ticker}.IS").news or []


def ingest_ticker(ticker: str):
    """Bir hisse için fiyat+haber çekip teknik sinyal ve embedding'le news_events'e kaydeder."""
    hist = fetch_price_history(ticker)
    signal = detect_breakout(hist)
    change = price_change_pct(hist)

    for item in fetch_news(ticker):
        # yfinance yeni sürümlerde haberi 'content' alt sözlüğünde döndürüyor, eskiler için de fallback
        content = item.get("content", item)
        title = content.get("title", "")
        if not title:
            continue
        summary = content.get("summary") or title
        published = content.get("pubDate", datetime.utcnow().isoformat())

        save_news_event({
            "ticker": ticker,
            "published_at": published,
            "title": title,
            "content": summary,
            "source": "yahoo",
            "technical_signal": signal,
            "price_change_pct": change,
            "embedding": embed_text(f"{title}. {summary}"),
        })


if __name__ == "__main__":
    # Elle çalıştırmak için: python news_ingest.py (ileride cron/scheduled job'a bağlanabilir)
    for t in TICKERS:
        ingest_ticker(t)
        print(f"{t} işlendi.")