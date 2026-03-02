# API設計書（FastAPI）

**プロジェクト名**: EmployeeHub
**作成日**: 2026年2月28日
**バージョン**: 1.0

---

## 1. 基本方針

| 項目 | 仕様 |
|---|---|
| ベースURL | `https://api.employeehub.example.com/api/v1` |
| プロトコル | HTTPS / REST |
| データ形式 | JSON（`Content-Type: application/json`）|
| 認証 | `Authorization: Bearer <access_token>`（JWT）|
| バージョニング | URLパスによるバージョン管理（`/api/v1/`）|
| ドキュメント | `/docs`（Swagger UI）、`/redoc`（ReDoc）自動生成 |
| ページネーション | `?page=1&per_page=20` |
| エラー形式 | 統一レスポンス（後述）|

---

## 2. 認証（Auth）

### `POST /api/v1/auth/login`
メール＋パスワードでログイン。

**Request**
```json
{ "email": "user@example.com", "password": "secret" }
```
**Response 200**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### `POST /api/v1/auth/google`
Google OAuth 認証。フロントエンドから受け取ったIDトークンを検証。

**Request**
```json
{ "id_token": "google_id_token_here" }
```
**Response 200**: `login` と同じ形式

---

### `POST /api/v1/auth/refresh`
アクセストークンを更新。

**Request**
```json
{ "refresh_token": "eyJ..." }
```

---

### `DELETE /api/v1/auth/logout`
リフレッシュトークンを無効化。

---

## 3. 社員管理（Employees）

### `GET /api/v1/employees`
社員一覧（権限に応じてフィルタ自動適用）。

**Query Parameters**
| パラメータ | 型 | 説明 |
|---|---|---|
| `page` | int | ページ番号（デフォルト: 1）|
| `per_page` | int | 1ページ件数（デフォルト: 20、最大: 100）|
| `department_id` | UUID | 部署で絞り込み |
| `is_active` | bool | 在籍フラグ（デフォルト: true）|
| `q` | string | 氏名検索（部分一致）|

**Response 200**
```json
{
  "items": [
    {
      "id": "uuid",
      "name_ja": "グエン・バン・アン",
      "name_en": "Nguyen Van An",
      "employee_number": "VN-1001",
      "department": { "id": "uuid", "name_ja": "バックエンド開発部" },
      "system_role": "member",
      "office_location": "HANOI",
      "work_status": { "status": "FREE_IMMEDIATE", "free_from": null },
      "avatar_url": "https://...",
      "top_skills": ["Java", "Spring Boot", "AWS"]
    }
  ],
  "total": 1248,
  "page": 1,
  "per_page": 20
}
```

---

### `POST /api/v1/employees`
社員登録。**権限: `admin`**

**Request**
```json
{
  "employee_number": "VN-1002",
  "name_ja": "グエン・バン・アン",
  "name_en": "Nguyen Van An",
  "name_vi": "Nguyễn Văn An",
  "email": "an.nguyen@company.com",
  "department_id": "uuid",
  "system_role": "member",
  "office_location": "HANOI",
  "employment_type": "FULLTIME",
  "work_style": "REMOTE",
  "joined_at": "2021-04-01"
}
```
**Response 201**: 作成された社員オブジェクト

---

### `GET /api/v1/employees/{id}`
社員詳細。権限によって返却フィールドが異なる（給与情報等）。

**Response 200**
```json
{
  "id": "uuid",
  "employee_number": "VN-1001",
  "name_ja": "グエン・バン・アン",
  "department": { "id": "uuid", "name_ja": "バックエンド開発部" },
  "system_role": "member",
  "office_location": "HANOI",
  "work_style": "REMOTE",
  "joined_at": "2021-04-01",
  "email": "an.nguyen@company.com",
  "skills": [...],
  "certifications": [...],
  "work_status": { "status": "FREE_IMMEDIATE" },
  "visa": { "visa_type": "技人国", "expires_at": "2027-03-31" }
}
```

---

### `PUT /api/v1/employees/{id}`
社員情報更新。**権限: 本人（一部フィールド）/ `admin`（全フィールド）**

---

### `PATCH /api/v1/employees/{id}/work-status`
稼働状況更新。**権限: `manager` / `department_head` / `admin`**

**Request**
```json
{
  "status": "FREE_PLANNED",
  "free_from": "2026-03-15",
  "note": "現案件が3/14で終了予定"
}
```

---

## 4. スキル（Skills）

### `GET /api/v1/skills`
スキルマスタ一覧（カテゴリ別グループ化）。

**Response 200**
```json
{
  "categories": [
    {
      "id": "uuid",
      "name_ja": "プログラミング言語",
      "skills": [
        { "id": "uuid", "name": "Java" },
        { "id": "uuid", "name": "Python" }
      ]
    }
  ]
}
```

---

### `GET /api/v1/employees/{id}/skills`
個人スキル一覧（`status`でフィルタ可能）。

**Query**: `?status=APPROVED` / `PENDING` / `REJECTED`

---

### `POST /api/v1/employees/{id}/skills`
スキル申請。**権限: 本人**

**Request**
```json
{
  "skill_id": "uuid",
  "self_level": 3,
  "experience_years": 2.5,
  "last_used_at": "2025-12-01",
  "self_comment": "個人プロジェクトで使用"
}
```
**Response 201**

---

### `POST /api/v1/employees/{id}/skills/evidence`
証明書ファイルアップロード（multipart/form-data）。
アップロード後に返却された `file_url` をスキル申請時に使用。

**Response 200**
```json
{ "file_url": "https://storage.example.com/evidence/..." }
```

---

### `PATCH /api/v1/employee-skills/{skill_id}/approve`
スキル承認。**権限: `manager` / `department_head` / `admin`**

**Request**
```json
{
  "approved_level": 3,
  "approver_comment": "プロジェクトでの実績を確認"
}
```

---

### `PATCH /api/v1/employee-skills/{skill_id}/reject`
スキル差し戻し。**権限: `manager` / `department_head` / `admin`**

**Request**
```json
{ "approver_comment": "証明書の再提出をお願いします" }
```

---

## 5. 資格（Certifications）

### `GET /api/v1/certification-masters`
資格マスタ一覧。

---

### `GET /api/v1/employees/{id}/certifications`
個人資格一覧。

---

### `POST /api/v1/employees/{id}/certifications`
資格申請。**権限: 本人**

**Request**
```json
{
  "certification_master_id": "uuid",
  "custom_name": null,
  "score": "N2",
  "obtained_at": "2025-11-15",
  "expires_at": null,
  "file_url": "https://storage.example.com/certs/..."
}
```

---

### `PATCH /api/v1/certifications/{id}/approve`
資格承認。**権限: `manager` / `department_head` / `admin`**

### `PATCH /api/v1/certifications/{id}/reject`
資格差し戻し。

---

## 6. プロジェクト経歴（Projects）

### `GET /api/v1/employees/{id}/projects`
プロジェクト経歴一覧（`sort_order` 順）。

### `POST /api/v1/employees/{id}/projects`
経歴追加。**権限: 本人 / `manager` / `admin`**

**Request**
```json
{
  "project_name": "ECサイトリニューアル",
  "client_name": "株式会社〇〇",
  "industry": "EC",
  "role": "SE",
  "started_at": "2024-04-01",
  "ended_at": null,
  "tech_stack": ["Java", "Spring Boot", "PostgreSQL", "AWS"],
  "team_size": 8,
  "responsibilities": "バックエンドAPI設計・実装",
  "achievements": "レスポンスタイムを50%改善"
}
```

### `PUT /api/v1/employee-projects/{id}`
経歴更新。

### `DELETE /api/v1/employee-projects/{id}`
経歴削除。

### `PATCH /api/v1/employees/{id}/projects/reorder`
表示順変更（スキルシート用）。

**Request**
```json
{ "ordered_ids": ["uuid-1", "uuid-2", "uuid-3"] }
```

---

## 7. ビザ情報（Visa）

### `GET /api/v1/employees/{id}/visa`
ビザ情報取得。**権限: 本人 / `department_head` / `admin`**

### `PUT /api/v1/employees/{id}/visa`
ビザ情報更新（upsert）。**権限: `admin`（HR相当）**

**Request**
```json
{
  "visa_type": "技術・人文知識・国際業務",
  "residence_card_number": "AB12345678CD",
  "expires_at": "2027-03-31",
  "notes": "更新申請中"
}
```

---

## 8. 検索（Search）

### `POST /api/v1/search/filter`
構造化フィルター検索。**権限: `sales` / `manager` 以上**

**Request**
```json
{
  "skills": [
    { "skill_id": "uuid", "level_min": 3, "required": true },
    { "skill_id": "uuid", "required": false }
  ],
  "experience_years_min": 3,
  "work_statuses": ["FREE_IMMEDIATE", "FREE_PLANNED"],
  "free_from_before": "2026-04-01",
  "office_locations": ["HANOI", "HCMC"],
  "work_style": "REMOTE",
  "japanese_level": "N2",
  "certification_ids": ["uuid"],
  "page": 1,
  "per_page": 20
}
```

**Response 200**
```json
{
  "items": [
    {
      "employee": { ...社員基本情報... },
      "match_score": 92,
      "matched_skills": ["Java", "Spring Boot"],
      "missing_skills": [],
      "work_status": { "status": "FREE_IMMEDIATE" }
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 20
}
```

---

### `POST /api/v1/search/ai-parse`
自然言語テキストをAIで解析し、検索条件を構造化して返す。
**権限: `sales` / `manager` 以上**

バックエンドがLLM API（Claude / OpenAI）を呼び出し、JSON形式で条件を抽出。

**Request**
```json
{
  "text": "来月からJavaのバックエンド開発者が2名必要です。Spring Bootの経験が3年以上あって..."
}
```

**Response 200**
```json
{
  "summary": "Java / Spring Boot 3年以上、AWS歓迎、日本語N2以上、フルリモート、2名、翌月から",
  "criteria": {
    "skills": [
      { "name": "Java",        "skill_id": "uuid", "level_min": 3, "required": true },
      { "name": "Spring Boot", "skill_id": "uuid", "experience_years_min": 3, "required": true },
      { "name": "AWS",         "skill_id": "uuid", "required": false }
    ],
    "japanese_level": "N2",
    "work_style": "REMOTE",
    "headcount": 2,
    "free_from_before": "2026-04-01",
    "roles": ["バックエンドエンジニア"]
  },
  "unmatched_terms": ["PMの経験"]    -- スキルマスタに存在しない語句
}
```

> フロントエンドはこのレスポンスをユーザーに確認させ、修正後に `/search/filter` へ送信する。

---

### `GET /api/v1/search/saved`
保存済み検索条件一覧（本人のみ）。

### `POST /api/v1/search/saved`
検索条件を保存。

**Request**
```json
{
  "name": "Java/Spring Boot フリー案件用",
  "criteria": { ...filterリクエストと同形式... }
}
```

### `DELETE /api/v1/search/saved/{id}`
保存検索を削除。

---

## 9. 承認キュー（Approvals）

### `GET /api/v1/approvals/pending`
自分が承認すべき申請一覧。**権限: `manager` 以上**

**Response 200**
```json
{
  "skills": [
    {
      "id": "uuid",
      "employee": { "id": "uuid", "name_ja": "グエン・バン・アン" },
      "skill": { "name": "Kubernetes" },
      "self_level": 2,
      "experience_years": 1.0,
      "evidence_file_url": "https://...",
      "self_comment": "CKA取得済み",
      "submitted_at": "2026-02-25T10:00:00Z"
    }
  ],
  "certifications": [...]
}
```

---

## 10. スキルシート出力（Skill Sheet）

### `POST /api/v1/skillsheet/export`
複数社員のスキルシートを一括出力。
**権限: `sales` / `manager` 以上**

**Request**
```json
{
  "employee_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "format": "xlsx",              -- "xlsx" | "pdf"
  "output_style": "combined",   -- "combined"（1ファイル）| "zip"（個別ZIP）
  "filename_prefix": "株式会社〇〇_提案用",
  "include_salary": false
}
```

**Response 200**
```json
{
  "download_url": "https://storage.example.com/exports/skillsheet_xxx.xlsx",
  "expires_at": "2026-02-28T13:00:00Z"   -- 一時URL（1時間有効）
}
```

---

## 11. ダッシュボード（Dashboard）

### `GET /api/v1/dashboard/overview`
KPIサマリー。**権限: `manager` 以上**

**Response 200**
```json
{
  "total_employees": 1248,
  "assigned": 1091,
  "free_immediate": 67,
  "free_planned": 45,
  "utilization_rate": 87.4,
  "pending_approvals": 45,
  "alerts": {
    "visa_expiry_30d": 8,
    "cert_expiry_30d": 12
  }
}
```

---

### `GET /api/v1/dashboard/utilization-trend`
稼働率推移（過去6ヶ月）。

**Query**: `?months=6`

---

### `GET /api/v1/dashboard/free-forecast`
フリー人材推移予測（今後3ヶ月）。

---

### `GET /api/v1/dashboard/skills-distribution`
スキル別フリー人材数。

---

## 12. アラート（Alerts）

### `GET /api/v1/alerts`
アラート一覧（種別・期限でフィルタ可能）。**権限: `manager` 以上**

**Query**: `?type=VISA_EXPIRY&days=30`

**Response 200**
```json
{
  "items": [
    {
      "type": "VISA_EXPIRY",
      "employee": { "id": "uuid", "name_ja": "グエン・バン・エックス" },
      "expires_at": "2026-03-07",
      "days_remaining": 7,
      "is_notified": true
    }
  ]
}
```

---

## 13. 通知（Notifications）

### `GET /api/v1/notifications`
自分宛の通知一覧。

**Query**: `?is_read=false&page=1&per_page=20`

### `PATCH /api/v1/notifications/{id}/read`
既読にする。

### `PATCH /api/v1/notifications/read-all`
全件既読にする。

---

## 14. マスタ管理（Admin）

### スキルカテゴリ
- `GET /api/v1/admin/skill-categories`
- `POST /api/v1/admin/skill-categories`
- `PUT /api/v1/admin/skill-categories/{id}`

### スキルマスタ
- `POST /api/v1/admin/skills`
- `PUT /api/v1/admin/skills/{id}`
- `DELETE /api/v1/admin/skills/{id}`（論理削除）

### ユーザー・権限管理
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users` — 社内アカウント発行
- `PATCH /api/v1/admin/employees/{id}/role` — ロール変更
- `DELETE /api/v1/admin/users/{id}` — アカウント無効化

---

## 15. エラーレスポンス（統一形式）

```json
{
  "error": {
    "code": "SKILL_ALREADY_EXISTS",
    "message": "このスキルはすでに登録されています",
    "details": {}
  }
}
```

| HTTPステータス | 用途 |
|---|---|
| 200 | 成功 |
| 201 | 作成成功 |
| 400 | バリデーションエラー |
| 401 | 未認証 |
| 403 | 権限不足 |
| 404 | リソース未存在 |
| 409 | 競合（重複登録等）|
| 422 | パラメータ型エラー（FastAPI自動）|
| 500 | サーバーエラー |

---

## 16. 認証・認可ミドルウェア

```python
# FastAPIの依存性注入パターン
@router.get("/employees")
async def list_employees(
    current_user: Employee = Depends(require_role(["manager", "department_head", "director", "admin"]))
):
    ...
```

- `require_role(roles)`: ロールチェック
- `require_own_or_role(employee_id, roles)`: 本人 or 指定ロール
- `require_team(employee_id)`: `manager`は自チームのみアクセス可
