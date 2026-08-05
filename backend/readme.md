# ENGLİSH

# FinSight AI

FinSight AI is a BIST (Borsa Istanbul) stock analysis platform, developed in parallel with [Ghost](./ghost-README.md). It was submitted to TEKNOFEST in the Financial Technologies category and is one of two core projects featured in the developer's internship CV.

## Current stack

- **RAG**: Pinecone with `multilingual-e5-large` embeddings.
- **LLM layer**: dual-agent architecture combining Gemini and Ollama.
- **Auth / storage**: Supabase / PostgreSQL.
- **Frontend**: deployed on Vercel.
- **Backend**: FastAPI, deployed on Render — unified from a previously split backend into a single `main.py` with routers (`auth.py`, `analysis.py`).
- **ML layer**: migrated from PyTorch to scikit-learn's `RandomForestRegressor`, significantly reducing deployment size.

## Notable fixes

- Full backend security audit: replaced unsalted SHA-256 password hashing with bcrypt, fixed unauthenticated endpoints.
- Patched security vulnerabilities in watchlist endpoints.
- Fixed CORS trailing-slash failures.
- Corrected HTTP method mismatches (GET vs POST).
- Migrated the frontend from Streamlit to HTML/JS.
- Mitigated `yfinance` rate limiting issues.
- Earlier chat interface used Streamlit + Groq before migrating to the current architecture.

## Repositioning: v2

The original FinSight AI is considered a **student project**; a v2 direction is being planned as the actual product — built separately, not as a rewrite of the current app.

**Why the change:** prediction/analysis stability was identified as a core weakness of a forecasting-oriented product. The new direction repositions FinSight around **education rather than prediction**.

**v2 concept**: a case-analysis chatbot that explains *historical* stock movements (not future predictions), with fast Q&A and visual, chart-based explanations.

- **Daily format**: 2 stock charts per day, each explaining why the move happened — framed as historical-pattern observation, not forecasting.
- **Free tier / homepage**: shows 2–4 randomly selected stocks each day with explanations for their movement or stability, plus roughly 20 chatbot questions/day about them.
- **Pro tier**: users can query any stock of their choice (e.g., a portfolio holding) via chat or homepage search, and get a chart plus a news-backed explanation of its movement.
- **Pricing**: usage-tiered, inspired by AI API cost-based pricing — for example, roughly 150–200 TL/month for ~20 messages/day, and roughly 400–500 TL/month for ~40 messages/day (under consideration).

## v2 technical direction

- Backend structured as `main.py` / `auth.py` / `llm.py`.
- Supabase (Postgres) for storage, with tables created directly from code.
- Ollama for the LLM layer.
- **Vector store**: consolidating on Supabase **pgvector** instead of Pinecone; keeping `multilingual-e5-large` for embeddings.
- **No LangChain** — RAG retrieval is written manually.
- **RAG design**: retrieves historical news + price-reaction analogies for a given stock, rather than doing plain document Q&A.
- **Data ingestion**: `yfinance` for BIST price/technical data and news, with plans to add KAP and other Turkish news sources later.

## Status

Actively being redesigned. The current app remains live as-is while v2 is built as a separate product.

# TÜRKCE

# FinSight AI

FinSight AI, [Ghost](./ghost-README.tr.md) ile paralel olarak geliştirilen bir BIST (Borsa İstanbul) hisse senedi analiz platformu. TEKNOFEST'e Finansal Teknolojiler kategorisinde başvuru olarak sunuldu ve geliştiricinin staj CV'sinde yer alan iki ana projeden biri.

## Mevcut teknoloji yığını

- **RAG**: `multilingual-e5-large` embedding'leriyle Pinecone.
- **LLM katmanı**: Gemini ve Ollama'yı birleştiren çift ajan (dual-agent) mimarisi.
- **Auth / depolama**: Supabase / PostgreSQL.
- **Frontend**: Vercel üzerinde deploy edilmiş.
- **Backend**: FastAPI, Render üzerinde deploy edilmiş — daha önce bölünmüş olan backend, router'lı (`auth.py`, `analysis.py`) tek bir `main.py`'de birleştirildi.
- **ML katmanı**: PyTorch'tan scikit-learn'in `RandomForestRegressor`'ına geçildi, bu da deployment boyutunu ciddi şekilde azalttı.

## Öne çıkan düzeltmeler

- Kapsamlı bir backend güvenlik denetimi: tuzsuz (unsalted) SHA-256 şifre hash'leme yerine bcrypt kullanımına geçildi, kimlik doğrulaması olmayan endpoint'ler düzeltildi.
- Watchlist endpoint'lerindeki güvenlik açıkları yamalandı.
- CORS trailing-slash hatalarının düzeltilmesi.
- HTTP metod uyumsuzluklarının (GET vs POST) düzeltilmesi.
- Frontend'in Streamlit'ten HTML/JS'e taşınması.
- `yfinance` rate limiting sorunlarının hafifletilmesi.
- Şu anki mimariye geçilmeden önce, sohbet arayüzü Streamlit + Groq kullanıyordu.

## Yeniden konumlandırma: v2

Orijinal FinSight AI bir **öğrenci projesi** olarak görülüyor; asıl ürün olarak planlanan v2 yönü ayrı bir ürün olarak inşa ediliyor — mevcut uygulamanın yeniden yazımı olarak değil.

**Değişimin nedeni:** tahmin/analiz istikrarının, tahmin odaklı bir ürünün temel zayıflığı olduğu tespit edildi. Yeni yön, FinSight'ı **tahmin yerine eğitim** etrafında konumlandırıyor.

**v2 konsepti**: gelecekteki değil, *geçmiş* hisse senedi hareketlerini açıklayan, hızlı soru-cevap ve grafik tabanlı görsel açıklamalar sunan bir vaka analizi (case-analysis) chatbot'u.

- **Günlük format**: günde 2 hisse grafiği, her biri hareketin nedenini açıklıyor — tahmin değil, geçmişe dönük örüntü gözlemi olarak sunuluyor.
- **Ücretsiz katman / anasayfa**: her gün rastgele seçilen 2-4 hisseyi, hareketlerinin veya durağanlığının nedenleriyle birlikte gösteriyor; ayrıca bunlar hakkında günde yaklaşık 20 chatbot sorusu hakkı.
- **Pro katman**: kullanıcılar seçtikleri herhangi bir hisseyi (örn. portföylerindeki bir hisse) sohbet veya anasayfa arama üzerinden sorgulayabiliyor ve hareketi için grafik + haber destekli bir açıklama alıyor.
- **Fiyatlandırma**: AI API maliyet tabanlı fiyatlandırmadan esinlenen, kullanım katmanlı bir model — örneğin günde ~20 mesaj için ayda ~150-200 TL, günde ~40 mesaj için ayda ~400-500 TL (değerlendirme aşamasında).

## v2 teknik yönü

- Backend `main.py` / `auth.py` / `llm.py` yapısında kuruluyor.
- Depolama için Supabase (Postgres), tablolar doğrudan kod üzerinden oluşturuluyor.
- LLM katmanı için Ollama.
- **Vektör deposu**: Pinecone yerine Supabase **pgvector**'da konsolide olma kararı alındı; embedding için `multilingual-e5-large` korundu.
- **LangChain yok** — RAG retrieval manuel olarak yazılıyor.
- **RAG tasarımı**: düz doküman soru-cevabı yerine, belirli bir hisse için geçmiş haber + fiyat-tepkisi analojilerini buluyor.
- **Veri girişi**: BIST fiyat/teknik veri ve haberler için `yfinance` kullanılıyor; ileride KAP ve diğer Türkçe haber kaynaklarının eklenmesi planlanıyor.

## Durum

Aktif olarak yeniden tasarlanıyor. v2 ayrı bir ürün olarak inşa edilirken, mevcut uygulama olduğu gibi canlı kalmaya devam ediyor.