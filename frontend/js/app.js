// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));

// Scroll-spy for nav active state
const sections = document.querySelectorAll('.section[id]');
const navAnchors = navLinks.querySelectorAll('a[data-section]');
window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => {
    const rect = s.getBoundingClientRect();
    if (rect.top <= 120 && rect.bottom > 120) current = s.id;
  });
  navAnchors.forEach(a => a.classList.toggle('active', a.dataset.section === current));
});

// ---- Floating panel: open/close ----
const fabBtn = document.getElementById('fabBtn');
const sidePanel = document.getElementById('sidePanel');
const panelOverlay = document.getElementById('panelOverlay');
const panelClose = document.getElementById('panelClose');
const loginView = document.getElementById('loginView');
const chatView = document.getElementById('chatView');
const planBadge = document.getElementById('planBadge');

document.getElementById('ctaBtn').addEventListener('click', () => openPanel());

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
fabBtn.addEventListener('click', () => openPanel());
panelClose.addEventListener('click', closePanel);
panelOverlay.addEventListener('click', closePanel);
document.getElementById('openChatFromSection').addEventListener('click', () => openPanel());

// ---- Mock auth + usage state ----
const GUEST_LIMIT = 3;
const FREE_LIMIT = 20;
const state = { loggedIn: false, guestCount: 0, usedCount: 0 };

function showLoginView() {
  loginView.style.display = 'flex';
  chatView.style.display = 'none';
}
function showChatView() {
  loginView.style.display = 'none';
  chatView.style.display = 'flex';
  updateUsageText();
}
function updateUsageText() {
  const usageText = document.getElementById('usageText');
  if (state.loggedIn) {
    usageText.textContent = `${state.usedCount}/${FREE_LIMIT} soru kullanıldı`;
    planBadge.textContent = 'Free plan';
  } else {
    usageText.textContent = `${state.guestCount}/${GUEST_LIMIT} misafir sorusu kullanıldı`;
    planBadge.textContent = 'Misafir';
  }
}

document.getElementById('continueGuest').addEventListener('click', () => {
  showChatView();
  if (chatLogEl().children.length === 0) {
    addBubble('Merhaba! Bir hisse hakkında soru sorabilirsin — örneğin "THYAO neden yükseldi?"', 'bot', 'FinSight');
  }
});

document.getElementById('authSubmit').addEventListener('click', () => {
  const email = document.getElementById('authEmail').value.trim();
  if (!email) { document.getElementById('authEmail').focus(); return; }
  state.loggedIn = true;
  state.usedCount = 0;
  showChatView();
  addBubble(`Tekrar hoş geldin! Günde ${FREE_LIMIT} soru hakkın var.`, 'bot', 'FinSight');
});
document.getElementById('authGoogle').addEventListener('click', () => {
  state.loggedIn = true;
  state.usedCount = 0;
  showChatView();
  addBubble(`Google ile giriş yapıldı. Günde ${FREE_LIMIT} soru hakkın var.`, 'bot', 'FinSight');
});
document.getElementById('authSwitchSignup').addEventListener('click', () => {
  document.getElementById('authSubmit').textContent = 'Kayıt ol';
  document.querySelector('.panel-lead').textContent = 'Hesap oluştur, günlük 20 soru hakkın hemen aktif olsun.';
});
document.getElementById('logoutBtn').addEventListener('click', () => {
  state.loggedIn = false;
  chatLogEl().innerHTML = '';
  showLoginView();
});

// ---- Chat logic (shared) ----
const chatInput = document.getElementById('chatInput');
const chatSend = document.getElementById('chatSend');
function chatLogEl(){ return document.getElementById('chatLog'); }

const knownAnswers = {
  THYAO: "THYAO bugün %7.4 yükseldi. Temmuz yolcu istatistikleri beklentinin üzerinde geldi ve işlem hacmi ortalamanın 3 katına çıktı. Geçmişte benzer rekor açıklamalarının birkaç gün etkisini sürdürdüğü gözlemleniyor.",
  AKBNK: "AKBNK bugün %1.9 geriledi. TCMB faiz kararı öncesi bankacılık endeksi genelinde temkinli bir hareket görüldü, tek başına şirkete özgü bir gelişme değil.",
  EREGL: "EREGL bugün %2.1 yükseldi. Avrupa'da çelik talebine dair toparlanma sinyalleri ihracat fiyatlarını destekledi.",
  ASTOR: "ASTOR bu hafta %5.2 geriledi. 12 Temmuz'da açıklanan ihracat rakamları beklentinin altında kaldı ve aynı gün sektör genelinde kâr satışı görüldü."
};

function addBubble(text, type, label) {
  const div = document.createElement('div');
  div.className = 'bubble ' + type;
  if (label) {
    const lbl = document.createElement('span');
    lbl.className = 'lbl';
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
      document.getElementById('fiyat').scrollIntoView({behavior:'smooth'});
    });
  }
}

function respondTo(question) {
  if (!state.loggedIn && state.guestCount >= GUEST_LIMIT) { showLimitReached(); return; }
  if (state.loggedIn && state.usedCount >= FREE_LIMIT) { showLimitReached(); return; }

  addBubble(question, 'user');
  if (state.loggedIn) { state.usedCount++; } else { state.guestCount++; }
  updateUsageText();

  const typing = document.createElement('div');
  typing.className = 'bubble bot typing';
  typing.innerHTML = '<span></span><span></span><span></span>';
  chatLogEl().appendChild(typing);
  chatLogEl().scrollTop = chatLogEl().scrollHeight;

  setTimeout(() => {
    typing.remove();
    const upper = question.toUpperCase();
    const match = Object.keys(knownAnswers).find(sym => upper.includes(sym));
    const answer = match
      ? knownAnswers[match]
      : "Bu demo sürümde yalnızca THYAO, AKBNK, EREGL ve ASTOR için örnek cevaplar var. Gerçek sürümde her hisse için canlı veri ve haber taraması kullanılacak.";
    addBubble(answer, 'bot', 'FinSight');
    if ((state.loggedIn && state.usedCount >= FREE_LIMIT) || (!state.loggedIn && state.guestCount >= GUEST_LIMIT)) {
      showLimitReached();
    }
  }, 900);
}

chatSend.addEventListener('click', () => {
  const q = chatInput.value.trim();
  if (!q) return;
  respondTo(q);
  chatInput.value = '';
});
chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') chatSend.click();
});

// Clicking a stock card opens the panel and asks about it
document.querySelectorAll('.stock-card').forEach(card => {
  card.addEventListener('click', () => {
    openPanel(card.dataset.symbol + ' neden bu şekilde hareket etti?');
  });
});