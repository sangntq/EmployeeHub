# EmployeeHub

IT人材派遣会社（ベトナム・日本拠点）向けの社内人材管理プラットフォーム。
エンジニアのスキル・経歴・稼働状況・ビザを一元管理し、日本語顧客向け案件への人材マッチングを効率化する。

## 技術スタック

| レイヤー | 技術 |
|---|---|
| フロントエンド | React 18 + TypeScript + Vite + Ant Design |
| バックエンド | Python 3.12 + FastAPI |
| データベース | PostgreSQL 16 |
| ORM / マイグレーション | SQLAlchemy 2.0 (asyncpg) + Alembic |
| 認証 | JWT + Google OAuth 2.0 |
| 状態管理 | Zustand + TanStack Query |
| コンテナ | Docker + Docker Compose |

---

## 事前要件

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 24以降
- Docker Compose v2 (`docker compose` コマンドが使えること)

---

## セットアップ

### 1. 環境変数ファイルを作成

```bash
cp .env.example .env
```

開発環境ではデフォルト値のままで動作する。
`SECRET_KEY` は本番環境では必ず変更すること。

### 2. コンテナを起動

```bash
docker compose up --build
```

初回は依存パッケージのインストールとイメージビルドが行われるため数分かかる。

### 3. データベースマイグレーション実行

```bash
docker compose exec backend alembic upgrade head
```

管理者アカウントが自動作成される:
- メール: `admin@employeehub.local`
- パスワード: `Admin1234!`

### 4. アクセス

| URL | 説明 |
|---|---|
| http://localhost:3000 | フロントエンド（ログイン画面） |
| http://localhost:8000/docs | バックエンド API ドキュメント（Swagger UI） |
| http://localhost:8000/redoc | バックエンド API ドキュメント（ReDoc） |
| http://localhost:5432 | PostgreSQL（ユーザー: employeehub / パスワード: employeehub） |

---

## コンテナ管理

```bash
# バックグラウンド起動
docker compose up -d

# コンテナ停止
docker compose down

# DB データも含めて完全リセット
docker compose down -v

# ログ確認
docker compose logs -f backend
docker compose logs -f frontend
```

---

## ユニットテスト

### バックエンド（pytest）

SQLite インメモリ DB を使用するため PostgreSQL 不要でテスト実行できる。

```bash
# Docker コンテナ内で実行（推奨）
docker compose exec backend pytest

# 詳細出力
docker compose exec backend pytest -v

# 特定ファイルのみ
docker compose exec backend pytest tests/test_auth.py -v
docker compose exec backend pytest tests/test_employees.py -v

# ローカル（仮想環境あり）で実行する場合
cd backend
pip install -r requirements.txt
pytest
```

テスト構成:
```
backend/tests/
├── conftest.py          # フィクスチャ（SQLite インメモリ DB、テストクライアント、ユーザー/社員生成）
├── test_auth.py         # 認証 API テスト（ログイン・リフレッシュ・me・ログアウト）
└── test_employees.py    # 社員 API テスト（一覧・詳細・作成・更新、RBAC 検証）
```

### フロントエンド（Vitest）

```bash
# Docker コンテナ内で実行（推奨）
docker compose exec frontend npm test

# ウォッチモード（ファイル変更時に自動再実行）
docker compose exec frontend npm run test:watch

# ローカルで実行する場合
cd frontend
npm install
npm test
```

テスト構成:
```
frontend/src/
├── test/setup.ts                                   # グローバルセットアップ（jest-dom 拡張）
├── stores/__tests__/authStore.test.ts              # Zustand ストアのテスト
├── hooks/__tests__/useAuth.test.ts                 # useAuth フックのロール判定テスト
└── components/common/StatusBadge/__tests__/
    └── StatusBadge.test.tsx                        # StatusBadge コンポーネントテスト
```

---

## 開発ワークフロー

### バックエンドのコードを変更した場合

ボリュームマウントにより自動リロードが有効。変更は即座に反映される。

### 新しい DB マイグレーションを作成する

```bash
# マイグレーションファイルを自動生成
docker compose exec backend alembic revision --autogenerate -m "説明文"

# マイグレーション適用
docker compose exec backend alembic upgrade head

# ロールバック（1つ前に戻す）
docker compose exec backend alembic downgrade -1
```

### フロントエンドのパッケージを追加する

```bash
docker compose exec frontend npm install <パッケージ名>
```

---

## 環境変数一覧

| 変数名 | デフォルト値 | 説明 |
|---|---|---|
| `DB_USER` | `employeehub` | PostgreSQL ユーザー名 |
| `DB_PASSWORD` | `employeehub` | PostgreSQL パスワード |
| `DB_NAME` | `employeehub_db` | データベース名 |
| `SECRET_KEY` | `dev-secret-key-...` | JWT 署名キー（**本番では必ず変更**） |
| `ENVIRONMENT` | `development` | 環境名（`production` 時は Swagger UI 非表示） |
| `CORS_ORIGINS` | `http://localhost:3000` | フロントエンドのオリジン（カンマ区切りで複数指定可） |
| `GOOGLE_CLIENT_ID` | _(任意)_ | Google OAuth クライアント ID |
| `GOOGLE_CLIENT_SECRET` | _(任意)_ | Google OAuth クライアントシークレット |
| `S3_ENDPOINT_URL` | _(任意)_ | S3 互換ストレージ URL（未設定時はローカル保存） |
| `ANTHROPIC_API_KEY` | _(任意)_ | Claude API キー（AI 自然言語検索用） |

---

## API 認証

全エンドポイント（`/auth/*` を除く）は JWT Bearer トークンが必要。

```http
Authorization: Bearer <access_token>
```

トークンは `POST /api/v1/auth/login` で取得する。有効期限は 60 分。
リフレッシュトークン（有効期限 30 日）で `POST /api/v1/auth/refresh` から新しいアクセストークンを取得できる。

---

## フェーズ開発状況

| フェーズ | 内容 | 状態 |
|---|---|---|
| Phase 0 | Docker 環境、共通コンポーネント、i18n | ✅ 完了 |
| Phase 1 | 認証（JWT + Google OAuth）・社員 CRUD | ✅ 完了 |
| Phase 2 | スキル管理・資格管理・承認フロー | ✅ 完了 |
| Phase 3 | 稼働状況・アサイン管理 | ✅ 完了 |
| Phase 4 | キーワード検索・フィルタリング | ✅ 完了 |
| Phase 5 | AI 自然言語検索（Claude API） | ✅ 完了 |
| Phase 6 | ダッシュボード・アラートダッシュボード | ✅ 完了 |
| Phase 7 | スキルシート出力（Excel / PDF / ZIP） | ✅ 完了 |
| Phase 8 | 通知・アラート（APScheduler・メール） | ✅ 完了 |
| Phase 9 | デプロイ基盤（Docker prod・CI/CD・AWS） | ✅ 完了 |

---

## 本番ビルドのローカル検証

本番用 Docker イメージをローカルでビルドして動作確認するための手順。
実際の AWS ECS デプロイ前に使用する。

### 1. 環境変数ファイルを準備

```bash
cp .env.staging.example .env.prod
# .env.prod を編集（最低限 SECRET_KEY を変更する）
```

### 2. 本番イメージをビルド・起動

```bash
docker compose -f docker-compose.prod.yml up --build
```

| URL | 説明 |
|---|---|
| http://localhost:80 | フロントエンド（Nginx 静的配信） |
| http://localhost:80/api/v1/health | バックエンドヘルスチェック |

### 3. ⚠️ 重要: 開発環境の復元

本番ビルドは `employeehub-frontend` イメージを上書きするため、
**ビルド後に開発環境（localhost:3000）が起動しなくなる**。

```bash
# 開発環境を復元する（必ず実行）
docker compose up --build
```

このコマンドで Vite dev server イメージが再ビルドされ、`localhost:3000` が復活する。

---

## AWS デプロイ

### アーキテクチャ概要

```
インターネット
      ↓
 ALB (HTTPS / 443)
  ├── /api/*  → Backend ECS Service (uvicorn)
  └── /*      → Frontend ECS Service (nginx 静的配信)
                       ↓
                  RDS PostgreSQL
```

`VITE_API_BASE_URL=""`（空文字）でビルドされた React アプリは `/api/v1/...` 形式の相対パスで
API を呼び出す。ALB がパスベースルーティングでバックエンドに転送する。

### CI/CD パイプライン（GitHub Actions）

| ワークフロー | ファイル | トリガー |
|---|---|---|
| CI（テスト） | `.github/workflows/ci.yml` | 全 PR・push |
| Deploy Staging | `.github/workflows/deploy.yml` | `develop` ブランチへの push |
| Deploy Production | `.github/workflows/deploy.yml` | `main` ブランチへの push |

### 初回デプロイの手順

#### Step 1 — AWS リソースを手動作成

以下を AWS Console で作成しておく:

1. **ECR リポジトリ** × 2（バックエンド・フロントエンド）
2. **RDS PostgreSQL 16**（Multi-AZ 推奨）
3. **ECS クラスター**（Fargate）
4. **ECS タスク定義** × 2（backend / frontend）— 最初は仮のイメージで作成して OK
5. **ECS サービス** × 2（ALB と連携）
6. **ALB** + ターゲットグループ × 2 + リスナールール

#### Step 2 — GitHub Secrets / Variables を設定

GitHub リポジトリの Settings → Environments で `staging` と `production` を作成し、それぞれに設定する。

**Secrets（機密情報）:**

| Secret 名 | 説明 |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM ユーザーのアクセスキー |
| `AWS_SECRET_ACCESS_KEY` | IAM ユーザーのシークレットキー |

**Variables（環境ごと）:**

| Variable 名 | 例 |
|---|---|
| `AWS_REGION` | `ap-northeast-1` |
| `ECR_REGISTRY` | `123456789.dkr.ecr.ap-northeast-1.amazonaws.com` |
| `ECR_BACKEND_REPO` | `employeehub-backend` |
| `ECR_FRONTEND_REPO` | `employeehub-frontend` |
| `ECS_CLUSTER` | `employeehub-staging` |
| `ECS_BACKEND_SERVICE` | `employeehub-backend-service` |
| `ECS_FRONTEND_SERVICE` | `employeehub-frontend-service` |
| `ECS_BACKEND_TASK_DEF` | `employeehub-backend-task` |
| `ECS_FRONTEND_TASK_DEF` | `employeehub-frontend-task` |
| `BACKEND_CONTAINER_NAME` | `backend` |
| `FRONTEND_CONTAINER_NAME` | `frontend` |

#### Step 3 — 環境変数（ECS タスク定義）

ECS タスク定義の `environment` / `secrets`（SSM Parameter Store 推奨）に設定:

```
DATABASE_URL=postgresql+asyncpg://user:pass@rds-host:5432/dbname
SECRET_KEY=<本番用ランダム文字列 64 文字以上>
ENVIRONMENT=production
CORS_ORIGINS=https://app.employeehub.com
ANTHROPIC_API_KEY=<Claude API キー>
S3_BUCKET_NAME=employeehub-production
S3_ACCESS_KEY=<IAM キー>
S3_SECRET_KEY=<IAM シークレット>
SMTP_HOST=email-smtp.ap-northeast-1.amazonaws.com   # SES
SMTP_USER=<SES SMTP ユーザー>
SMTP_PASSWORD=<SES SMTP パスワード>
```

#### Step 4 — 最初の DB マイグレーション

ECS タスク定義の「Run Task」または踏み台経由で一度だけ実行:

```bash
alembic upgrade head
```

#### Step 5 — デプロイ実行

```bash
# ステージング
git push origin develop

# 本番
git push origin main   # または develop → main へ PR マージ
```

GitHub Actions が自動でビルド → ECR プッシュ → ECS デプロイを行う。

### IAM 権限（最小権限）

GitHub Actions 用の IAM ユーザーに必要なポリシー:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*" },
    { "Effect": "Allow", "Action": ["ecr:BatchCheckLayerAvailability", "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage"], "Resource": "arn:aws:ecr:*:*:repository/employeehub-*" },
    { "Effect": "Allow", "Action": ["ecs:DescribeTaskDefinition", "ecs:RegisterTaskDefinition",
      "ecs:UpdateService", "ecs:DescribeServices"], "Resource": "*" },
    { "Effect": "Allow", "Action": ["iam:PassRole"], "Resource": "arn:aws:iam::*:role/ecsTaskExecutionRole" }
  ]
}
```

---

## Appendix: AI 自然言語検索の仕組み

`/search` 画面の「AI Natural Language Search」タブで利用できる機能。
営業担当が顧客との会話テキストをそのまま貼り付けると、Claude API が構造化された検索条件に自動変換する。

### 全体フロー

```
ユーザーがテキスト入力
        ↓
POST /api/v1/search/ai-parse        ← backend/app/services/ai_parser.py
        ↓
Claude API（Haiku）へ送信
        ↓
JSON レスポンスを受信・検証
        ↓
AIParseResponse をフロントエンドに返却   ← 条件確認画面を表示
        ↓
ユーザーが「この条件で検索」をクリック
        ↓
POST /api/v1/search/filter           ← backend/app/services/search_service.py
        ↓
SQL クエリ生成 + マッチスコア算出
        ↓
結果カード表示
```

### ステップ 1 — プロンプト構築（`ai_parser.py`）

バックエンドが 3 要素からなる system prompt を動的に構築して Claude へ送る。

**① スキルマスタ（DB から取得した実データ）**

```json
[
  {"id": "abc-123", "name": "Java",        "name_ja": "Java"},
  {"id": "def-456", "name": "Spring Boot", "name_ja": "Spring Boot"},
  ...  // 最大 300 件
]
```

Claude はこのリストを参照して、テキスト中のスキル名を正確な ID に変換する。

**② 有効な enum 値**

```
office_locations : HANOI, HCMC, TOKYO, OSAKA, OTHER
work_styles      : ONSITE, REMOTE, HYBRID
japanese_levels  : NONE, N5, N4, N3, N2, N1, NATIVE
work_statuses    : ASSIGNED, FREE_IMMEDIATE, FREE_PLANNED, INTERNAL, LEAVE, LEAVING
```

**③ 出力 JSON スキーマ（strict 指定）**

```json
{
  "summary"         : "入力内容の一行サマリー",
  "skills"          : [{"skill_id": "<マスタの id>", "level_min": null, "required": true}],
  "japanese_level"  : null,
  "work_style"      : null,
  "office_locations": [],
  "work_statuses"   : [],
  "free_from_before": null,
  "unmatched_terms" : []
}
```

### ステップ 2 — Claude API 呼び出し

```python
client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
message = await client.messages.create(
    model="claude-haiku-4-5-20251001",  # 高速・低コスト
    max_tokens=1024,
    system=system_prompt,
    messages=[{"role": "user", "content": text}],
)
```

入力例:
> 来月からJavaとSpring Bootが得意なエンジニアが必要、N2以上、リモートOK

Claude が返す JSON の例:
```json
{
  "summary": "来月からJava/Spring Boot経験者、N2以上、リモート可能なエンジニア募集",
  "skills": [
    {"skill_id": "abc-123", "level_min": null, "required": true},
    {"skill_id": "def-456", "level_min": null, "required": true}
  ],
  "japanese_level": "N2",
  "work_style": "REMOTE",
  "office_locations": [],
  "work_statuses": [],
  "free_from_before": "2024-12-01",
  "unmatched_terms": []
}
```

### ステップ 3 — バリデーションとスキル名解決

Claude のレスポンスをそのまま信用せず、DB のスキルマスタで照合する。

```python
skill_map = {s.id: s for s in skills}  # DB から取得したマスタ

for item in raw_skills:
    sid = item.get("skill_id", "")
    if sid in skill_map:          # ← DB に存在する ID のみ受け入れる
        skill_matches.append(...)
    # 存在しない ID（hallucination）は無視
```

マスタに存在しない用語（例: 独自技術名）は `unmatched_terms` に格納され、フロントエンドで警告表示される。

### ステップ 4 — SQL クエリ生成（`search_service.py`）

ユーザーが条件を確認・承認した後、`SearchFilter` が `search_service.search_employees()` へ渡される。

**必須スキルフィルタ（スキルごとにサブクエリを生成）**

```sql
WHERE employee.id IN (
    SELECT employee_id FROM employee_skills
    WHERE skill_id = 'abc-123'
      AND status = 'APPROVED'
      AND approved_level >= 1
)
AND employee.id IN (
    -- 必須スキルの数だけサブクエリを追加
)
```

**日本語レベルフィルタ（N2 以上 → 範囲に展開）**

```python
# N2 → eligible = [N2, N1, NATIVE]
query.where(Employee.japanese_level.in_(["N2", "N1", "NATIVE"]))
```

**マッチスコア算出**

```
base_score = (必須スキルのマッチ数 / 必須スキル総数) × 80
bonus      = (推奨スキルのマッチ数 / 推奨スキル総数) × 20
match_score = min(100, base_score + bonus)
```

### エラーハンドリング

| 状況 | HTTP ステータス | 対応 |
|---|---|---|
| `ANTHROPIC_API_KEY` 未設定 | 503 | フロントエンドに「AI 検索は無効」メッセージ表示 |
| Anthropic API 障害 | 503 | エラーアラート表示 |
| Claude が無効な JSON を返した | 422 | エラーアラート表示 |
| Claude が存在しないスキル ID を返した | — | 該当スキルを無視（hallucination 耐性） |

### ログ・監査

すべての AI 検索は `search_logs` テーブルに記録される。

```
search_logs.is_ai_search = true   ← AI 検索と通常検索を区別
search_logs.raw_input             ← ユーザーが入力した元テキスト
search_logs.criteria              ← 抽出された検索条件（JSON）
```
