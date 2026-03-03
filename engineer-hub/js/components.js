/* ============================================
   ENGINEER HUB - Shared Components JS
   ============================================ */

// Current page detection
const currentPage = window.location.pathname.split('/').pop() || 'index.html';

// Sidebar nav items (labels via t())
const NAV_ITEMS = [
  { id: 'index.html',        icon: '📊', labelKey: 'nav.dashboard',    section: 'SALES' },
  { id: 'search.html',       icon: '🤖', labelKey: 'nav.ai_search',    section: 'SALES' },
  { id: 'availability.html', icon: '📅', labelKey: 'nav.availability', section: 'SALES' },
  { id: 'engineers.html',    icon: '👥', labelKey: 'nav.engineers',    section: 'MANAGE' },
  { id: 'skills.html',       icon: '📊', labelKey: 'nav.skills',       section: 'MANAGE' },
  { id: 'profile.html',      icon: '✏️', labelKey: 'nav.profile',      section: 'ENGINEER' },
  { id: 'certs.html',        icon: '🏅', labelKey: 'nav.certs',        section: 'ENGINEER' },
];

// Render sidebar
function renderSidebar(role = 'sales') {
  const sidebarEl = document.getElementById('sidebar');
  if (!sidebarEl) return;

  // Determine which sections to show
  const visibleSections = role === 'engineer'
    ? ['ENGINEER', 'MANAGE']
    : ['SALES', 'MANAGE', 'ENGINEER'];

  const groupedItems = {};
  NAV_ITEMS.forEach(item => {
    if (!groupedItems[item.section]) groupedItems[item.section] = [];
    groupedItems[item.section].push(item);
  });

  const userName  = role === 'engineer' ? 'Nguyen Van An' : 'Tanaka Kenji';
  const userRole  = role === 'engineer' ? 'Senior Engineer · ENG-001' : 'Sales Manager · JP';
  const userInit  = role === 'engineer' ? 'NA' : 'TK';

  const sectionKeys = { SALES: 'nav.section.SALES', MANAGE: 'nav.section.MANAGE', ENGINEER: 'nav.section.ENGINEER' };

  let navHtml = '';
  visibleSections.forEach(sec => {
    if (!groupedItems[sec]) return;
    const sectionLabel = (typeof t === 'function') ? t(sectionKeys[sec]) : sec;
    navHtml += `<div class="sidebar__section-label">${sectionLabel}</div>`;
    groupedItems[sec].forEach(item => {
      const isActive = currentPage === item.id;
      const label = (typeof t === 'function') ? t(item.labelKey) : item.labelKey;
      navHtml += `
        <a href="${item.id}" class="sidebar__nav-item ${isActive ? 'sidebar__nav-item--active' : ''}">
          <span class="sidebar__nav-item-icon">${item.icon}</span>
          ${label}
          ${item.id === 'search.html' && !isActive ? '<span class="sidebar__nav-item-badge">AI</span>' : ''}
        </a>`;
    });
    navHtml += '<div style="height:8px"></div>';
  });

  // Language selector
  const currentLangCode = (typeof getLang === 'function') ? getLang() : 'vi';
  const langSelectorHtml = `
    <div class="sidebar__lang">
      <div class="sidebar__lang-label">${(typeof t === 'function') ? t('lang.label') : '言語 / Ngôn ngữ'}</div>
      <div class="sidebar__lang-btns">
        <button class="lang-option ${currentLangCode === 'vi' ? 'lang-option--active' : ''}" data-lang="vi">🇻🇳 Việt</button>
        <button class="lang-option ${currentLangCode === 'ja' ? 'lang-option--active' : ''}" data-lang="ja">🇯🇵 日本語</button>
      </div>
    </div>`;

  sidebarEl.innerHTML = `
    <div class="sidebar__logo">
      <div class="sidebar__logo-icon">🏢</div>
      <div>
        <div class="sidebar__logo-text" data-i18n="app.name">EngineerHub</div>
        <div class="sidebar__logo-sub" data-i18n="app.sub">Engineer Management</div>
      </div>
    </div>

    <nav class="sidebar__nav">
      ${navHtml}
    </nav>

    ${langSelectorHtml}

    <div class="sidebar__user">
      <div class="sidebar__user-avatar">${userInit}</div>
      <div>
        <div class="sidebar__user-name">${userName}</div>
        <div class="sidebar__user-role">${userRole}</div>
      </div>
    </div>
  `;
}

// Render engineer card (used in multiple pages)
function renderEngineerCard(eng, showMatch = false, matchPct = null) {
  const skillsHtml = eng.skills.slice(0, 4).map(s =>
    `<span class="skill-tag">${s.name} <span style="color:var(--color-primary-400)">Lv.${s.level}</span></span>`
  ).join('');
  const certsHtml = eng.certs.slice(0, 2).map(c =>
    `<span class="cert-badge">🏅 ${c}</span>`
  ).join('');

  const matchLabel = (typeof t === 'function') ? t('label.match') : 'phù hợp';
  const viewLabel  = (typeof t === 'function') ? t('action.view') : '👁 Xem';

  const matchHtml = showMatch && matchPct ? `
    <div class="match-score">
      <div class="match-score__pct">${matchPct}%</div>
      <div class="match-score__bar">
        <div class="match-score__fill" style="width:${matchPct}%"></div>
      </div>
      <div class="match-score__label">${matchLabel}</div>
    </div>` : '';

  const mobilizeLabel = (typeof t === 'function') ? t('label.mobilizable') : 'Mobilizable';
  const mobilizeHtml = eng.mobilizable
    ? `<span class="badge badge--info" title="${mobilizeLabel}">✈️ Mobilizable</span>` : '';

  return `
    <div class="engineer-item" onclick="window.open('profile.html?id=${eng.id}','_self')">
      <div class="engineer-item__avatar" style="background:${eng.color}">${eng.initials}</div>
      <div class="engineer-item__info">
        <div class="flex items-center gap-2">
          <span class="engineer-item__name">${eng.name}</span>
          ${locationBadge(eng)}
          ${mobilizeHtml}
        </div>
        <div class="engineer-item__meta">
          <span class="text-xs text-muted font-semibold">${eng.level} · ${eng.years} ${(typeof t==='function')?t('label.year'):'năm'}</span>
          <span class="text-xs text-muted">🇯🇵 ${eng.japanese}</span>
          ${statusBadge(eng)}
          <span class="text-xs text-secondary">${availableText(eng)}</span>
        </div>
        <div class="engineer-item__skills">
          ${skillsHtml}
          ${certsHtml}
        </div>
      </div>
      <div class="engineer-item__right">
        ${matchHtml}
        <button class="btn btn--sm btn--secondary" onclick="event.stopPropagation()">${viewLabel}</button>
      </div>
    </div>`;
}

// Toast notification
function showToast(message, type = 'success') {
  const colors = { success: '#10B981', error: '#EF4444', info: '#3B82F6', warning: '#F59E0B' };
  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:${colors[type]}; color:white;
    padding:12px 20px; border-radius:12px;
    font-size:14px; font-weight:600;
    box-shadow:0 10px 25px rgba(0,0,0,0.2);
    display:flex; align-items:center; gap:8px;
    animation: slideUp 0.3s ease;
    max-width: 400px;
  `;
  const icons = { success:'✅', error:'❌', info:'ℹ️', warning:'⚠️' };
  toast.innerHTML = `${icons[type]} ${message}`;
  document.body.appendChild(toast);

  const style = document.createElement('style');
  style.textContent = '@keyframes slideUp { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:translateY(0) } }';
  document.head.appendChild(style);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Format date helper
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  const locale = (typeof getLang === 'function' && getLang() === 'ja') ? 'ja-JP' : 'vi-VN';
  return d.toLocaleDateString(locale, { day:'2-digit', month:'2-digit', year:'numeric' });
}
