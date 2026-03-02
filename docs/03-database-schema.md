# データベース設計書（PostgreSQL）

**プロジェクト名**: EmployeeHub
**作成日**: 2026年2月28日
**バージョン**: 1.0

---

## 1. ER図（概要）

```
departments ──┐
              ├──< employees >──< employee_skills >── skills >── skill_categories
roles ────────┘         │
                        ├──< employee_certifications >── certification_masters
                        ├──< employee_projects >──< projects
                        ├── work_statuses
                        ├──< assignments >── projects
                        ├── visa_info
                        │
users ──────────────────┘
                        ├──< notifications
                        ├──< search_logs
                        └──< approval_history
```

---

## 2. テーブル定義

### 2.1 `users` — 認証アカウント

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),               -- NULLの場合はGoogle認証のみ
    google_id       VARCHAR(255) UNIQUE,         -- Google OAuth sub
    is_active       BOOLEAN NOT NULL DEFAULT true,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_email    ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
```

---

### 2.2 `departments` — 部署・組織

```sql
CREATE TABLE departments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_ja     VARCHAR(100) NOT NULL,
    name_en     VARCHAR(100),
    name_vi     VARCHAR(100),
    parent_id   UUID REFERENCES departments(id) ON DELETE SET NULL,
    manager_id  UUID,                            -- FK → employees.id（循環参照回避のためDEFERRED）
    sort_order  INT NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

### 2.3 `employees` — 社員

```sql
CREATE TYPE employment_type AS ENUM ('FULLTIME', 'CONTRACT', 'FREELANCE');
CREATE TYPE work_style      AS ENUM ('ONSITE', 'REMOTE', 'HYBRID');
CREATE TYPE office_location AS ENUM ('HANOI', 'HCMC', 'TOKYO', 'OSAKA', 'OTHER');
CREATE TYPE system_role     AS ENUM ('member', 'manager', 'department_head', 'sales', 'director', 'admin');

CREATE TABLE employees (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID UNIQUE REFERENCES users(id) ON DELETE SET NULL,
    employee_number   VARCHAR(20) UNIQUE NOT NULL,
    name_ja           VARCHAR(100) NOT NULL,
    name_en           VARCHAR(100),
    name_vi           VARCHAR(100),
    department_id     UUID REFERENCES departments(id) ON DELETE SET NULL,
    system_role       system_role NOT NULL DEFAULT 'member',
    office_location   office_location NOT NULL,
    employment_type   employment_type NOT NULL DEFAULT 'FULLTIME',
    work_style        work_style NOT NULL DEFAULT 'ONSITE',
    joined_at         DATE NOT NULL,
    email             VARCHAR(255) NOT NULL,           -- 社内メール（usersと同じとは限らない）
    phone             VARCHAR(30),
    slack_id          VARCHAR(100),
    avatar_url        VARCHAR(500),
    is_active         BOOLEAN NOT NULL DEFAULT true,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_employees_department  ON employees(department_id);
CREATE INDEX idx_employees_role        ON employees(system_role);
CREATE INDEX idx_employees_location    ON employees(office_location);
CREATE INDEX idx_employees_active      ON employees(is_active);
```

---

### 2.4 `skill_categories` — スキルカテゴリ

```sql
CREATE TABLE skill_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_ja     VARCHAR(50) NOT NULL,
    name_en     VARCHAR(50) NOT NULL,
    sort_order  INT NOT NULL DEFAULT 0
);

-- 初期データ
INSERT INTO skill_categories (name_ja, name_en, sort_order) VALUES
    ('プログラミング言語', 'Programming Language', 1),
    ('フレームワーク',     'Framework',            2),
    ('データベース',       'Database',             3),
    ('クラウド',          'Cloud',                4),
    ('インフラ・ツール',   'Infrastructure/Tools', 5),
    ('ドメイン知識',       'Domain Knowledge',     6);
```

---

### 2.5 `skills` — スキルマスタ

```sql
CREATE TABLE skills (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES skill_categories(id),
    name        VARCHAR(100) NOT NULL UNIQUE,       -- 正式名（検索キー）
    name_ja     VARCHAR(100),
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_skills_category ON skills(category_id);
```

---

### 2.6 `employee_skills` — 個人スキル（承認フロー付き）

```sql
CREATE TYPE approval_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');

CREATE TABLE employee_skills (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id         UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    skill_id            UUID NOT NULL REFERENCES skills(id),
    self_level          SMALLINT NOT NULL CHECK (self_level BETWEEN 1 AND 5),
    approved_level      SMALLINT CHECK (approved_level BETWEEN 1 AND 5),
    experience_years    DECIMAL(4,1),
    last_used_at        DATE,
    status              approval_status NOT NULL DEFAULT 'PENDING',
    evidence_file_url   VARCHAR(500),              -- 証明書ファイル（S3等）
    self_comment        TEXT,
    approver_id         UUID REFERENCES employees(id),
    approver_comment    TEXT,
    approved_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (employee_id, skill_id)                 -- 1人1スキル1レコード
);

CREATE INDEX idx_emp_skills_employee ON employee_skills(employee_id);
CREATE INDEX idx_emp_skills_skill    ON employee_skills(skill_id);
CREATE INDEX idx_emp_skills_status   ON employee_skills(status);
```

---

### 2.7 `certification_masters` — 資格マスタ

```sql
CREATE TYPE cert_category AS ENUM ('LANGUAGE', 'CLOUD', 'PM', 'NETWORK', 'SECURITY', 'OTHER');

CREATE TABLE certification_masters (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    category    cert_category NOT NULL,
    issuer      VARCHAR(100),
    has_expiry  BOOLEAN NOT NULL DEFAULT true,
    is_active   BOOLEAN NOT NULL DEFAULT true
);
```

---

### 2.8 `employee_certifications` — 個人資格

```sql
CREATE TABLE employee_certifications (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id             UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    certification_master_id UUID REFERENCES certification_masters(id),
    custom_name             VARCHAR(200),          -- マスタにない資格は自由入力
    score                   VARCHAR(50),           -- JLPT N1, スコア等
    obtained_at             DATE NOT NULL,
    expires_at              DATE,                  -- NULLは無期限
    file_url                VARCHAR(500),
    status                  approval_status NOT NULL DEFAULT 'PENDING',
    approver_id             UUID REFERENCES employees(id),
    approver_comment        TEXT,
    approved_at             TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_emp_certs_employee   ON employee_certifications(employee_id);
CREATE INDEX idx_emp_certs_expires    ON employee_certifications(expires_at);
CREATE INDEX idx_emp_certs_status     ON employee_certifications(status);
```

---

### 2.9 `projects` — プロジェクトマスタ

```sql
CREATE TABLE projects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    client_name VARCHAR(200),
    industry    VARCHAR(100),
    started_at  DATE,
    ended_at    DATE,              -- NULLは継続中
    description TEXT,
    created_by  UUID REFERENCES employees(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

### 2.10 `employee_projects` — プロジェクト経歴

```sql
CREATE TYPE project_role AS ENUM ('PL', 'PM', 'SE', 'PG', 'QA', 'INFRA', 'DESIGNER', 'OTHER');

CREATE TABLE employee_projects (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id         UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id),
    role                project_role NOT NULL,
    started_at          DATE NOT NULL,
    ended_at            DATE,
    tech_stack          TEXT[],                    -- PostgreSQL配列 例: '{Java,Spring Boot,AWS}'
    team_size           SMALLINT,
    responsibilities    TEXT,
    achievements        TEXT,
    sort_order          INT NOT NULL DEFAULT 0,    -- スキルシートでの表示順
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_emp_projects_employee ON employee_projects(employee_id);
CREATE INDEX idx_emp_projects_project  ON employee_projects(project_id);
```

---

### 2.11 `work_statuses` — 稼働状況（1人1レコード）

```sql
CREATE TYPE work_status AS ENUM (
    'ASSIGNED',         -- アサイン中
    'FREE_IMMEDIATE',   -- フリー（即時）
    'FREE_PLANNED',     -- フリー（予定）
    'INTERNAL',         -- 社内業務
    'LEAVE',            -- 休職中
    'LEAVING'           -- 退職予定
);

CREATE TABLE work_statuses (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID UNIQUE NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    status      work_status NOT NULL DEFAULT 'FREE_IMMEDIATE',
    free_from   DATE,                              -- FREE_PLANNEDの場合の予定日
    note        TEXT,
    updated_by  UUID REFERENCES employees(id),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_work_statuses_status ON work_statuses(status);
CREATE INDEX idx_work_statuses_free_from ON work_statuses(free_from);
```

---

### 2.12 `assignments` — アサイン管理

```sql
CREATE TABLE assignments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id         UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    project_id          UUID NOT NULL REFERENCES projects(id),
    allocation_percent  SMALLINT NOT NULL DEFAULT 100
        CHECK (allocation_percent BETWEEN 1 AND 100),
    started_at          DATE NOT NULL,
    ends_at             DATE,
    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_by          UUID REFERENCES employees(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_assignments_employee ON assignments(employee_id);
CREATE INDEX idx_assignments_active   ON assignments(is_active, ends_at);
```

---

### 2.13 `visa_info` — ビザ情報（1人1レコード）

```sql
CREATE TABLE visa_info (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id           UUID UNIQUE NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    visa_type             VARCHAR(100),
    residence_card_number VARCHAR(20),
    expires_at            DATE,
    notes                 TEXT,
    updated_by            UUID REFERENCES employees(id),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_visa_expires ON visa_info(expires_at);
```

---

### 2.14 `notifications` — 通知

```sql
CREATE TYPE notification_type AS ENUM (
    'VISA_EXPIRY',
    'CERT_EXPIRY',
    'SKILL_APPROVED',
    'SKILL_REJECTED',
    'CERT_APPROVED',
    'CERT_REJECTED',
    'ASSIGNMENT_ENDING',
    'PROFILE_STALE',
    'APPROVAL_REQUESTED'
);

CREATE TABLE notifications (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id          UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    type                  notification_type NOT NULL,
    title                 VARCHAR(200) NOT NULL,
    body                  TEXT,
    is_read               BOOLEAN NOT NULL DEFAULT false,
    related_entity_type   VARCHAR(50),             -- 'employee_skill', 'employee_certification', etc.
    related_entity_id     UUID,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_recipient ON notifications(recipient_id, is_read);
CREATE INDEX idx_notifications_created   ON notifications(created_at DESC);
```

---

### 2.15 `search_logs` — 検索ログ

```sql
CREATE TABLE search_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    searcher_id     UUID REFERENCES employees(id) ON DELETE SET NULL,
    is_ai_search    BOOLEAN NOT NULL DEFAULT false,
    raw_input       TEXT,                          -- AI検索時の貼り付けテキスト
    criteria        JSONB,                         -- 検索条件（構造化）
    result_count    INT,
    saved_name      VARCHAR(100),                  -- 保存検索の名前
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_search_logs_searcher ON search_logs(searcher_id);
CREATE INDEX idx_search_logs_created  ON search_logs(created_at DESC);
```

---

### 2.16 `approval_history` — 承認履歴（監査ログ）

```sql
CREATE TYPE approval_action AS ENUM ('SUBMITTED', 'APPROVED', 'REJECTED', 'RESUBMITTED');

CREATE TABLE approval_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     VARCHAR(50) NOT NULL,          -- 'employee_skill' / 'employee_certification'
    entity_id       UUID NOT NULL,
    action          approval_action NOT NULL,
    actor_id        UUID REFERENCES employees(id) ON DELETE SET NULL,
    comment         TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_approval_history_entity ON approval_history(entity_type, entity_id);
```

---

## 3. 主要インデックス設計

### 人材検索の高速化

```sql
-- フリー人材の高速抽出
CREATE INDEX idx_work_status_free
    ON work_statuses(status)
    WHERE status IN ('FREE_IMMEDIATE', 'FREE_PLANNED');

-- スキル検索（承認済みのみ対象）
CREATE INDEX idx_emp_skills_approved
    ON employee_skills(skill_id, approved_level)
    WHERE status = 'APPROVED';

-- tech_stackの全文検索（プロジェクト経歴）
CREATE INDEX idx_emp_projects_tech_stack
    ON employee_projects USING GIN(tech_stack);

-- JSONB検索（保存された検索条件）
CREATE INDEX idx_search_logs_criteria
    ON search_logs USING GIN(criteria);
```

---

## 4. マイグレーション管理

- **ツール**: Alembic（FastAPI標準のマイグレーションツール）
- **命名規則**: `YYYYMMDD_HHMMSS_description.py`
- **方針**: `upgrade()` / `downgrade()` 必ず両方実装

---

## 5. 初期データ（シード）

| テーブル | 内容 |
|---|---|
| `skill_categories` | 6カテゴリ（言語/FW/DB/クラウド/インフラ/ドメイン）|
| `skills` | Java, Python, React, PostgreSQL, AWS等 主要50スキル |
| `certification_masters` | JLPT N1〜N5, AWS SAA/SAP, PMP, IPA基本/応用 等 |
| `departments` | サンプル部署構成 |
| `users` + `employees` | 管理者アカウント1件 |
