# Plan: Dashboard — Thêm Biểu Đồ Heatmap & Biến Động

## Context

Dashboard hiện tại (Phase 6) có 4 KPI cards + 4 charts. Yêu cầu thêm:
1. **Skill Heatmap** — phân bố skill toàn công ty (category × level × số người)
2. **Biểu đồ biến động** — 2 loại:
   - **Headcount Movement Trend** — nhân viên gia nhập + rời đi theo tháng (12 tháng gần đây)
   - **Location Distribution Donut** — phân bố nhân sự theo văn phòng

---

## Layout Sau Khi Thêm

```
Row 1: [KPI ×4]
Row 2: [Utilization Trend 14col]   [Free Forecast 10col]
Row 3: [Skills Bar 12col]          [Alert Summary 12col]
Row 4: [Skill Heatmap — full width 24col]                ← NEW
Row 5: [Headcount Movement 14col]  [Location Donut 10col] ← NEW
```

---

## Thay Đổi Quan Trọng: Thêm Cột `left_at`

Employee model hiện tại không có field ngày rời công ty. Cần thêm:

### DB Migration (`backend/alembic/versions/006_add_left_at.py`)
```python
op.add_column('employees', sa.Column('left_at', sa.Date(), nullable=True))
```

### Employee Model (`backend/app/models/employee.py`)
```python
left_at: Mapped[date | None] = mapped_column(Date, nullable=True)
```

### Employee Schema (`backend/app/schemas/employee.py`)
```python
# EmployeeUpdate — thêm:
left_at: date | None = None
```

### Employee Service (`backend/app/services/employee_service.py`)
Khi update employee: nếu `is_active` đổi từ `True → False` VÀ `left_at` chưa được set:
```python
if 'is_active' in data and data['is_active'] is False:
    if employee.left_at is None:
        employee.left_at = date.today()
```

---

## Files

### Backend
| File | Action |
|------|--------|
| `backend/alembic/versions/006_add_left_at.py` | NEW — migration |
| `backend/app/models/employee.py` | Thêm `left_at` column |
| `backend/app/schemas/employee.py` | Thêm `left_at` vào Update/Detail schemas |
| `backend/app/services/employee_service.py` | Auto-set `left_at` khi deactivate |
| `backend/app/schemas/dashboard.py` | Thêm 3 schema mới |
| `backend/app/services/dashboard_service.py` | Thêm 3 service functions |
| `backend/app/routers/dashboard.py` | Thêm 3 GET endpoints |
| `backend/tests/test_dashboard.py` | Thêm ~6 test cases |

### Frontend
| File | Action |
|------|--------|
| `frontend/src/api/dashboard.ts` | Thêm types + API functions |
| `frontend/src/components/dashboard/SkillHeatmapChart.tsx` | NEW |
| `frontend/src/components/dashboard/HeadcountTrendChart.tsx` | NEW (joined + left bars) |
| `frontend/src/components/dashboard/LocationDonutChart.tsx` | NEW |
| `frontend/src/pages/Dashboard/index.tsx` | Thêm Row 4 + Row 5 |
| `frontend/src/i18n/locales/ja/common.json` | 7 keys mới |
| `frontend/src/i18n/locales/en/common.json` | 7 keys mới |
| `frontend/src/i18n/locales/vi/common.json` | 7 keys mới |

---

## Backend Implementation

### Schemas (`dashboard.py`)

```python
# Skill Heatmap
class SkillHeatmapCell(BaseModel):
    category: str   # SkillCategory.name_ja
    level: int      # approved_level 1–5
    count: int      # distinct employee count (APPROVED)

class SkillHeatmapResponse(BaseModel):
    categories: list[str]        # ordered by sort_order
    items: list[SkillHeatmapCell]

# Headcount Movement Trend
class HeadcountTrendItem(BaseModel):
    month: str    # "2026-03"
    joined: int   # employees WHERE joined_at IN [month_start, month_end]
    left: int     # employees WHERE left_at IN [month_start, month_end]

class HeadcountTrendResponse(BaseModel):
    months: list[HeadcountTrendItem]

# Location Distribution
class DistributionItem(BaseModel):
    label: str   # "HANOI", "HCMC", ...
    count: int

class LocationDistributionResponse(BaseModel):
    items: list[DistributionItem]
```

### Service Functions (`dashboard_service.py`)

**`get_skill_heatmap(db)`**
```python
# SELECT sc.name_ja, es.approved_level, COUNT(DISTINCT es.employee_id)
# FROM employee_skills es
# JOIN skills s ON es.skill_id = s.id
# JOIN skill_categories sc ON s.category_id = sc.id
# WHERE es.status = 'APPROVED' AND es.approved_level IS NOT NULL
# GROUP BY sc.name_ja, sc.sort_order, es.approved_level
# ORDER BY sc.sort_order, es.approved_level
```

**`get_headcount_trend(db, months=12)`**
```python
# Dùng _add_months() helper đã có trong file
# For each month in past N months:
#   joined = COUNT(employees WHERE joined_at IN [first, last])
#   left   = COUNT(employees WHERE left_at  IN [first, last])
```

**`get_location_distribution(db)`**
```python
# SELECT office_location, COUNT(*)
# FROM employees WHERE is_active=True
# GROUP BY office_location
```

### Router (`dashboard.py`) — 3 endpoints mới

```python
GET /dashboard/skill-heatmap         → SkillHeatmapResponse
GET /dashboard/headcount-trend       → HeadcountTrendResponse (?months=12)
GET /dashboard/location-distribution → LocationDistributionResponse
```
Tất cả dùng `require_role(*DASHBOARD_ROLES)`.

---

## Frontend Implementation

### API Types (`dashboard.ts`)

```typescript
export interface SkillHeatmapCell { category: string; level: number; count: number }
export interface SkillHeatmapResponse { categories: string[]; items: SkillHeatmapCell[] }

export interface HeadcountTrendItem { month: string; joined: number; left: number }
export interface HeadcountTrendResponse { months: HeadcountTrendItem[] }

export interface DistributionItem { label: string; count: number }
export interface LocationDistributionResponse { items: DistributionItem[] }
```

### SkillHeatmapChart.tsx — Custom CSS Grid

recharts không có native heatmap → dùng CSS grid thuần.

```
Layout:
┌──────────────┬────┬────┬────┬────┬────┐
│              │ L1 │ L2 │ L3 │ L4 │ L5 │  ← header row
├──────────────┼────┼────┼────┼────┼────┤
│ バックエンド  │ 12 │  8 │  5 │  2 │  1 │
│ フロントエンド│  9 │  6 │  3 │  1 │  0 │
└──────────────┴────┴────┴────┴────┴────┘

Cell color: rgba(22, 119, 255, count/maxCount)
Cell 0: background #f5f5f5, no text
```

- `display: grid`, `grid-template-columns: minmax(120px,auto) repeat(5, 1fr)`
- Ant Design `Tooltip` mỗi cell: "X người — {category} Lv{level}"
- `overflow-x: auto` (scroll ngang trên mobile)

### HeadcountTrendChart.tsx — Grouped BarChart

recharts `BarChart` với 2 bars mỗi tháng:
```
      ┌──┐
      │  │ ← joined (purple #722ed1)
   ┌──┤  │
   │  ├──┤ ← left (red #f5222d)
───┴──┴──┴──
   Jan  Feb
```

- `<Bar dataKey="joined" fill="#722ed1" name="入社" />`
- `<Bar dataKey="left" fill="#f5222d" name="退社" />`
- `<Legend />` để phân biệt 2 series
- Tooltip hiển thị cả 2 giá trị
- Height: 220px (cao hơn chút để có chỗ cho legend)

### LocationDonutChart.tsx

recharts `PieChart` + `Pie` với `innerRadius`:
```tsx
<PieChart>
  <Pie data={data} dataKey="count" nameKey="label"
       innerRadius={50} outerRadius={80} paddingAngle={3}>
    {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
  </Pie>
  <Tooltip formatter={(v, name) => [`${v}名`, t(`officeLocation.${name}`)]} />
  <Legend formatter={(label) => t(`officeLocation.${label}`)} />
</PieChart>
```
Dùng `t('officeLocation.HANOI')` etc. (i18n key đã có sẵn).

### i18n Keys (7 keys × 3 ngôn ngữ)

| Key | JA | EN | VI |
|-----|----|----|-----|
| `dashboard.skillHeatmap` | 全社スキルマトリクス（レベル別） | Company Skill Matrix (by Level) | Ma trận kỹ năng (theo cấp độ) |
| `dashboard.heatmapLevel` | レベル | Level | Cấp độ |
| `dashboard.heatmapTooltip` | {{count}}名 | {{count}} people | {{count}} người |
| `dashboard.headcountTrend` | 入退社トレンド（過去{{months}}ヶ月） | Headcount Movement (Last {{months}} Months) | Biến động nhân sự ({{months}} tháng) |
| `dashboard.headcountJoined` | 入社 | Joined | Gia nhập |
| `dashboard.headcountLeft` | 退社 | Left | Rời công ty |
| `dashboard.locationDistribution` | 拠点別人員分布 | Headcount by Office | Phân bố theo văn phòng |

---

## Verification

```bash
# 1. Chạy migration mới
docker compose exec backend alembic upgrade head

# 2. Backend tests
docker compose exec backend pytest tests/test_dashboard.py -v

# 3. Frontend build (TypeScript check)
docker compose exec frontend npm run build

# 4. Frontend tests
docker compose exec frontend npm test

# 5. Visual — http://localhost:3000/dashboard (login as admin)
#    Row 4: Skill Heatmap — grid gradient xanh
#    Row 5 left: Bar chart 12 tháng với 2 bars (入社/退社)
#    Row 5 right: Donut chart phân bố văn phòng
```
