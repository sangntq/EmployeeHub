/* ============================================
   ENGINEER HUB - Mock Data
   ============================================ */

const ENGINEERS = [
  // === JAPAN ENGINEERS (onsite) ===
  {
    id: 'ENG-001', name: 'Nguyen Van An', initials: 'NA', color: '#4F46E5',
    location: 'jp', level: 'Senior', years: 6, team: 'Backend A',
    bucho: 'Yamada-san', status: 'available', availableFrom: '2026-03-01',
    workload: 0, currentProject: null,
    skills: [
      { name: 'Java', level: 5, years: 6 }, { name: 'Spring Boot', level: 5, years: 5 },
      { name: 'AWS', level: 4, years: 3 }, { name: 'Microservices', level: 4, years: 3 },
      { name: 'PostgreSQL', level: 4, years: 4 }, { name: 'Docker', level: 3, years: 2 },
    ],
    certs: ['AWS SAA', 'Oracle Java OCP'],
    japanese: 'N2', english: 'TOEIC 750',
    mobilizable: false, note: 'Tech Lead kinh nghiệm 2 dự án lớn',
    rating: 4.8,
  },
  {
    id: 'ENG-002', name: 'Tran Thi Bich', initials: 'TB', color: '#7C3AED',
    location: 'jp', level: 'Senior', years: 5, team: 'Frontend',
    bucho: 'Yamada-san', status: 'partial', availableFrom: '2026-03-15',
    workload: 50, currentProject: 'Dự án Alpha (Toshiba)',
    skills: [
      { name: 'React', level: 5, years: 5 }, { name: 'TypeScript', level: 5, years: 4 },
      { name: 'Vue.js', level: 3, years: 2 }, { name: 'Node.js', level: 3, years: 3 },
      { name: 'AWS', level: 3, years: 2 },
    ],
    certs: ['AWS SAA', 'Meta React Developer'],
    japanese: 'N2', english: 'Business',
    mobilizable: false, note: 'Chuyên gia UI/UX, đã làm 3 dự án Nhật', rating: 4.6,
  },
  {
    id: 'ENG-003', name: 'Le Van Cuong', initials: 'LC', color: '#0891B2',
    location: 'jp', level: 'Senior', years: 7, team: 'Backend B',
    bucho: 'Tanaka-san', status: 'busy', availableFrom: '2026-06-01',
    workload: 100, currentProject: 'Dự án Beta (Sony)',
    skills: [
      { name: 'Java', level: 5, years: 7 }, { name: '.NET', level: 4, years: 4 },
      { name: 'Kubernetes', level: 5, years: 4 }, { name: 'AWS', level: 5, years: 5 },
      { name: 'Terraform', level: 4, years: 3 },
    ],
    certs: ['AWS SAP', 'CKA (Kubernetes)', 'Azure Administrator'],
    japanese: 'N1', english: 'TOEIC 860',
    mobilizable: false, note: 'DevOps/Cloud chuyên sâu', rating: 4.9,
  },
  {
    id: 'ENG-004', name: 'Pham Duc Dat', initials: 'PD', color: '#DC2626',
    location: 'jp', level: 'Middle', years: 4, team: 'Backend A',
    bucho: 'Yamada-san', status: 'busy', availableFrom: '2026-04-30',
    workload: 100, currentProject: 'Dự án Gamma (NTT)',
    skills: [
      { name: 'Java', level: 4, years: 4 }, { name: 'Spring Boot', level: 4, years: 3 },
      { name: 'MySQL', level: 3, years: 3 }, { name: 'Redis', level: 3, years: 2 },
    ],
    certs: ['AWS SAA'], japanese: 'N2', english: 'Giao tiếp',
    mobilizable: false, note: 'Chăm chỉ, học nhanh', rating: 4.2,
  },
  {
    id: 'ENG-005', name: 'Hoang Thi Yen', initials: 'HY', color: '#059669',
    location: 'jp', level: 'Lead', years: 8, team: 'Architecture',
    bucho: 'Tanaka-san', status: 'partial', availableFrom: '2026-03-01',
    workload: 50, currentProject: 'Tư vấn nội bộ',
    skills: [
      { name: 'Java', level: 5, years: 8 }, { name: 'Microservices', level: 5, years: 5 },
      { name: 'AWS', level: 5, years: 6 }, { name: 'System Design', level: 5, years: 5 },
      { name: 'Python', level: 4, years: 3 }, { name: 'Kafka', level: 4, years: 3 },
    ],
    certs: ['AWS SAP', 'Google Cloud Architect', 'TOGAF'],
    japanese: 'N1', english: 'Fluent',
    mobilizable: false, note: 'Solution Architect hàng đầu công ty', rating: 5.0,
  },

  // === VIETNAM ENGINEERS (mobilizable - JLPT N2+) ===
  {
    id: 'ENG-101', name: 'Vo Minh Hieu', initials: 'VH', color: '#7C3AED',
    location: 'vn', level: 'Senior', years: 5, team: 'VN Backend',
    bucho: 'Nguyen Manager', status: 'available', availableFrom: '2026-03-01',
    workload: 0, currentProject: null,
    skills: [
      { name: 'Java', level: 5, years: 5 }, { name: 'Spring Boot', level: 4, years: 4 },
      { name: 'AWS', level: 4, years: 3 }, { name: 'Docker', level: 4, years: 3 },
      { name: 'PostgreSQL', level: 4, years: 4 },
    ],
    certs: ['AWS SAA', 'Oracle Java SE'],
    japanese: 'N2', english: 'TOEIC 700',
    mobilizable: true, visaStatus: 'active', note: 'Sẵn sàng sang JP', rating: 4.5,
  },
  {
    id: 'ENG-102', name: 'Dang Thi Lan', initials: 'DL', color: '#EC4899',
    location: 'vn', level: 'Senior', years: 6, team: 'VN Frontend',
    bucho: 'Nguyen Manager', status: 'available', availableFrom: '2026-03-01',
    workload: 0, currentProject: null,
    skills: [
      { name: 'React', level: 5, years: 6 }, { name: 'TypeScript', level: 5, years: 4 },
      { name: 'Next.js', level: 4, years: 3 }, { name: 'Angular', level: 3, years: 2 },
      { name: 'Node.js', level: 4, years: 4 },
    ],
    certs: ['AWS SAA'], japanese: 'N2', english: 'Business',
    mobilizable: true, visaStatus: 'needs_new', note: 'Cần xin visa mới (~3 tuần)', rating: 4.7,
  },
  {
    id: 'ENG-103', name: 'Bui Quoc Khanh', initials: 'BK', color: '#0891B2',
    location: 'vn', level: 'Senior', years: 7, team: 'VN DevOps',
    bucho: 'Tran Manager', status: 'partial', availableFrom: '2026-03-15',
    workload: 50, currentProject: 'Offshore Project X',
    skills: [
      { name: 'AWS', level: 5, years: 6 }, { name: 'Kubernetes', level: 5, years: 4 },
      { name: 'Terraform', level: 5, years: 4 }, { name: 'Jenkins', level: 4, years: 5 },
      { name: 'Python', level: 4, years: 5 },
    ],
    certs: ['AWS SAP', 'CKA', 'HashiCorp Terraform'],
    japanese: 'N2', english: 'TOEIC 800',
    mobilizable: true, visaStatus: 'active', note: 'DevOps chuyên sâu cloud native', rating: 4.8,
  },
  {
    id: 'ENG-104', name: 'Nguyen Thi Thu', initials: 'NT', color: '#D97706',
    location: 'vn', level: 'Middle', years: 3, team: 'VN Backend',
    bucho: 'Nguyen Manager', status: 'available', availableFrom: '2026-03-01',
    workload: 0, currentProject: null,
    skills: [
      { name: 'Java', level: 3, years: 3 }, { name: 'Spring Boot', level: 3, years: 2 },
      { name: 'MySQL', level: 3, years: 3 }, { name: 'Docker', level: 2, years: 1 },
    ],
    certs: [], japanese: 'N2', english: 'Giao tiếp',
    mobilizable: true, visaStatus: 'active', note: 'Đang học thêm AWS', rating: 4.0,
  },
  {
    id: 'ENG-105', name: 'Phan Van Long', initials: 'PL', color: '#059669',
    location: 'vn', level: 'Senior', years: 5, team: 'VN AI/ML',
    bucho: 'Tran Manager', status: 'busy', availableFrom: '2026-05-01',
    workload: 100, currentProject: 'AI Project Alpha',
    skills: [
      { name: 'Python', level: 5, years: 5 }, { name: 'Machine Learning', level: 5, years: 4 },
      { name: 'TensorFlow', level: 4, years: 3 }, { name: 'AWS', level: 4, years: 3 },
      { name: 'FastAPI', level: 4, years: 2 },
    ],
    certs: ['AWS ML Specialty', 'Google ML Engineer'],
    japanese: 'N2', english: 'Business',
    mobilizable: true, visaStatus: 'active', note: 'AI/ML chuyên sâu', rating: 4.9,
  },

  // === VIETNAM ENGINEERS (offshore only) ===
  {
    id: 'ENG-201', name: 'Tran Van Minh', initials: 'TM', color: '#6366F1',
    location: 'vn', level: 'Middle', years: 3, team: 'VN Backend',
    bucho: 'Le Manager', status: 'available', availableFrom: '2026-03-01',
    workload: 0, currentProject: null,
    skills: [
      { name: '.NET', level: 4, years: 3 }, { name: 'C#', level: 4, years: 3 },
      { name: 'SQL Server', level: 3, years: 3 }, { name: 'Azure', level: 3, years: 2 },
    ],
    certs: ['Azure Developer Associate'], japanese: 'N3', english: 'TOEIC 600',
    mobilizable: false, note: 'Đang học N2, thi tháng 7', rating: 4.1,
  },
  {
    id: 'ENG-202', name: 'Le Thi Hong', initials: 'LH', color: '#BE185D',
    location: 'vn', level: 'Junior', years: 1, team: 'VN Frontend',
    bucho: 'Le Manager', status: 'available', availableFrom: '2026-03-01',
    workload: 0, currentProject: null,
    skills: [
      { name: 'React', level: 2, years: 1 }, { name: 'JavaScript', level: 3, years: 2 },
      { name: 'HTML/CSS', level: 3, years: 2 },
    ],
    certs: [], japanese: 'N3', english: 'Cơ bản',
    mobilizable: false, note: 'Fresher tiềm năng', rating: 3.8,
  },
  {
    id: 'ENG-203', name: 'Do Anh Khoa', initials: 'DK', color: '#0EA5E9',
    location: 'vn', level: 'Senior', years: 6, team: 'VN Backend',
    bucho: 'Le Manager', status: 'busy', availableFrom: '2026-07-01',
    workload: 100, currentProject: 'Offshore Project Z',
    skills: [
      { name: 'Java', level: 5, years: 6 }, { name: 'Kotlin', level: 4, years: 3 },
      { name: 'Android', level: 4, years: 4 }, { name: 'Spring Boot', level: 4, years: 4 },
    ],
    certs: ['Oracle Java OCP'], japanese: 'Giao tiếp', english: 'Business',
    mobilizable: false, note: 'Mobile + Backend đa năng', rating: 4.6,
  },
];

// Stats summary
const STATS = {
  total: { jp: 120, vn: 1000 },
  available: { jp: 18, vn: 169 },
  soonAvailable: { jp: 9, vn: 85 },  // within 30 days
  utilization: { jp: 87, vn: 82 },
  mobilizable: 43,
};

// Alert items
const ALERTS = [
  { type: 'danger',  icon: '🔴', text: '5 kỹ sư chưa có dự án > 2 tuần' },
  { type: 'warning', icon: '🟡', text: '8 chứng chỉ sắp hết hạn trong 60 ngày' },
  { type: 'warning', icon: '🟡', text: '3 dự án đang thiếu nhân lực' },
  { type: 'info',    icon: 'ℹ️',  text: '12 kỹ sư chưa cập nhật profile' },
];

// Top skills
const TOP_SKILLS = [
  { name: 'Java',       count: 312, pct: 100 },
  { name: 'React',      count: 248, pct: 79  },
  { name: 'Python',     count: 198, pct: 63  },
  { name: '.NET',       count: 156, pct: 50  },
  { name: 'AWS',        count: 134, pct: 43  },
  { name: 'TypeScript', count: 112, pct: 36  },
  { name: 'Docker',     count: 98,  pct: 31  },
  { name: 'Kubernetes', count: 65,  pct: 21  },
];

// Avatar colors pool
const AVATAR_COLORS = [
  '#4F46E5','#7C3AED','#0891B2','#DC2626','#059669',
  '#D97706','#EC4899','#0EA5E9','#6366F1','#BE185D',
];

function getAvatarColor(idx) {
  return AVATAR_COLORS[idx % AVATAR_COLORS.length];
}

// Helper: get status badge HTML
function statusBadge(eng) {
  const _t = (typeof t === 'function') ? t : (k) => k;
  if (eng.status === 'available') {
    const label = eng.workload === 0 ? _t('status.free_now') : _t('status.available_pct');
    return `<span class="badge badge--available"><span class="badge__dot"></span>${label}</span>`;
  }
  if (eng.status === 'partial') {
    return `<span class="badge badge--partial"><span class="badge__dot"></span>${100-eng.workload}${_t('status.partial')}</span>`;
  }
  return `<span class="badge badge--busy"><span class="badge__dot"></span>${_t('status.busy_pct')} ${eng.workload}%</span>`;
}

function locationBadge(eng) {
  const _t = (typeof t === 'function') ? t : (k) => k;
  if (eng.location === 'jp') return `<span class="loc-badge loc-badge--jp">${_t('loc.jp')}</span>`;
  return `<span class="loc-badge loc-badge--vn">${_t('loc.vn')}</span>`;
}

function skillStars(level) {
  return Array.from({length:5}, (_,i) =>
    `<span class="star ${i < level ? 'star--filled' : ''}">★</span>`
  ).join('');
}

function availableText(eng) {
  const _t = (typeof t === 'function') ? t : (k) => k;
  if (eng.status === 'available') return _t('avail.now');
  const _lang = (typeof getLang === 'function') ? getLang() : 'vi';
  const locale = _lang === 'ja' ? 'ja-JP' : 'vi-VN';
  const d = new Date(eng.availableFrom);
  return `${_t('avail.from')} ${d.toLocaleDateString(locale, {day:'2-digit', month:'2-digit', year:'numeric'})}`;
}
