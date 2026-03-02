# Plan: UI Standards Refactor — Phase 1+2 Screens

## Context
Phase 0–2 đã hoàn tất nhưng các màn hình hiện tại có nhiều vấn đề về chất lượng code:
- **~50+ hardcoded strings** tiếng Nhật rải rác trong component (không dùng i18n)
- **Raw HTML `<input>`** thay vì Ant Design `<Input>` trong form fields
- **Nested Form.Item** bug trong SkillsTab
- **Blank loading state** — EmployeeDetail trả `null` khi đang load, không có skeleton
- **Inline `<style>` tag** trong EmployeeList
- **Thiếu tests** cho 3 common components (SkillLevelBadge, ApprovalBadge, PageHeader)

Mục tiêu: đưa tất cả màn hình Phase 1+2 lên chuẩn UI Designer (i18n hoàn chỉnh, code quality, test coverage).

---

## Issues Found (by file)

### `Approvals/index.tsx` — ~25 hardcoded strings
- Tất cả column headers: `'社員番号'`, `'氏名'`, `'スキル'`, `'自己レベル'`, `'経験年数'`, `'コメント'`, `'申請日'`, `'操作'`, `'資格名'`, `'取得日'`, `'有効期限'`, `'スコア'`
- Card titles: `スキル申請`, `資格申請`
- Empty states, modal titles, form labels, validation messages
- `toLocaleDateString('ja-JP')` — hardcoded locale

### `SkillsTab.tsx` — ~15 hardcoded strings + 3 code bugs
- Column concat: `` t('skillLevel.label') + '（自己）' `` → cần key riêng
- Modal titles, form labels, validation messages
- **Bug**: dùng `<input>` (HTML raw) thay vì `<Input>` (Ant Design) — 3 chỗ
- **Bug**: Nested `Form.Item name="self_comment"` (lines 260–273) — cần xóa wrapper thừa

### `CertificationsTab.tsx` — cùng pattern với SkillsTab (giả định tương tự)
- Modal titles, form labels, validation messages (cần đọc và fix)

### `EmployeeDetail/index.tsx` — 10 hardcoded strings + 1 UX bug
- Form/Description labels: `'氏名（日本語）'`, `'Name (English)'`, `'Tên (Tiếng Việt)'`, `'Slack ID'` (4 chỗ)
- Placeholder: `'Phase 3 で実装予定'` (2 chỗ)
- **UX bug**: `if (isLoading || !emp) return null` — blank page, cần Skeleton + Alert(error)

### `Login/index.tsx` — 2 hardcoded strings
- `'IT人材管理プラットフォーム'` subtitle
- `'Google OAuth は設定後に利用できます。'` info message

### `EmployeeList/index.tsx` — 1 code quality issue
- `<style>{`.clickable-row { cursor: pointer; }`}</style>` — inline style tag, dùng `style` prop thay thế

---

## Files to Modify (9 files)

| # | File | Thay đổi |
|---|------|----------|
| 1 | `frontend/src/i18n/locales/ja/common.json` | Thêm ~40 keys mới |
| 2 | `frontend/src/i18n/locales/en/common.json` | Cùng keys, tiếng Anh |
| 3 | `frontend/src/i18n/locales/vi/common.json` | Cùng keys, tiếng Việt |
| 4 | `frontend/src/pages/Login/index.tsx` | Fix 2 hardcoded strings |
| 5 | `frontend/src/pages/Employees/List/index.tsx` | Xóa `<style>` tag |
| 6 | `frontend/src/pages/Employees/Detail/index.tsx` | Fix labels, add Skeleton/Alert |
| 7 | `frontend/src/pages/Employees/Detail/SkillsTab.tsx` | Fix ~15 strings, fix 3 code bugs |
| 8 | `frontend/src/pages/Employees/Detail/CertificationsTab.tsx` | Fix hardcoded strings (cùng pattern) |
| 9 | `frontend/src/pages/Approvals/index.tsx` | Fix ~25 hardcoded strings |

## Files to Create (3 test files)

| # | File | Nội dung |
|---|------|----------|
| 10 | `frontend/src/components/common/SkillLevelBadge/__tests__/SkillLevelBadge.test.tsx` | Render levels 1–5, tooltip, dots |
| 11 | `frontend/src/components/common/ApprovalBadge/__tests__/ApprovalBadge.test.tsx` | Render PENDING/APPROVED/REJECTED |
| 12 | `frontend/src/components/common/PageHeader/__tests__/PageHeader.test.tsx` | Title, breadcrumbs, extra actions |

---

## i18n Keys to Add (3 language files)

### `auth` section
```json
"tagline": "IT人材管理プラットフォーム",
"googleNotReady": "Google OAuth は設定後に利用できます。"
```

### `profile` section
```json
"nameJa": "氏名（日本語）",
"nameEn": "Name (English)",
"nameVi": "Tên (Tiếng Việt)",
"slackId": "Slack ID"
```

### `common` section
```json
"comingSoon": "Phase {{phase}} で実装予定"
```

### `skill` section (new)
```json
"skill": {
  "submitSkill": "スキルを申請",
  "applyModal": "スキル申請",
  "selectSkill": "スキル",
  "selectSkillPlaceholder": "スキルを選択...",
  "selectSkillRequired": "スキルを選択してください",
  "selfLevelCol": "レベル（自己）",
  "approvedLevelCol": "レベル（承認）",
  "selfLevelForm": "スキルレベル（1〜5）",
  "selfLevelRequired": "レベルを入力してください",
  "experienceYears": "経験年数",
  "experienceYearsAddon": "年",
  "commentField": "コメント",
  "commentPlaceholder": "自己PR、プロジェクト実績など",
  "approveModal": "スキル承認: {{name}}",
  "rejectModal": "差し戻し: {{name}}",
  "selfLevelInfo": "申請レベル: Lv{{level}} {{label}}",
  "approvedLevelForm": "承認レベル（1〜5）",
  "approvedLevelRequired": "承認レベルを入力してください",
  "approverComment": "コメント（任意）",
  "approverCommentPlaceholder": "承認コメント",
  "rejectReason": "差し戻し理由",
  "rejectReasonPlaceholder": "差し戻し理由を記入してください",
  "rejectReasonRequired": "差し戻し理由を入力してください"
}
```

### `approval` section (thêm vào existing)
```json
"skillSubmission": "スキル申請",
"certSubmission": "資格申請",
"noSkillsPending": "承認待ちのスキル申請はありません",
"noCertsPending": "承認待ての資格申請はありません",
"noPending": "承認待ちの申請はありません",
"employeeNameCol": "氏名",
"skillCol": "スキル",
"selfLevelCol": "自己レベル",
"experienceYearsCol": "経験年数",
"commentCol": "コメント",
"submittedAtCol": "申請日",
"actionsCol": "操作",
"certNameCol": "資格名",
"obtainedAtCol": "取得日",
"expiresAtCol": "有効期限",
"scoreCol": "スコア",
"approveSkillTitle": "スキル承認: {{name}}",
"rejectSkillTitle": "差し戻し: {{name}}",
"approveCertTitle": "資格承認: {{name}}",
"rejectCertTitle": "差し戻し: {{name}}"
```

---

## Implementation Steps

### Step 1: i18n files (ja/en/vi) — nền tảng cho mọi thứ còn lại
Thêm tất cả keys mới vào cả 3 file cùng lúc. Nhất quán key structure.

### Step 2: Login/index.tsx
- Line 71: `'IT人材管理プラットフォーム'` → `t('auth.tagline')`
- Line 41: `'Google OAuth は...'` → `t('auth.googleNotReady')`

### Step 3: EmployeeList/index.tsx
- Line 236: xóa `<style>` tag, thêm `style={{ cursor: 'pointer' }}` vào `onRow`

### Step 4: EmployeeDetail/index.tsx
- Thêm `isError` từ `useQuery`
- Thay `return null` bằng conditional: Skeleton khi loading, Alert khi error
- Form labels: `'氏名（日本語）'` → `t('profile.nameJa')`, tương tự cho En/Vi/Slack
- Descriptions labels: cùng pattern
- Placeholder: `'Phase 3 で実装予定'` → `t('common.comingSoon', { phase: 3 })`

### Step 5: SkillsTab.tsx
- Fix 3 `<input>` → `<Input>` (Ant Design)
- Fix nested `Form.Item` bug (lines 260–273)
- Replace `t('skillLevel.label') + '（自己）'` → `t('skill.selfLevelCol')`
- Replace tất cả hardcoded strings với i18n keys
- Button: `{t('action.submit')}スキル` → `t('skill.submitSkill')`

### Step 6: CertificationsTab.tsx
- Đọc file, áp dụng cùng pattern fix như SkillsTab (replace hardcoded strings)

### Step 7: Approvals/index.tsx
- Replace tất cả ~25 hardcoded strings với i18n keys
- `toLocaleDateString('ja-JP')` → `toLocaleDateString()` (dùng browser locale)
- Card titles, column headers, empty states, modal titles/labels dùng `t()`

### Step 8: Add tests (3 files)
Pattern giống `StatusBadge.test.tsx`:
- Wrap với `I18nextProvider`
- Test render variants
- Use `container.querySelector('.ant-tag')` cho Ant Design tags

---

## SkillsTab Bug Detail

**Nested Form.Item (bug)**:
```tsx
// TRƯỚC (bug: nested Form.Item)
<Form.Item name="self_comment" label="コメント">
  <Form.Item name="self_comment">   {/* ← thừa, xóa */}
    <input ... />
  </Form.Item>
</Form.Item>

// SAU (fix)
<Form.Item name="self_comment" label={t('skill.commentField')}>
  <Input.TextArea placeholder={t('skill.commentPlaceholder')} rows={3} />
</Form.Item>
```

**Raw `<input>` → `<Input>` (3 chỗ)**:
- `self_comment` field trong apply modal
- `approver_comment` field trong approve modal
- `approver_comment` field trong reject modal

---

## EmployeeDetail Loading State

```tsx
// TRƯỚC
if (isLoading || !emp) return null

// SAU
const { data: emp, isLoading, isError } = useQuery(...)

if (isLoading) return (
  <div>
    <PageHeader title="..." breadcrumbs={[...]} />
    <Skeleton active paragraph={{ rows: 8 }} />
  </div>
)

if (isError || !emp) return (
  <div>
    <PageHeader title="..." breadcrumbs={[...]} />
    <Alert type="error" message={t('common.error')} showIcon />
  </div>
)
```

---

## Test Patterns (follow StatusBadge.test.tsx)

```tsx
// SkillLevelBadge: test levels 1–5, dots rendering, tooltip
// ApprovalBadge: test PENDING/APPROVED/REJECTED colors & icons
// PageHeader: test title render, breadcrumbs, extra prop
```

---

## Verification

```bash
docker compose exec frontend npm test
# Expected: tất cả existing 36 tests pass + 3 component tests mới → 39+ passed
```

Confirm không có TypeScript errors:
```bash
docker compose exec frontend npm run build
```
