# Plan: UI Redesign + Missing Features (Mockup Alignment)

## Context

Bản mockup HTML tại `C:\Users\NTQJ-\EmployeeHub-old-ui\engineer-hub` có 7 trang và thiết kế phong phú hơn app hiện tại. Người dùng muốn:
1. Đối chiếu & liệt kê chức năng thiếu
2. Sửa giao diện giống mockup hoàn toàn (Indigo theme, Inter font, dark sidebar)
3. Thêm 3 trang còn thiếu + cải thiện trang hiện có

---

## Gap Analysis: Mockup vs. Current App

### Trang hoàn toàn thiếu (3)
| Trang mockup | Route đề xuất | Mô tả |
|---|---|---|
| `skills.html` | `/skills` | Skill Matrix toàn công ty (engineer rows x skill columns) |
| `certs.html` | `/certifications` | Cert Overview toàn công ty (grouped by category, holders) |
| `availability.html` | `/availability` | Gantt 6 tháng (engineer x month, FREE/PARTIAL/BUSY) |

### Tính năng thiếu trong trang hiện có
| Trang | Tính năng thiếu |
|---|---|
| Employee List | Card view toggle, Slide-out detail panel (Drawer), Workload % column, Mobilizable column |
| Dashboard | Location filter tabs (All/JP/VN), Mobilizable widget |
| Employee Profile | Goals tracking with progress bars, Notes for manager tab |

### UI/Design gaps
| Element | Mockup | Hiện tại |
|---|---|---|
| Primary color | #4F46E5 Indigo | #1677ff Blue |
| Font | Inter | System default |
| Sidebar | Dark indigo (#1E1B4B) white text | White background |
| Cards | shadow-md, radius 12px | Ant Design default |
| Status badges | Emoji-based (green/yellow/red circles) | Ant Design Tag |

---

## Phase 1: UI Design System Overhaul

**Mục tiêu:** Đổi visual giống mockup — HIGH IMPACT, ít rủi ro

### 1.1 Ant Design Theme (ConfigProvider)
**File:** `frontend/src/main.tsx`

Wrap app với ConfigProvider:
- `colorPrimary: '#4F46E5'` (Indigo)
- `colorSuccess: '#10B981'`
- `colorWarning: '#F59E0B'`
- `colorError: '#EF4444'`
- `borderRadius: 8`
- `fontFamily: 'Inter, sans-serif'`
- Layout sider background: `#1E1B4B`
- Menu dark theme: `darkItemBg: '#1E1B4B'`, `darkItemSelectedBg: '#4F46E5'`

### 1.2 Inter Font + CSS tokens
**Files:** `frontend/index.html`, `frontend/src/index.css`
- Link Inter font từ Google Fonts
- CSS custom properties: `--color-primary`, `--shadow-card`, etc.

### 1.3 Sidebar Dark Indigo
**File:** `frontend/src/components/common/AppLayout/Sidebar.tsx`
- `theme="dark"` trên Ant Design Menu
- Background `#1E1B4B`
- Logo text: white
- Active item highlight: `#4F46E5`
- Text: white/gray-400

### 1.4 AppLayout Background
**File:** `frontend/src/components/common/AppLayout/index.tsx`
- Content background: `#F9FAFB` (gray-50, giống mockup)

---

## Phase 2: Engineer List Enhancements

### 2.1 Backend: workload + mobilizable fields
**File:** `backend/app/schemas/employee.py` — `EmployeeListItem`
- Thêm `workload_percent: int | None = None` (0-100, từ active assignments)
- Thêm `is_mobilizable: bool = False` (HANOI/HCMC + visa còn hạn)

**File:** `backend/app/services/employee_service.py`
- Subquery cho `workload_percent` = SUM(allocation_percent) assignments đang active
- `is_mobilizable` = office_location IN ('HANOI','HCMC') AND visa.expires_at > today
- Trả về cùng với EmployeeListItem response

### 2.2 Frontend: Card/Table Toggle + New Columns
**File:** `frontend/src/pages/Employees/List/index.tsx`
- State `viewMode: 'table' | 'card'`
- Header: Button group ☰ Bảng | ⊞ Thẻ
- Table: thêm cột Workload (Progress bar), Mobilizable (✈️ badge)

**File:** `frontend/src/pages/Employees/List/EmployeeCard.tsx` (NEW)
- Card hiển thị: avatar (color + initials), name, location badge, status badge, level
- Meta: experience, Japanese level
- Top skills (4 tags)
- Mobilizable flag (✈️)
- "Xem →" button

### 2.3 Frontend: Slide-out Detail Panel (Drawer)
**File:** `frontend/src/pages/Employees/List/EmployeeDetailPanel.tsx` (NEW)
- Ant Design `Drawer` từ phải (width 480px)
- Content: avatar, name, ID, basic info grid (6 fields), work status, skills list, certs
- Footer: "Xem full profile →" navigate to `/employees/:id` | "Đóng"
- Click row table/card → mở Drawer (không navigate ngay)

---

## Phase 3: Backend APIs cho 3 trang mới

### 3.1 Availability API
**Schema file:** `backend/app/schemas/availability.py` (NEW)
```
AvailabilityMonth: { month, status (FREE|PARTIAL|BUSY), allocation (0-100), project_name? }
EmployeeAvailability: { employee: EmployeeListItem, months: list[AvailabilityMonth] }
AvailabilityResponse: { months_header: list[str], items: list[EmployeeAvailability] }
```

**Service file:** `backend/app/services/availability_service.py` (NEW)
- Input: months=6, offset_months=0 (navigation), filters
- Cho mỗi engineer, mỗi tháng:
  - Query assignments active trong tháng đó
  - allocation = SUM(allocation_percent)
  - status = FREE(0) | PARTIAL(1-99) | BUSY(>=100)
- Dùng Python `timedelta` (không dùng PostgreSQL INTERVAL)

**Router:** `backend/app/routers/availability.py` (NEW)
```
GET /api/v1/availability?months=6&offset_months=0&location=&search=&status=
```
Access: Sales, Manager, Department Head, Director, Admin

### 3.2 Skill Matrix API
**Schema file:** `backend/app/schemas/skillmatrix.py` (NEW)
```
EngineerSkillEntry: { skill_id, level: int|None, years: int|None }
EngineerRow: { employee: EmployeeListItem, skills: dict[skill_id, EngineerSkillEntry] }
SkillMatrixCategory: { id, name_ja, skills: list[{id, name}] }
SkillMatrixResponse: { categories: list[SkillMatrixCategory], engineers: list[EngineerRow] }
```

**Service file:** `backend/app/services/skillmatrix_service.py` (NEW)
- JOIN employee_skills + skills + skill_categories (status = APPROVED)
- Group by engineer, pivot to dict
- Filter: location, level_min, category_id, free_only, search

**Router:** `backend/app/routers/skillmatrix.py` (NEW)
```
GET /api/v1/skills/matrix?location=&level_min=&category_id=&free_only=&search=
```
Access: Manager+

### 3.3 Cert Overview API
**File:** `backend/app/services/certification_service.py` (thêm function)
- `get_company_cert_overview(db, filters)` — group by cert_master + category
- Per cert: list of APPROVED holders with expiry status

**File:** `backend/app/routers/certifications.py` (thêm endpoint)
```
GET /api/v1/certifications/overview?location=&category=&status=&search=
Returns: { categories: [{name, certs: [{master, holders, expiry_stats}]}] }
```
Access: Manager+

### 3.4 Backend Tests
- `backend/tests/test_availability.py` — 5 tests (200 manager, 403 member, data accuracy)
- `backend/tests/test_skillmatrix.py` — 4 tests (200, 403, data format)
- `backend/tests/test_cert_overview.py` — 4 tests

---

## Phase 4: 3 Trang Mới

### 4.1 `/availability` — Availability Timeline
**File:** `frontend/src/pages/Availability/index.tsx` (NEW)
**File:** `frontend/src/api/availability.ts` (NEW)

Layout (giống mockup `availability.html`):
```
[Header] [4 Summary cards: Rảnh ngay | Rảnh 30d | Rảnh 3m | Bận 100%]
[Month nav: ◀ Mar–Aug 2026 ▶]
[Filter bar: search | location | skill | status | mobilizable checkbox]
[Gantt table]:
  Sticky header row: Engineer | Mar | Apr | May | Jun | Jul | Aug
  Body rows: [avatar+name+level+skills+location] [colored cells per month]
  Footer: "📊 Tổng KS rảnh" | [X rảnh per month]
[Legend: green=Rảnh | amber=50% | red=Bận]
```

Cell colors:
- FREE: `#D1FAE5` bg + `#065F46` text (green)
- PARTIAL: `#FEF3C7` bg + `#92400E` text (amber)
- BUSY: `#FEE2E2` bg + `#991B1B` text (red)

State: `offsetMonths` (navigation), filters, drawer for engineer detail

### 4.2 `/skills` — Skill Matrix
**File:** `frontend/src/pages/SkillMatrix/index.tsx` (NEW)
**File:** `frontend/src/api/skillmatrix.ts` (NEW)

Layout (giống mockup `skills.html`):
```
[Header + ⊞ Ma trận | 📊 Biểu đồ toggle + Export]
[4 Stats: 👥 engineers | 🔥 top skill | ⭐ experts | ⚠️ gaps]
[Filters: search | location | level_min | category | free_only]
[Matrix View]:
  Color-coded category sub-headers
  Skill names sub-row
  Engineer rows: [avatar+name+badge] [level cells 1-5 or —]
  Footer: skill count totals
[Chart View]:
  Grid of skill cards (stacked bar per level)
```

Level cell colors:
- 1: `#FEF3C7` (amber light)
- 2: `#FED7AA` (orange light)
- 3: `#D1FAE5` (green light)
- 4: `#BAE6FD` (blue light)
- 5: `#DDD6FE` (purple light)

### 4.3 `/certifications` — Cert Overview
**File:** `frontend/src/pages/Certifications/index.tsx` (NEW)

Layout (giống mockup `certs.html`):
```
[Header + Export + Add Cert]
[4 Stats: 🏅 total | 📋 types | ⚠️ expiring 60d | 🏆 top cert]
[⚠️ Expiry warning banner (if any)]
[Filters: search | category | location | status]
[Sections grouped by category]:
  Section header: icon + name + count
  Cert cards grid:
    - Cert name + vendor
    - Expiry status badge (⚠️ Soon / ✅ Valid / ♾️ No expiry)
    - Holder avatars (max 8, "+N more")
    - 🇯🇵 X JP · 🇻🇳 Y VN | Tổng: Z
```

---

## Phase 5: Dashboard + Profile Enhancements

### 5.1 Dashboard Location Filter
**File:** `frontend/src/pages/Dashboard/index.tsx`
- State `locationFilter: 'all' | 'JP' | 'VN'`
- Horizontal Tab bar dưới PageHeader
- Pass `?location=JP|VN` vào tất cả dashboard API calls

**Backend:** Cập nhật `/dashboard/overview`, `/dashboard/skill-heatmap`, etc. để accept `location` param

### 5.2 Dashboard Mobilizable Widget
**Backend:** `GET /api/v1/dashboard/mobilizable`
Returns: `{ total, valid_visa, need_visa }`

**Frontend:** Thêm card ✈️ trên Dashboard

### 5.3 Profile: Goals + Notes Tab
**File:** `frontend/src/pages/Employees/Detail/NotesTab.tsx` (NEW)
- Notes textarea → ghi chú gửi manager
- Stored as JSON field hoặc separate table (simple: localStorage + API stub)

---

## Sidebar Navigation Updates
**File:** `frontend/src/components/common/AppLayout/Sidebar.tsx`

Thêm nav items mới:
- `/availability` — 📅 Lịch trống (sales+)
- `/skills` — 📊 Skill Matrix (manager+)
- `/certifications` — 🏅 Chứng chỉ (manager+)

---

## App.tsx Route Additions
**File:** `frontend/src/App.tsx`
```
/availability → AvailabilityPage
/skills → SkillMatrixPage
/certifications → CertificationsPage
```

---

## i18n Keys (JA/EN/VI)
**Files:** `frontend/src/i18n/locales/*/common.json`
```json
{
  "nav.availability": "Lịch trống / Availability / 空きカレンダー",
  "nav.skills": "Skill Matrix",
  "nav.certifications": "Chứng chỉ / Certifications / 資格管理",
  "availability.*": { ... },
  "skillMatrix.*": { ... },
  "certOverview.*": { ... }
}
```

---

## Files to Create/Modify

### Backend
| File | Action |
|---|---|
| `backend/app/schemas/availability.py` | NEW |
| `backend/app/services/availability_service.py` | NEW |
| `backend/app/routers/availability.py` | NEW |
| `backend/app/schemas/skillmatrix.py` | NEW |
| `backend/app/services/skillmatrix_service.py` | NEW |
| `backend/app/routers/skillmatrix.py` | NEW |
| `backend/app/services/certification_service.py` | Add overview function |
| `backend/app/routers/certifications.py` | Add overview endpoint |
| `backend/app/schemas/employee.py` | Add workload_percent, is_mobilizable |
| `backend/app/services/employee_service.py` | Compute workload + mobilizable |
| `backend/app/main.py` | Register new routers |
| `backend/tests/test_availability.py` | NEW |
| `backend/tests/test_skillmatrix.py` | NEW |

### Frontend
| File | Action |
|---|---|
| `frontend/index.html` | Add Inter font |
| `frontend/src/main.tsx` | ConfigProvider theme |
| `frontend/src/components/common/AppLayout/Sidebar.tsx` | Dark theme + new nav |
| `frontend/src/components/common/AppLayout/index.tsx` | Content bg color |
| `frontend/src/pages/Employees/List/index.tsx` | Card/Table toggle + Drawer + columns |
| `frontend/src/pages/Employees/List/EmployeeCard.tsx` | NEW |
| `frontend/src/pages/Employees/List/EmployeeDetailPanel.tsx` | NEW |
| `frontend/src/pages/Availability/index.tsx` | NEW |
| `frontend/src/pages/SkillMatrix/index.tsx` | NEW |
| `frontend/src/pages/Certifications/index.tsx` | NEW |
| `frontend/src/api/availability.ts` | NEW |
| `frontend/src/api/skillmatrix.ts` | NEW |
| `frontend/src/pages/Dashboard/index.tsx` | Location filter + Mobilizable widget |
| `frontend/src/App.tsx` | 3 new routes |
| `frontend/src/i18n/locales/*/common.json` | New keys (3 langs) |

---

## Implementation Order (per execution session)

```
Session 1: Phase 1 (Design System) — quick wins
Session 2: Phase 2 (Engineer List) + Phase 3 (Backend APIs)
Session 3: Phase 4 (3 New Pages)
Session 4: Phase 5 (Dashboard + Profile) + cleanup
```

---

## Verification

```bash
# Backend tests (after Phase 3)
docker compose exec backend pytest -v
# Expected: 162+ passed (previous 149 + ~13 new)

# Frontend TypeScript build (after each phase)
docker compose exec frontend npm run build
# Expected: built successfully (0 TS errors)

# Frontend tests
docker compose exec frontend npm test -- --run
# Expected: 90+ passed

# Visual checks (localhost:3000):
# Phase 1: Sidebar dark indigo, buttons indigo color
# Phase 2: /employees - Card/Table toggle, Drawer on row click
# Phase 3+4: /availability, /skills, /certifications pages load
# Phase 5: Dashboard location tabs, mobilizable card
```
