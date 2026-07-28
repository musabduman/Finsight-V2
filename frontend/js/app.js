/**
 * FinSight AI V2 — Frontend Uygulama Mantığı
 * Render backend ile gerçek API entegrasyonu.
 *
 * ⚠️  DEPLOY SONRASI: API_BASE değişkenini Render URL'inle güncelle.
 */

// ─── CONFIG ─────────────────────────────────────────────────────────────────
const API_BASE = 'https://finsight-api.onrender.com'; // ← Render URL buraya

const SECTOR_MAP = {
  THYAO: 'havacılık',  AKBNK: 'bankacılık',  GARAN: 'bankacılık',
  EREGL: 'demir-çelik', ASTOR: 'enerji',      BIMAS: 'perakende',
  KCHOL: 'holding',    SISE:  'cam & kimya',  TCELL: 'telekom',
  FROTO: 'otomotiv',   ISCTR: 'bankacılık',  TOASO: 'otomotiv',
  ARCLK: 'beyaz eşya', KOZAL: 'altın mad.',  SAHOL: 'holding',
};

const GUEST_LIMIT = 3;
const FREE_LIMIT  = 20;

const state = {
  loggedIn: false,
  guestCount: 0,
  usedCount: 0,
  token: null,
  user: null,
  isSignupMode: false,
};

// ─── NAVIGATION ─────────────────────────────────────────────────────────────
const navToggle = document.getElementById('navToggle');
const navLinks  = document.getElementById('navLinks');
navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
navLinks.querySelectorAll('a').forEach(a =>
  a.addEventListener('click', () => navLinks.classList.remove('open'))
);

const sections   = document.querySelectorAll('.section[id]');
const navAnchors = navLinks.querySelectorAll('a[data-section]');
window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => {
    const rect = s.getBoundingClientRect();
    if (rect.top <= 120 && rect.bottom > 120) current = s.id;
  });
  navAnchors.forEach(a =>
    a.classList.toggle('active', a.dataset.section === current)
  );
});

// ─── SIDE PANEL ─────────────────────────────────────────────────────────────
const fabBtn       = document.getElementById('fabBtn');
const sidePanel    = document.getElementById('sidePanel');
const panelOverlay = document.getElementById('panelOverlay');
const panelClose   = document.getElementById('panelClose');
const loginView    = document.getElementById('loginView');
const chatView     = document.getElementById('chatView');
const planBadge    = document.getElementById('planBadge');

document.getElementById('ctaBtn').addEventListener('click', () => openPanel());
fabBtn.addEventListener('click', () => openPanel());
panelClose.addEventListener('click', closePanel);
panelOverlay.addEventListener('click', closePanel);
document.getElementById('openChatFromSection').addEventListener('click', () => openPanel());

function openPanel(prefillQuestion) {
  sidePanel.classList.add('open');
  panelOverlay.classList.add('open');
  if (prefillQuestion) {
    if (state.loggedIn || state.guestCount < GUEST_LIMIT) {
      showChatView();
      respondTo(prefillQuestion);
    } else {
      showLoginView();
    }
  }
}
function closePanel() {
  sidePanel.classList.remove('open');
  panelOverlay.classList.remove('open');
}

// ─── VIEWS ──────────────────────────────────────────────────────────────────
function showLoginView() {
  loginView.style.display = 'flex';
  chatView.style.display  = 'none';
}
function showChatView() {
  loginView.style.display = 'none';
  chatView.style.display  = 'flex';
  updateUsageText();
}
function updateUsageText() {
  const usageText = document.getElementById('usageText');
  if (state.loggedIn) {
    usageText.textContent = `${state.usedCount}/${FREE_LIMIT} soru kullanıldı`;
    planBadge.textContent = state.user?.plan === 'pro' ? 'Pro' : 'Free';
  } else {
    usageText.textContent = `${state.guestCount}/${GUEST_LIMIT} misafir sorusu`;
    planBadge.textContent = 'Misafir';
  }
}

// ─── AUTH ───────────────────────────────────────────────────────────────────
document.getElementById('continueGuest').addEventListener('click', () => {
  showChatView();
  if (chatLogEl().children.length === 0) {
    addBubble(
      'Merhaba! Bir hisse hakkında soru sorabilirsin — örn: "THYAO neden yükseldi?"',
      'bot', 'FinSight'
    );
  }
});

document.getElementById('authSwitchSignup').addEventListener('click', () => {
  state.isSignupMode = !state.isSignupMode;
  const submitBtn = document.getElementById('authSubmit');
  const leadText  = document.querySelector('.panel-lead');
  const switchBtn = document.getElementById('authSwitchSignup');

  if (state.isSignupMode) {
    submitBtn.textContent = 'Kayıt ol';
    leadText.textContent  = 'Hesap oluştur, günlük 20 soru hakkın hemen aktif olsun.';
    switchBtn.textContent = 'Zaten hesabın var mı? Giriş yap';
  } else {
    submitBtn.textContent = 'Giriş yap';
    leadText.textContent  = 'Giriş yap, günlük 20 soru hakkınla sınırsız hisse sorgula.';
    switchBtn.textContent = 'Hesabın yok mu? Kayıt ol';
  }
});

document.getElementById('authSubmit').addEventListener('click', async () => {
  const email    = document.getElementById('authEmail').value.trim();
  const password = document.getElementById('authPassword').value;
  if (!email || !password) {
    document.getElementById('authEmail').focus();
    return;
  }

  const submitBtn = document.getElementById('authSubmit');
  submitBtn.disabled    = true;
  submitBtn.textContent = '...';

  try {
    const endpoint = state.isSignupMode ? '/auth/register' : '/auth/login';
    const body     = state.isSignupMode
      ? { name: email.split('@')[0], email, password }
      : { email, password };

    const res  = await fetch(`${API_BASE}${endpoint}`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body),
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || 'İşlem başarısız.');
      return;
    }

    state.loggedIn  = true;
    state.token     = data.token;
    state.user      = data.user;
    state.usedCount = 0;

    showChatView();
    const greeting = state.isSignupMode
      ? `Hoş geldin, ${data.user.name}! Hesabın oluşturuldu.`
      : `Tekrar hoş geldin, ${data.user.name}!`;
    addBubble(`${greeting} Günde ${FREE_LIMIT} soru hakkın var.`, 'bot', 'FinSight');

  } catch (e) {
    alert('Sunucuya bağlanılamadı. Lütfen tekrar deneyin.');
  } finally {
    submitBtn.disabled    = false;
    submitBtn.textContent = state.isSignupMode ? 'Kayıt ol' : 'Giriş yap';
  }
});

document.getElementById('authGoogle').addEventListener('click', () => {
  alert('Google ile giriş özelliği çok yakında eklenecek!');
});

document.getElementById('logoutBtn').addEventListener('click', () => {
  state.loggedIn = false;
  state.token    = null;
  state.user     = null;
  chatLogEl().innerHTML = '';
  showLoginView();
});

// ─── CHAT ───────────────────────────────────────────────────────────────────
const chatInput = document.getElementById('chatInput');
const chatSend  = document.getElementById('chatSend');

function chatLogEl() { return document.getElementById('chatLog'); }

function addBubble(text, type, label) {
  const div = document.createElement('div');
  div.className = `bubble ${type}`;
  if (label) {
    const lbl = document.createElement('span');
    lbl.className   = 'lbl';
    lbl.textContent = label;
    div.appendChild(lbl);
    div.appendChild(document.createTextNode(text));
  } else {
    div.textContent = text;
  }
  chatLogEl().appendChild(div);
  chatLogEl().scrollTop = chatLogEl().scrollHeight;
  return div;
}

function showLimitReached() {
  const div = document.createElement('div');
  div.className = 'limit-notice';
  div.innerHTML = state.loggedIn
    ? `Bugünkü ${FREE_LIMIT} soru hakkın doldu. <button id="upsellBtn">Pro'ya geç</button>, sınırsız sor.`
    : `Misafir sorunu doldu. <button id="loginFromLimit">Giriş yap</button>, günde ${FREE_LIMIT} soru kazan.`;
  chatLogEl().appendChild(div);
  chatLogEl().scrollTop = chatLogEl().scrollHeight;

  if (!state.loggedIn) {
    document.getElementById('loginFromLimit').addEventListener('click', showLoginView);
  } else {
    document.getElementById('upsellBtn').addEventListener('click', () => {
      closePanel();
      document.getElementById('fiyat').scrollIntoView({ behavior: 'smooth' });
    });
  }
}

async function respondTo(question) {
  if (!state.loggedIn && state.guestCount >= GUEST_LIMIT) { showLimitReached(); return; }
  if (state.loggedIn  && state.usedCount  >= FREE_LIMIT)  { showLimitReached(); return; }

  addBubble(question, 'user');
  if (state.loggedIn) { state.usedCount++; } else { state.guestCount++; }
  updateUsageText();

  // Yazıyor animasyonu
  const typing = document.createElement('div');
  typing.className = 'bubble bot typing';
  typing.innerHTML = '<span></span><span></span><span></span>';
  chatLogEl().appendChild(typing);
  chatLogEl().scrollTop = chatLogEl().scrollHeight;

  // Soruda geçen BIST ticker'ını bul
  const upper  = question.toUpperCase();
  const ticker = Object.keys(SECTOR_MAP).find(sym => upper.includes(sym)) || null;

  try {
    const headers = { 'Content-Type': 'application/json' };
    if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

    const res  = await fetch(`${API_BASE}/chat/ask`, {
      method:  'POST',
      headers,
      body:    JSON.stringify({ question, ticker }),
    });
    const data = await res.json();

    typing.remove();

    if (!res.ok) {
      addBubble(`⚠️ ${data.detail || 'Sunucu hatası.'}`, 'bot', 'FinSight');
      return;
    }

    addBubble(data.answer, 'bot', 'FinSight');

    // Kaynak göster (varsa)
    if (data.sources && data.sources.length > 0) {
      const srcDiv = document.createElement('div');
      srcDiv.className = 'sources';
      srcDiv.innerHTML = data.sources
        .map(s => `<span class="src-tag">${s.ticker} · ${new Date(s.published_at).toLocaleDateString('tr-TR')} · %${s.price_change_pct ?? '?'}</span>`)
        .join('');
      chatLogEl().appendChild(srcDiv);
      chatLogEl().scrollTop = chatLogEl().scrollHeight;
    }

  } catch (_e) {
    typing.remove();
    addBubble('⚠️ Sunucuya bağlanılamadı. Render servisi uyku modunda olabilir, 30 sn sonra tekrar dene.', 'bot', 'FinSight');
  }

  if (
    (state.loggedIn  && state.usedCount  >= FREE_LIMIT) ||
    (!state.loggedIn && state.guestCount >= GUEST_LIMIT)
  ) {
    showLimitReached();
  }
}

chatSend.addEventListener('click', () => {
  const q = chatInput.value.trim();
  if (!q) return;
  respondTo(q);
  chatInput.value = '';
});
chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') chatSend.click();
});

// ─── STOCK GRID (Gerçek Veri) ────────────────────────────────────────────────
async function loadDailyStocks() {
  const grid = document.querySelector('.stock-grid');
  if (!grid) return;

  // Yükleniyor durumu
  grid.innerHTML = `
    <div class="stock-loading">
      <span class="load-dot"></span><span class="load-dot"></span><span class="load-dot"></span>
      <span style="margin-left:8px;font-size:0.82rem;color:#5b6472;">BIST verisi yükleniyor...</span>
    </div>`;

  try {
    const res  = await fetch(`${API_BASE}/stocks/daily`);
    const json = await res.json();

    if (!json.success || !json.data.length) {
      grid.innerHTML = '<div class="stock-error">Veri alınamadı — daha sonra tekrar dene.</div>';
      return;
    }

    grid.innerHTML = '';
    json.data.forEach(stock => {
      const sign   = stock.direction === 'up' ? '+' : '';
      const card   = document.createElement('div');
      card.className       = 'stock-card';
      card.dataset.symbol  = stock.symbol;
      card.innerHTML = `
        <div class="row1">
          <span class="sym">${stock.symbol}</span>
          <span class="pct ${stock.direction}">${sign}${stock.change_pct}%</span>
        </div>
        <p class="why">Güncel kapanış: ${stock.close.toLocaleString('tr-TR')} TL — detay için tıkla.</p>
        <span class="tag">${stock.sector}</span>`;
      card.addEventListener('click', () =>
        openPanel(`${stock.symbol} neden ${stock.direction === 'up' ? 'yükseldi' : 'düştü'}?`)
      );
      grid.appendChild(card);
    });

    if (json.stale) {
      const note = document.createElement('p');
      note.style.cssText = 'font-size:0.72rem;color:#5b6472;margin-top:10px;font-family:monospace;';
      note.textContent = '⚠ Önbellekteki veriler gösteriliyor — yfinance geçici olarak ulaşılamaz.';
      grid.after(note);
    }

  } catch (_e) {
    grid.innerHTML = '<div class="stock-error">Sunucuya bağlanılamadı.</div>';
  }
}

// Sayfa yüklenince hisseleri çek
loadDailyStocks();