/* ============================================
   ENGINEER HUB - i18n (Internationalization)
   Languages: vi (Tiếng Việt), ja (日本語)
   ============================================ */

const TRANSLATIONS = {
  vi: {
    // ── App ──
    'app.name': 'EngineerHub',
    'app.sub':  'Quản lý Kỹ sư',

    // ── Sidebar sections ──
    'nav.section.SALES':    '📌 Sales Tools',
    'nav.section.MANAGE':   '⚙️ Quản lý',
    'nav.section.ENGINEER': '👤 Kỹ sư',

    // ── Nav items ──
    'nav.dashboard':    'Dashboard',
    'nav.ai_search':    'AI Search',
    'nav.availability': 'Lịch trống',
    'nav.proposal':     'Tạo Proposal',
    'nav.engineers':    'Danh sách KS',
    'nav.skills':       'Skill Matrix',
    'nav.profile':      'Profile của tôi',
    'nav.certs':        'Chứng chỉ của tôi',

    // ── Language selector ──
    'lang.label': 'Ngôn ngữ',
    'lang.vi':    '🇻🇳 Tiếng Việt',
    'lang.ja':    '🇯🇵 日本語',

    // ── Common actions ──
    'action.view':    '👁 Xem',
    'action.edit':    '✏️ Sửa',
    'action.delete':  '🗑 Xóa',
    'action.save':    'Lưu',
    'action.cancel':  'Hủy',
    'action.add':     'Thêm',
    'action.export':  '📤 Export',
    'action.filter':  '🔽 Lọc',
    'action.search':  'Tìm kiếm',
    'action.reset':   'Đặt lại',
    'action.close':   '✕',
    'action.submit':  'Gửi',

    // ── Status badges ──
    'status.available':     'Rảnh ngay',
    'status.available_pct': 'một phần',
    'status.partial':       '% rảnh',
    'status.busy':          'Bận',
    'status.busy_pct':      'Bận',
    'status.free_now':      'Rảnh ngay',

    // ── Location ──
    'loc.jp': '🇯🇵 Nhật Bản',
    'loc.vn': '🇻🇳 Việt Nam',
    'loc.all': 'Tất cả',
    'loc.label': 'Địa điểm',

    // ── Level ──
    'level.junior': 'Junior',
    'level.middle': 'Middle',
    'level.senior': 'Senior',
    'level.lead':   'Lead',

    // ── Availability text ──
    'avail.now':  'Rảnh ngay',
    'avail.from': 'Rảnh từ',

    // ── Common labels ──
    'label.year':        'năm',
    'label.years':       'năm kinh nghiệm',
    'label.japanese':    'Tiếng Nhật',
    'label.english':     'Tiếng Anh',
    'label.skill':       'Kỹ năng',
    'label.skills':      'Kỹ năng',
    'label.cert':        'Chứng chỉ',
    'label.certs':       'Chứng chỉ',
    'label.rating':      'Đánh giá',
    'label.workload':    'Workload',
    'label.team':        'Team',
    'label.bucho':       'Quản lý',
    'label.project':     'Dự án hiện tại',
    'label.mobilizable': 'Có thể onsite JP',
    'label.visa':        'Visa',
    'label.note':        'Ghi chú',
    'label.level':       'Cấp độ',
    'label.id':          'Mã KS',
    'label.name':        'Họ tên',
    'label.location':    'Địa điểm',
    'label.status':      'Trạng thái',
    'label.available_from': 'Rảnh từ',
    'label.result':      'kết quả',
    'label.all':         'Tất cả',
    'label.match':       'phù hợp',
    'label.filter':      'Lọc',
    'label.sort_by':     'Sắp xếp',

    // ── Dashboard page ──
    'dash.title':           'Sales Dashboard',
    'dash.subtitle':        'Tổng quan nhân lực hiện tại',
    'dash.stats.available': 'KS rảnh ngay',
    'dash.stats.partial':   'KS rảnh một phần',
    'dash.stats.soon':      'Sắp rảnh (30 ngày)',
    'dash.stats.total':     'Tổng KS',
    'dash.stats.util_jp':   '% Utilization JP',
    'dash.stats.util_vn':   '% Utilization VN',
    'dash.stats.mobilize':  'Có thể onsite JP',
    'dash.available_list':  'Kỹ sư đang rảnh',
    'dash.alerts':          'Cảnh báo & Chú ý',
    'dash.util_chart':      'Utilization Rate',
    'dash.mobilize_track':  'Theo dõi Mobilizable',
    'dash.top_skills':      'Top Skills (toàn công ty)',
    'dash.tab.all':         'Tất cả',
    'dash.tab.jp':          '🇯🇵 Nhật Bản (120)',
    'dash.tab.vn':          '🇻🇳 Việt Nam (1,000)',

    // ── AI Search page ──
    'search.title':          'AI Engineer Search',
    'search.subtitle':       'Dán JD của khách hàng, AI sẽ tìm kỹ sư phù hợp nhất',
    'search.placeholder':    'Dán thông tin dự án / JD của khách hàng vào đây...',
    'search.btn':            '🤖 Phân tích & Tìm kiếm',
    'search.example.label':  'Ví dụ nhanh:',
    'search.parsed_title':   '📋 AI đã phân tích yêu cầu:',
    'search.result_title':   'Kỹ sư phù hợp',
    'search.no_result':      'Không tìm thấy kỹ sư phù hợp với yêu cầu này.',
    'search.create_proposal': '📋 Tạo Proposal từ',
    'search.selected':       'đã chọn',
    'search.ai_suggest':     '💡 Gợi ý từ AI',

    // ── Availability page ──
    'avail.title':           'Availability Timeline',
    'avail.subtitle':        'Lịch trống kỹ sư trong 6 tháng tới',
    'avail.filter.name':     'Tìm theo tên...',
    'avail.filter.skill':    'Kỹ năng',
    'avail.filter.mobilize': 'Chỉ Mobilizable',
    'avail.legend.free':     'Rảnh',
    'avail.legend.partial':  '50% rảnh',
    'avail.legend.busy':     'Bận',
    'avail.summary_footer':  'KS rảnh',

    // ── Profile page ──
    'profile.title':         'Profile của tôi',
    'profile.subtitle':      'Cập nhật thông tin, kỹ năng và chứng chỉ',
    'profile.tab.skills':    'Kỹ năng',
    'profile.tab.certs':     'Chứng chỉ',
    'profile.tab.projects':  'Dự án',
    'profile.tab.note':      'Ghi chú',
    'profile.add_skill':     '+ Thêm kỹ năng',
    'profile.skill_name':    'Tên kỹ năng',
    'profile.skill_level':   'Cấp độ',
    'profile.skill_years':   'Số năm',
    'profile.upload_cert':   '📎 Tải lên chứng chỉ',
    'profile.send_to_bucho': '📤 Gửi cập nhật cho Bucho',
    'profile.submit_banner': 'Có thay đổi mới chưa gửi',
    'profile.goals':         'Mục tiêu phát triển',

    // ── Skills (Matrix) page ──
    'skills.title':          'Skill Matrix',
    'skills.subtitle':       'Ma trận kỹ năng toàn bộ kỹ sư',
    'skills.view.matrix':    '📊 Ma trận',
    'skills.view.chart':     '📈 Biểu đồ',
    'skills.filter.name':    'Tìm kỹ sư...',
    'skills.filter.min_level': 'Lv tối thiểu',
    'skills.filter.category': 'Danh mục',
    'skills.filter.avail_only': 'Chỉ người rảnh',
    'skills.legend.lv1':     'Lv.1 Cơ bản',
    'skills.legend.lv2':     'Lv.2 Học viên',
    'skills.legend.lv3':     'Lv.3 Thành thạo',
    'skills.legend.lv4':     'Lv.4 Nâng cao',
    'skills.legend.lv5':     'Lv.5 Chuyên gia',
    'skills.footer.total':   'Có kỹ năng (Lv≥3)',
    'skills.footer.expert':  'Chuyên gia (Lv5)',

    // ── Engineers page ──
    'engineers.title':       'Quản lý Kỹ sư',
    'engineers.subtitle':    'Danh sách toàn bộ kỹ sư',
    'engineers.view.table':  '☰ Bảng',
    'engineers.view.card':   '⊞ Thẻ',
    'engineers.add':         '+ Thêm KS',
    'engineers.export':      '📤 Export',
    'engineers.filter.name': 'Tìm theo tên / ID...',
    'engineers.col.name':    'Họ tên',
    'engineers.col.loc':     'Địa điểm',
    'engineers.col.level':   'Level',
    'engineers.col.skills':  'Kỹ năng',
    'engineers.col.status':  'Trạng thái',
    'engineers.col.workload': 'Workload',
    'engineers.col.japanese': 'Tiếng Nhật',
    'engineers.col.rating':  'Rating',
    'engineers.col.actions': 'Thao tác',
    'engineers.detail.info':     'Thông tin chung',
    'engineers.detail.skills':   'Kỹ năng',
    'engineers.detail.certs':    'Chứng chỉ',
    'engineers.detail.mobilize': 'Trạng thái Mobilization',

    // ── Proposal ──
    'proposal.title':        'Tạo Proposal',
    'proposal.subtitle':     'Tổng hợp thông tin kỹ sư cho khách hàng',
    'proposal.engineer_count': 'kỹ sư được chọn',
    'proposal.client_name':  'Tên khách hàng',
    'proposal.project_name': 'Tên dự án',
    'proposal.generate':     '📄 Tạo Proposal',
    'proposal.download':     '⬇️ Tải về (PDF)',
    'proposal.preview':      'Xem trước',
  },

  ja: {
    // ── App ──
    'app.name': 'EngineerHub',
    'app.sub':  'エンジニア管理',

    // ── Sidebar sections ──
    'nav.section.SALES':    '📌 営業ツール',
    'nav.section.MANAGE':   '⚙️ 管理',
    'nav.section.ENGINEER': '👤 エンジニア',

    // ── Nav items ──
    'nav.dashboard':    'ダッシュボード',
    'nav.ai_search':    'AI検索',
    'nav.availability': '空き状況',
    'nav.proposal':     '提案書作成',
    'nav.engineers':    'エンジニア一覧',
    'nav.skills':       'スキルマトリクス',
    'nav.profile':      'マイプロフィール',
    'nav.certs':        'マイ資格',

    // ── Language selector ──
    'lang.label': '言語',
    'lang.vi':    '🇻🇳 ベトナム語',
    'lang.ja':    '🇯🇵 日本語',

    // ── Common actions ──
    'action.view':    '👁 詳細',
    'action.edit':    '✏️ 編集',
    'action.delete':  '🗑 削除',
    'action.save':    '保存',
    'action.cancel':  'キャンセル',
    'action.add':     '追加',
    'action.export':  '📤 エクスポート',
    'action.filter':  '🔽 絞込',
    'action.search':  '検索',
    'action.reset':   'リセット',
    'action.close':   '✕',
    'action.submit':  '送信',

    // ── Status badges ──
    'status.available':     '今すぐ空き',
    'status.available_pct': '一部空き',
    'status.partial':       '% 空き',
    'status.busy':          '稼働中',
    'status.busy_pct':      '稼働中',
    'status.free_now':      '今すぐ空き',

    // ── Location ──
    'loc.jp': '🇯🇵 日本',
    'loc.vn': '🇻🇳 ベトナム',
    'loc.all': 'すべて',
    'loc.label': '勤務地',

    // ── Level ──
    'level.junior': 'ジュニア',
    'level.middle': 'ミドル',
    'level.senior': 'シニア',
    'level.lead':   'リード',

    // ── Availability text ──
    'avail.now':  '今すぐ空き',
    'avail.from': '空き予定',

    // ── Common labels ──
    'label.year':        '年',
    'label.years':       '年経験',
    'label.japanese':    '日本語',
    'label.english':     '英語',
    'label.skill':       'スキル',
    'label.skills':      'スキル',
    'label.cert':        '資格',
    'label.certs':       '資格',
    'label.rating':      '評価',
    'label.workload':    '稼働率',
    'label.team':        'チーム',
    'label.bucho':       '部長',
    'label.project':     '担当プロジェクト',
    'label.mobilizable': '日本常駐可',
    'label.visa':        'ビザ',
    'label.note':        '備考',
    'label.level':       'レベル',
    'label.id':          'エンジニアID',
    'label.name':        '氏名',
    'label.location':    '勤務地',
    'label.status':      'ステータス',
    'label.available_from': '空き予定日',
    'label.result':      '件',
    'label.all':         'すべて',
    'label.match':       'マッチ',
    'label.filter':      '絞込',
    'label.sort_by':     '並び替え',

    // ── Dashboard page ──
    'dash.title':           'セールスダッシュボード',
    'dash.subtitle':        '現在の人材状況',
    'dash.stats.available': '今すぐ空き',
    'dash.stats.partial':   '一部空き',
    'dash.stats.soon':      '間もなく空き (30日)',
    'dash.stats.total':     'エンジニア総数',
    'dash.stats.util_jp':   '稼働率 JP',
    'dash.stats.util_vn':   '稼働率 VN',
    'dash.stats.mobilize':  '日本常駐可',
    'dash.available_list':  '空きエンジニア',
    'dash.alerts':          'アラート・注意事項',
    'dash.util_chart':      '稼働率',
    'dash.mobilize_track':  'モビライズ追跡',
    'dash.top_skills':      'トップスキル（全社）',
    'dash.tab.all':         'すべて',
    'dash.tab.jp':          '🇯🇵 日本 (120名)',
    'dash.tab.vn':          '🇻🇳 ベトナム (1,000名)',

    // ── AI Search page ──
    'search.title':          'AIエンジニア検索',
    'search.subtitle':       '顧客のJDを貼り付けると、AIが最適なエンジニアを提案します',
    'search.placeholder':    'プロジェクト情報 / 顧客のJDをここに貼り付けてください...',
    'search.btn':            '🤖 分析して検索',
    'search.example.label':  '例:',
    'search.parsed_title':   '📋 AI分析結果:',
    'search.result_title':   'マッチしたエンジニア',
    'search.no_result':      'この条件に合うエンジニアが見つかりませんでした。',
    'search.create_proposal': '📋 提案書を作成',
    'search.selected':       '名選択',
    'search.ai_suggest':     '💡 AIからの提案',

    // ── Availability page ──
    'avail.title':           '空き状況タイムライン',
    'avail.subtitle':        '今後6ヶ月のエンジニア空き状況',
    'avail.filter.name':     '名前で検索...',
    'avail.filter.skill':    'スキル',
    'avail.filter.mobilize': 'モビライズのみ',
    'avail.legend.free':     '空き',
    'avail.legend.partial':  '50%空き',
    'avail.legend.busy':     '稼働中',
    'avail.summary_footer':  '名空き',

    // ── Profile page ──
    'profile.title':         'マイプロフィール',
    'profile.subtitle':      'スキル・資格・プロジェクト情報を更新',
    'profile.tab.skills':    'スキル',
    'profile.tab.certs':     '資格',
    'profile.tab.projects':  'プロジェクト',
    'profile.tab.note':      '備考',
    'profile.add_skill':     '+ スキル追加',
    'profile.skill_name':    'スキル名',
    'profile.skill_level':   'レベル',
    'profile.skill_years':   '経験年数',
    'profile.upload_cert':   '📎 資格をアップロード',
    'profile.send_to_bucho': '📤 部長に更新を送信',
    'profile.submit_banner': '未送信の変更があります',
    'profile.goals':         '成長目標',

    // ── Skills (Matrix) page ──
    'skills.title':          'スキルマトリクス',
    'skills.subtitle':       '全エンジニアのスキル一覧',
    'skills.view.matrix':    '📊 マトリクス',
    'skills.view.chart':     '📈 チャート',
    'skills.filter.name':    'エンジニアを検索...',
    'skills.filter.min_level': '最低レベル',
    'skills.filter.category': 'カテゴリ',
    'skills.filter.avail_only': '空きのみ',
    'skills.legend.lv1':     'Lv.1 初級',
    'skills.legend.lv2':     'Lv.2 基礎',
    'skills.legend.lv3':     'Lv.3 中級',
    'skills.legend.lv4':     'Lv.4 上級',
    'skills.legend.lv5':     'Lv.5 エキスパート',
    'skills.footer.total':   'スキルあり (Lv≥3)',
    'skills.footer.expert':  'エキスパート (Lv5)',

    // ── Engineers page ──
    'engineers.title':       'エンジニア管理',
    'engineers.subtitle':    '全エンジニア一覧',
    'engineers.view.table':  '☰ テーブル',
    'engineers.view.card':   '⊞ カード',
    'engineers.add':         '+ エンジニア追加',
    'engineers.export':      '📤 エクスポート',
    'engineers.filter.name': '氏名 / IDで検索...',
    'engineers.col.name':    '氏名',
    'engineers.col.loc':     '勤務地',
    'engineers.col.level':   'レベル',
    'engineers.col.skills':  'スキル',
    'engineers.col.status':  'ステータス',
    'engineers.col.workload': '稼働率',
    'engineers.col.japanese': '日本語',
    'engineers.col.rating':  '評価',
    'engineers.col.actions': '操作',
    'engineers.detail.info':     '基本情報',
    'engineers.detail.skills':   'スキル',
    'engineers.detail.certs':    '資格',
    'engineers.detail.mobilize': 'モビライズ状況',

    // ── Proposal ──
    'proposal.title':        '提案書作成',
    'proposal.subtitle':     '顧客向けエンジニア提案書を作成',
    'proposal.engineer_count': '名のエンジニアを選択',
    'proposal.client_name':  'クライアント名',
    'proposal.project_name': 'プロジェクト名',
    'proposal.generate':     '📄 提案書を作成',
    'proposal.download':     '⬇️ ダウンロード (PDF)',
    'proposal.preview':      'プレビュー',
  },
};

// ── Core i18n functions ──

let currentLang = localStorage.getItem('eh_lang') || 'vi';

function t(key) {
  const dict = TRANSLATIONS[currentLang] || TRANSLATIONS['vi'];
  return dict[key] || TRANSLATIONS['vi'][key] || key;
}

function setLang(lang) {
  if (!TRANSLATIONS[lang]) return;
  currentLang = lang;
  localStorage.setItem('eh_lang', lang);
  applyTranslations();
  // Re-render sidebar if available
  if (typeof renderSidebar === 'function') {
    const role = document.body.dataset.role || 'sales';
    renderSidebar(role);
    // Re-attach lang selector events after sidebar re-render
    attachLangSelector();
  }
  // Trigger page-level refresh if defined
  if (typeof onLangChange === 'function') onLangChange(lang);
}

function getLang() {
  return currentLang;
}

// Apply translations to elements with data-i18n attribute
function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const val = t(key);
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      el.placeholder = val;
    } else {
      el.textContent = val;
    }
  });
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    const key = el.getAttribute('data-i18n-html');
    el.innerHTML = t(key);
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.getAttribute('data-i18n-title');
    el.title = t(key);
  });
  // Update lang selector active state
  document.querySelectorAll('.lang-option').forEach(btn => {
    btn.classList.toggle('lang-option--active', btn.dataset.lang === currentLang);
  });
}

// Attach click events to language selector buttons
function attachLangSelector() {
  document.querySelectorAll('.lang-option').forEach(btn => {
    btn.onclick = () => setLang(btn.dataset.lang);
  });
}

// Auto-apply on DOM ready (called after all scripts loaded)
function i18nInit() {
  applyTranslations();
  attachLangSelector();
}
