# FinSight AI V2 📈

🌍 [Türkçe](#türkçe) | [English](#english)

---

<a id="türkçe"></a>
## 🇹🇷 Türkçe

Yapay zeka destekli, Borsa İstanbul (BIST) hisse senedi hareketlerini geçmiş veri, teknik sinyaller ve haber akışıyla açıklayan RAG tabanlı finansal analiz asistanı. 

FinSight geleceği tahmin etmez; piyasadaki güncel hareketleri tarihsel örüntülerle eşleştirerek kullanıcılara anlamlı ve veri odaklı içgörüler sunar.

### 🚀 Özellikler
* **RAG Tabanlı Hisse Analizi:** Kullanıcı sorularını (`THYAO neden yükseldi?`), pgvector ile vektör uzayında arayarak geçmiş benzer haber ve teknik kırılımlarla eşleştirir.
* **Yerel LLM Entegrasyonu:** Veri gizliliği ve esneklik için Ollama üzerinden çalışır (Metin işleme için `llama3.1`, embedding için `bge-m3`).
* **Günlük Piyasa Özeti:** Hacim kırılımlarını (breakout) tespit eden sinyal algoritmaları ve otomatik haber tarayıcı (`news_ingest.py`).
* **Modüler Frontend:** Herhangi bir framework'e bağımlı olmayan, temiz ve performanslı Vanilla HTML/CSS/JS arayüzü.
* **Kullanıcı ve Rol Yönetimi:** JWT tabanlı güvenli oturum yönetimi, misafir/pro kullanıcı soru limitasyonları.

### 🛠️ Teknoloji Yığını
* **Backend:** Python, FastAPI, yfinance, PyJWT
* **Veritabanı:** PostgreSQL (Supabase), pgvector eklentisi, psycopg2
* **Yapay Zeka:** Ollama (Llama 3.1 & BGE-M3)
* **Frontend:** Vanilla HTML, CSS, JavaScript (FastAPI `StaticFiles` ile sunulur)

### 📂 Proje Yapısı
```text
FINSIGHT AI V2/
├── backend/
│   ├── ai/
│   │   ├── embeddings.py   # Metinleri vektöre çeviren Ollama entegrasyonu
│   │   └── llm.py          # Sistem promptu ve cevap üretme mantığı
│   ├── database/
│   │   ├── auth.py         # JWT oluşturma, Kayıt/Giriş endpoint'leri
│   │   ├── db.py           # Supabase bağlantısı, tablo oluşturma, pgvector sorguları
│   │   └── schema.py       # Pydantic veri modelleri
│   ├── main.py             # FastAPI ana uygulama ve middleware/router ayarları
│   └── news_ingest.py      # BIST haber/fiyat verilerini çekip veritabanına işleyen script
├── frontend/
│   ├── css/
│   │   └── style.css       # Özelleştirilmiş arayüz tasarımları
│   ├── js/
│   │   └── app.js          # Chatbot mantığı, UI state yönetimi ve API istekleri
│   └── finsight-v2.html    # Tek sayfalık ana arayüz şablonu
├── requirements.txt        # Python bağımlılıkları
└── README.md               # Proje dokümantasyonu