"""
Günlük BIST hisse hareketlerini yfinance ile çeken endpoint.
- 30 dakika in-memory cache ile rate limit'e karşı korunur
- Veri gelmezse son geçerli cache'i döner (stale flag ile)
"""
import time
import yfinance as yf
from fastapi import APIRouter

router = APIRouter()

# Takip edilen BIST hisseleri — ihtiyaca göre büyütülebilir
BIST_TICKERS = [
    "THYAO", "AKBNK", "GARAN", "EREGL", "ASTOR",
    "BIMAS", "KCHOL", "SISE", "TCELL", "FROTO",
    "ISCTR", "TOASO", "ARCLK", "KOZAL", "SAHOL",
]

SECTOR_MAP = {
    "THYAO": "havacılık",
    "AKBNK": "bankacılık",
    "GARAN": "bankacılık",
    "EREGL": "demir-çelik",
    "ASTOR": "enerji",
    "BIMAS": "perakende",
    "KCHOL": "holding",
    "SISE": "cam & kimya",
    "TCELL": "telekom",
    "FROTO": "otomotiv",
    "ISCTR": "bankacılık",
    "TOASO": "otomotiv",
    "ARCLK": "beyaz eşya",
    "KOZAL": "altın madenciliği",
    "SAHOL": "holding",
}

# Basit in-memory cache
_cache: dict = {"data": None, "ts": 0.0}
CACHE_TTL = 30 * 60  # 30 dakika


def _fetch_movers(tickers: list[str], top_n: int = 5) -> list[dict]:
    """Her ticker için son 2 günlük kapanışı çekip değişim yüzdesini hesaplar."""
    results = []
    for sym in tickers:
        try:
            hist = yf.Ticker(f"{sym}.IS").history(period="2d")
            if len(hist) < 2:
                continue
            prev = float(hist["Close"].iloc[-2])
            last = float(hist["Close"].iloc[-1])
            pct = round((last - prev) / prev * 100, 2)
            results.append(
                {
                    "symbol": sym,
                    "close": round(last, 2),
                    "change_pct": pct,
                    "direction": "up" if pct >= 0 else "down",
                    "sector": SECTOR_MAP.get(sym, "diğer"),
                }
            )
        except Exception as e:
            print(f"⚠️  {sym}.IS verisi alınamadı: {e}")
            continue

    # Mutlak değere göre sırala (en çok hareket eden önce)
    results.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return results[:top_n]


@router.get("/daily")
def daily_movers():
    """
    Günün en çok hareket eden 5 BIST hissesini döner.
    Sonuçlar 30 dakika boyunca cache'lenir.
    """
    global _cache
    now = time.time()

    # Cache geçerliyse direkt dön
    if _cache["data"] and (now - _cache["ts"]) < CACHE_TTL:
        return {"success": True, "data": _cache["data"], "cached": True}

    data = _fetch_movers(BIST_TICKERS, top_n=5)

    if not data:
        # Yeni veri gelmedi — eski cache'i stale flag ile dön
        if _cache["data"]:
            return {
                "success": True,
                "data": _cache["data"],
                "cached": True,
                "stale": True,
                "message": "yfinance'den yeni veri alınamadı, önceki veri gösteriliyor.",
            }
        return {"success": False, "data": [], "message": "BIST verisi alınamadı."}

    _cache = {"data": data, "ts": now}
    return {"success": True, "data": data, "cached": False}
