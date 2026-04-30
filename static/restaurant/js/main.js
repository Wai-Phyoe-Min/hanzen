/* ============================================================
   花膳 HANZEN — main.js
============================================================ */
'use strict';

/* ── CSRF token / URL config (set from template in base.html) ── */
// CSRF_TOKEN and URLS are initialized in the base template script.

/* ────────────────────────────────────────────────
   DYNAMIC COPYRIGHT YEAR
──────────────────────────────────────────────── */
(function setCopyrightYear() {
  const yearEl = document.getElementById('copyrightYear');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }
})();

/* ────────────────────────────────────────────────
   LANGUAGE TOGGLE  ← FIXED: scans ALL [data-ja]/[data-en]
──────────────────────────────────────────────── */
const LANG_STORAGE_KEY = 'hanzenPreferredLang';
let _lang = 'ja';

function setPreferredLang(lang) {
  try { localStorage.setItem(LANG_STORAGE_KEY, lang); } catch (err) {}
}

function getPreferredLang() {
  let stored = null;
  try {
    stored = localStorage.getItem(LANG_STORAGE_KEY);
  } catch (err) {
    stored = null;
  }

  if (stored === 'ja' || stored === 'en') {
    return stored;
  }

  const bodyLang = document.body.dataset.lang;
  if (bodyLang === 'ja' || bodyLang === 'en') {
    try { localStorage.setItem(LANG_STORAGE_KEY, bodyLang); } catch (err) {}
    return bodyLang;
  }

  const htmlLang = document.documentElement.lang;
  return htmlLang === 'en' ? 'en' : 'ja';
}

function updateLangButtons(lang) {
  ['langBtnMobile','langBtnDesktop','langBtn'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = lang === 'ja' ? 'EN' : 'JP';
  });
}

function applyLang(lang) {
  _lang = lang;
  document.body.dataset.lang = _lang;
  document.documentElement.lang = _lang;
  updateLangButtons(_lang);

  document.querySelectorAll('[data-ja],[data-en]').forEach(el => {
    const val = el.getAttribute('data-' + _lang);
    if (val === null) return;               // attribute absent → skip
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      el.placeholder = val;
    } else {
      el.innerHTML = val;                   // supports <br> etc.
    }
  });
}

function toggleLang() {
  const next = _lang === 'ja' ? 'en' : 'ja';
  applyLang(next);
  setPreferredLang(next);
}
window.toggleLang = toggleLang;

function initLanguage() {
  const preferred = getPreferredLang();
  applyLang(preferred);
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', initLanguage);
} else {
  initLanguage();
}
window.addEventListener('pageshow', initLanguage);

/* ────────────────────────────────────────────────
   CUSTOM CURSOR
──────────────────────────────────────────────── */
(function initCursor() {
  const dot  = document.getElementById('cursorDot');
  const ring = document.getElementById('cursorRing');
  if (!dot || !ring) return;

  let mx=0,my=0,rx=0,ry=0;
  document.addEventListener('mousemove', e => { mx=e.clientX; my=e.clientY; });

  (function animate() {
    rx += (mx-rx)*.18; ry += (my-ry)*.18;
    dot.style.left  = mx+'px'; dot.style.top  = my+'px';
    ring.style.left = rx+'px'; ring.style.top = ry+'px';
    requestAnimationFrame(animate);
  })();

  document.querySelectorAll('a,button,.dish-card,.g-item,.g-item-full,.menu-tab,.course-card,.pillar-card').forEach(el => {
    el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
    el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
  });
})();

/* ────────────────────────────────────────────────
   SEASONAL BANNER
──────────────────────────────────────────────── */
(function initBanner() {
  const banner = document.getElementById('seasonal-banner');
  const nav    = document.getElementById('mainNav');
  if (!banner) return;

  // Only show if banner is active (not closed)
  if (!banner.dataset.closed) {
    setTimeout(() => banner.classList.add('show'), 500);
  }

  function setNavOffset() {
    if (!nav) return;
    const h = (!banner.dataset.closed && banner.classList.contains('show'))
              ? banner.offsetHeight : 0;
    nav.style.top = h + 'px';
  }
  setNavOffset();
  window.addEventListener('resize', setNavOffset);

  window.closeBanner = function () {
    banner.classList.remove('show');
    banner.dataset.closed = '1';
    setNavOffset();
  };
})();

/* ────────────────────────────────────────────────
   NAVBAR SCROLL
──────────────────────────────────────────────── */
(function initNavbar() {
  const nav = document.getElementById('mainNav');
  const top = document.getElementById('scrollTop');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
    if (top) top.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });
})();

/* ────────────────────────────────────────────────
   SCROLL FADE-IN
──────────────────────────────────────────────── */
(function initFadeIn() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.fade-in').forEach(el => io.observe(el));
})();

/* ────────────────────────────────────────────────
   COUNTER ANIMATION
──────────────────────────────────────────────── */
(function initCounters() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target, target = +el.dataset.target, step = Math.max(1,Math.ceil(target/60));
      let c = 0;
      const t = setInterval(() => { c=Math.min(c+step,target); el.textContent=c; if(c>=target)clearInterval(t); },28);
      io.unobserve(el);
    });
  }, { threshold: 0.3 });
  document.querySelectorAll('.counter').forEach(el => io.observe(el));
})();

/* ────────────────────────────────────────────────
   TOAST
──────────────────────────────────────────────── */
let _toastTimer = null;
function showToast(msgJa, msgEn) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  const jp = document.getElementById('toastJp');
  const en = document.getElementById('toastEn');
  if (jp) jp.textContent = msgJa;
  if (en) en.textContent = msgEn;
  toast.classList.add('show');
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => toast.classList.remove('show'), 3200);
}
window.showToast = showToast;

/* ────────────────────────────────────────────────
   CART — ADD
──────────────────────────────────────────────── */
async function addToCartAjax(itemId, nameJa) {
  try {
    const res  = await fetch(URLS.cartAdd, {
      method: 'POST',
      headers: {'Content-Type':'application/json','X-CSRFToken':window.CSRF_TOKEN},
      body: JSON.stringify({item_id:itemId,qty:1}),
    });
    const data = await res.json();
    if (data.ok) {
      const badge = document.getElementById('navCartCount');
      if (badge) badge.textContent = data.cart_count;
      showToast(`「${nameJa}」を注文に追加しました`, `"${nameJa}" added to your order`);
    }
  } catch(e) { showToast('エラーが発生しました','An error occurred'); }
}
window.addToCartAjax = addToCartAjax;

/* ────────────────────────────────────────────────
   LIGHTBOX
──────────────────────────────────────────────── */
function openLightbox(src) {
  const lb=document.getElementById('lightbox'),img=document.getElementById('lightbox-img');
  if(!lb||!img) return;
  img.src=src; lb.classList.add('open'); document.body.style.overflow='hidden';
}
function closeLightbox() {
  const lb=document.getElementById('lightbox');
  if(!lb) return;
  lb.classList.remove('open'); document.body.style.overflow='';
}
window.openLightbox=openLightbox; window.closeLightbox=closeLightbox;
document.addEventListener('click',e=>{ if(document.getElementById('lightbox')===e.target) closeLightbox(); });
document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeLightbox(); });

/* ────────────────────────────────────────────────
   NEWSLETTER
──────────────────────────────────────────────── */
async function subscribeNewsletter(e) {
  e.preventDefault();
  const form=e.target, email=form.querySelector('[name=email]')?.value;
  if(!email) return;
  try {
    const res=await fetch(URLS.newsletter,{
      method:'POST',
      headers:{'Content-Type':'application/x-www-form-urlencoded','X-CSRFToken':window.CSRF_TOKEN},
      body:new URLSearchParams({email,csrfmiddlewaretoken:CSRF_TOKEN}).toString(),
    });
    const data=await res.json();
    if(data.ok){ showToast('ご登録ありがとうございます！','Thank you for subscribing!'); form.reset(); }
    else showToast('有効なメールを入力してください','Please enter a valid email.');
  } catch{ showToast('エラーが発生しました','Something went wrong.'); }
}
window.subscribeNewsletter=subscribeNewsletter;

/* ────────────────────────────────────────────────
   MODAL SYSTEM
──────────────────────────────────────────────── */
function openModal(id) {
  const m=document.getElementById(id);
  if(!m) return;
  m.style.display='flex';
  requestAnimationFrame(()=>m.classList.add('modal-open'));
  document.body.style.overflow='hidden';
}
function closeModal(id) {
  const m=document.getElementById(id);
  if(!m) return;
  m.classList.remove('modal-open');
  setTimeout(()=>{ m.style.display='none'; document.body.style.overflow=''; },280);
}
window.openModal=openModal; window.closeModal=closeModal;
// Close on backdrop click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    closeModal(e.target.id);
  }
});

/* ────────────────────────────────────────────────
   LOGOUT CONFIRMATION
──────────────────────────────────────────────── */
function confirmLogout(e) {
  e.preventDefault();
  const lang  = _lang;
  const msgJa = 'ログアウトしますか？';
  const msgEn = 'Are you sure you want to logout?';
  const msg   = lang === 'ja' ? msgJa : msgEn;

  // Custom confirm dialog
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.id = 'logoutConfirmOverlay';
  overlay.style.cssText = 'display:flex;z-index:9000';
  overlay.innerHTML = `
    <div class="modal-box modal-box-sm">
      <div class="modal-header">
        <h3 class="modal-title">
          <i class="fa-solid fa-right-from-bracket me-2" style="color:var(--aka)"></i>
          ログアウト / Logout
        </h3>
      </div>
      <p style="font-size:.88rem;color:#5a4840;margin-bottom:1.5rem;line-height:1.8">
        ${msgJa}<br><span style="font-size:.82rem;color:var(--smoke)">${msgEn}</span>
      </p>
      <div class="d-flex gap-3">
        <button class="btn-submit" style="width:auto;padding:.7rem 1.8rem;background:var(--aka)"
                onclick="document.getElementById('logoutForm').submit()">
          <i class="fa-solid fa-right-from-bracket me-1"></i>
          ログアウト / Logout
        </button>
        <button class="dash-cancel-btn" onclick="document.getElementById('logoutConfirmOverlay').remove();document.body.style.overflow=''">
          キャンセル / Cancel
        </button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  document.body.style.overflow = 'hidden';
  setTimeout(() => overlay.classList.add('modal-open'), 10);
}
window.confirmLogout = confirmLogout;

/* ────────────────────────────────────────────────
   PASSWORD SHOW / HIDE TOGGLE
──────────────────────────────────────────────── */
function togglePw(inputId, btn) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  const show = inp.type === 'password';
  inp.type   = show ? 'text' : 'password';
  const icon = btn.querySelector('i');
  if (icon) { icon.className = show ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye'; }
}
window.togglePw = togglePw;

/* ────────────────────────────────────────────────
   PASSWORD STRENGTH METER
──────────────────────────────────────────────── */
function checkStrength(pw, wrapperId, barId, labelId) {
  const wrap  = document.getElementById(wrapperId);
  const bar   = document.getElementById(barId);
  const label = document.getElementById(labelId);
  if (!wrap || !bar || !label) return;

  if (!pw) { wrap.style.display = 'none'; return; }
  wrap.style.display = 'flex';

  let score = 0;
  if (pw.length >= 8)  score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[a-z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;

  const levels = [
    { pct:16,  color:'#e53935', ja:'非常に弱い',  en:'Very Weak' },
    { pct:33,  color:'#f4511e', ja:'弱い',        en:'Weak' },
    { pct:50,  color:'#fb8c00', ja:'普通',        en:'Fair' },
    { pct:67,  color:'#fdd835', ja:'良い',        en:'Good' },
    { pct:83,  color:'#7cb342', ja:'強い',        en:'Strong' },
    { pct:100, color:'#43a047', ja:'非常に強い',  en:'Very Strong' },
  ];

  const idx   = Math.min(score, levels.length - 1);
  const lvl   = levels[idx];
  bar.style.width      = lvl.pct + '%';
  bar.style.background = lvl.color;
  
  // Use bilingual display based on current language
  if (typeof _lang !== 'undefined' && _lang === 'en') {
    label.textContent = lvl.en;
  } else {
    label.textContent = lvl.ja + ' / ' + lvl.en;
  }
  label.style.color = lvl.color;
}
window.checkStrength = checkStrength;

/* ────────────────────────────────────────────────
   REAL-TIME FORM VALIDATION
──────────────────────────────────────────────── */
(function initRealTimeValidation() {
  document.querySelectorAll('.form-control[required], .form-control[type="email"]').forEach(input => {
    input.addEventListener('blur', () => validateField(input));
    input.addEventListener('input', () => {
      if (input.dataset.touched) validateField(input);
    });
    input.addEventListener('blur', () => { input.dataset.touched = '1'; }, { once: true });
  });
})();

function validateField(input) {
  let errEl = input.parentElement.querySelector('.rt-error');
  if (!errEl) {
    errEl = document.createElement('div');
    errEl.className = 'rt-error field-error';
    input.parentElement.appendChild(errEl);
  }

  let msg = '';
  const val = input.value.trim();

  if (input.required && !val) {
    msg = _lang === 'ja' ? 'この項目は必須です。' : 'This field is required.';
  } else if (input.type === 'email' && val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
    msg = _lang === 'ja' ? '有効なメールアドレスを入力してください。' : 'Please enter a valid email address.';
  } else if (input.name === 'phone' && val && !/^[\d\-\+\(\)\s]+$/.test(val)) {
    msg = _lang === 'ja' ? '電話番号の形式が正しくありません。' : 'Please enter a valid phone number.';
  } else if (input.type === 'date' && val) {
    const today = new Date(); today.setHours(0,0,0,0);
    if (new Date(val) < today) {
      msg = _lang === 'ja' ? '本日以降の日付を選択してください。' : 'Please select today or a future date.';
    }
  }

  errEl.textContent = msg;
  input.style.borderColor = msg ? 'var(--aka)' : (val ? 'var(--matcha)' : '');
}
window.validateField = validateField;

/* ────────────────────────────────────────────────
   AUTO-DISMISS DJANGO MESSAGES
──────────────────────────────────────────────── */
document.querySelectorAll('.alert-msg').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .5s, transform .5s';
    el.style.opacity    = '0';
    el.style.transform  = 'translateX(120%)';
    setTimeout(() => el.remove(), 500);
  }, 4000);
});

/* ────────────────────────────────────────────────
   SMOOTH ANCHOR SCROLL
──────────────────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = document.getElementById('mainNav')?.offsetHeight || 80;
      window.scrollTo({ top: target.offsetTop - offset, behavior: 'smooth' });
    }
  });
});

/* ────────────────────────────────────────────────
   RIPPLE EFFECT
──────────────────────────────────────────────── */
document.querySelectorAll('.dish-order,.btn-gold,.btn-submit,.admin-action-btn').forEach(btn => {
  btn.addEventListener('click', function(e) {
    const r = this.getBoundingClientRect();
    const s = document.createElement('span');
    s.style.cssText=`position:absolute;left:${e.clientX-r.left}px;top:${e.clientY-r.top}px;width:0;height:0;border-radius:50%;background:rgba(255,255,255,.25);transform:translate(-50%,-50%);animation:ripple-anim .6s ease-out forwards;pointer-events:none`;
    this.style.position='relative'; this.style.overflow='hidden';
    this.appendChild(s);
    setTimeout(()=>s.remove(),700);
  });
});

/* ────────────────────────────────────────────────
   AVAILABILITY CHECK (reservation page)
──────────────────────────────────────────────── */
async function checkAvailability() {
  const dateField = document.getElementById('id_date');
  const timeField = document.getElementById('id_time');
  if (!dateField || !timeField) return;
  const date = dateField.value, time = timeField.value;
  if (!date || !time) return;

  const ac  = document.getElementById('availCheck');
  const ind = document.getElementById('availIndicator');
  const msg = document.getElementById('availMsg');
  if (!ac) return;
  ac.style.display = 'flex';
  ind.className    = 'avail-indicator checking';
  msg.textContent  = '確認中... / Checking...';

  try {
    const res  = await fetch(`${URLS.apiAvail}?date=${date}&time=${time}`);
    const data = await res.json();
    ind.className   = `avail-indicator ${data.available ? 'available' : 'unavailable'}`;
    msg.textContent = data.message + (data.available ? ` (残${data.remaining}席 / ${data.remaining} left)` : '');
  } catch { ac.style.display = 'none'; }
}
window.checkAvailability = checkAvailability;

/* ────────────────────────────────────────────────
   SCROLL TO TOP
──────────────────────────────────────────────── */
const scrollTopBtn = document.getElementById('scrollTop');
if (scrollTopBtn) {
  scrollTopBtn.addEventListener('click', () => window.scrollTo({ top:0, behavior:'smooth' }));
}

/* ────────────────────────────────────────────────
   KEYFRAME INJECTION
──────────────────────────────────────────────── */
const kf = document.createElement('style');
kf.textContent = '@keyframes ripple-anim{to{width:200px;height:200px;opacity:0}}';
document.head.appendChild(kf);
