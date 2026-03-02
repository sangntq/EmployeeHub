# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## プロジェクト概要

**EmployeeHub** — IT人材派遣会社（ベトナム・日本拠点）の社内人材管理プラットフォーム。
数千名のエンジニアのスキル・経歴・稼働状況・ビザを一元管理し、日本語顧客向け案件への人材マッチングを効率化する。

---

## ドキュメント

実装前に必ず参照すること。

| ファイル | 内容 |
|---|---|
| [`docs/01-requirements.md`](docs/01-requirements.md) | 機能・非機能要件、ロール定義、承認フロー |
| [`docs/02-ui-wireframes.md`](docs/02-ui-wireframes.md) | 全画面のASCIIワイヤーフレーム |
| [`docs/03-database-schema.md`](docs/03-database-schema.md) | PostgreSQL DDL、ER図、インデックス設計 |
| [`docs/04-api-design.md`](docs/04-api-design.md) | FastAPI全エンドポイント、リクエスト/レスポンス仕様 |
| [`docs/05-phases.md`](docs/05-phases.md) | 開発フェーズ計画、タスクリスト、ライブラリ候補 |

---

## 技術スタック

| レイヤー | 技術 |
|---|---|
| フロントエンド | React + TypeScript + Vite |
| バックエンド | Python + FastAPI |
| データベース | PostgreSQL（自社管理）|
| ORM / マイグレーション | SQLAlchemy + Alembic |
| 認証 | Google OAuth 2.0 + JWT（`python-jose`, `authlib`）|
| 状態管理 | Zustand + TanStack Query |
| UIライブラリ | Ant Design または shadcn/ui |
| ファイルストレージ | S3互換（MinIO等）|
| AI検索 | Claude API（`anthropic` SDK）|
| コンテナ | Docker + Docker Compose |

---

## ロール・権限モデル

6段階のロール。階層的な承認権限を持つ。

```
member < manager < department_head < director < admin
sales（横断: 検索・提案権限あり、承認権限なし）
```

| ロール | 主な権限 |
|---|---|
| `member` | 自プロフィール編集、スキル/資格申請 |
| `manager` | チームメンバーのスキル承認、稼働状況変更 |
| `department_head` | 部門全体の閲覧・承認 |
| `sales` | 人材検索、スキルシート出力（承認権限なし）|
| `director` | 全社ダッシュボード閲覧、給与情報閲覧 |
| `admin` | 全権限 + マスタ管理 + ユーザー管理 |

---

## 承認フロー

スキル・資格はすべて `PENDING → APPROVED / REJECTED` の2ステップ。

```
member: 自己評価 + 証明書アップロード（任意）→ PENDING
manager / department_head: 承認 → APPROVED / 差し戻し → REJECTED
```

`approval_history` テーブルに全アクションを記録（監査ログ）。

---

## 主要なデータモデル（概要）

```
users           認証アカウント（Google ID または password_hash）
employees       社員プロフィール（user_idで紐付け）
departments     部署・組織階層
skills          スキルマスタ（カテゴリ別）
employee_skills スキル申請・承認レコード（approval_status付き）
employee_certifications 資格申請・承認レコード
employee_projects プロジェクト経歴（tech_stack: TEXT[]）
work_statuses   稼働状況（1人1レコード）
assignments     アサイン管理（部分アサイン: allocation_percent）
visa_info       ビザ情報（1人1レコード）
notifications   アプリ内通知
search_logs     検索ログ（is_ai_search フラグ付き）
```

---

## AIナチュラルランゲージ検索

顧客との会話テキストをLLMで解析し、検索条件を自動抽出する機能。

- バックエンド `services/ai_parser.py` から `anthropic` SDK を呼び出す
- スキルマスタをプロンプトのコンテキストとして渡す
- 返却値は Pydantic で構造化 JSON としてバリデーション
- フロントエンドはユーザーに確認・修正させてから検索実行（誤抽出対策）
- `search_logs.is_ai_search = true` で追跡可能

---

## スキルシート出力

- 日本IT業界標準フォーマット（Excel: `openpyxl`、PDF: `WeasyPrint`）
- 複数候補者を1ファイル（シート別）またはZIP出力
- `POST /api/v1/skillsheet/export` → 一時ダウンロードURL（1時間有効）

---

## 開発規約

### 言語
- **会話（ユーザーとの）**: ベトナム語（tiếng Việt）
- **コードコメント・ドキュメント・ファイル内テキスト**: 日本語

### ディレクトリ構成（予定）
```
EmployeeHub/
├── frontend/          # React + TypeScript + Vite
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/       # axios クライアント
│   │   └── stores/    # Zustand
├── backend/           # FastAPI
│   ├── app/
│   │   ├── routers/
│   │   ├── models/    # SQLAlchemy
│   │   ├── schemas/   # Pydantic
│   │   ├── services/
│   │   └── core/      # 設定・認証・DB接続
│   ├── alembic/
│   └── tests/
└── docs/
```

### APIルール
- ベースURL: `/api/v1/`
- 認証: `Authorization: Bearer <JWT>`
- エラーレスポンス: `{ "error": { "code": "...", "message": "..." } }`
- ページネーション: `?page=1&per_page=20`

### 開発フェーズ順序
Phase 0（セットアップ）→ 1（認証・社員）→ 2（スキル・資格）→ 3（稼働状況）→ 4（検索）→ 5（AI検索）→ 6（ダッシュボード）→ 7（スキルシート）→ 8（通知）→ 9（リリース）

---

## コード実装後の必須手順（テスト義務）

**新しいエンドポイント・サービス・コンポーネントを実装したら、必ず以下を実行すること。**

### 1. バックエンド

新しいルーター・サービスを追加したら `backend/tests/` に対応するテストファイルを作成・更新し、すぐに実行する。

```bash
docker compose exec backend pytest -v
```

テストの書き方ルール:
- `tests/conftest.py` のフィクスチャ（`client`, `admin_employee`, `member_employee`, `auth_headers`）を再利用する
- 正常系・異常系・RBAC（権限）の3パターンを必ずカバーする
- テストDB は SQLite インメモリ（PostgreSQL 不要）
- **`EmailStr` は `.local` ドメインを拒否する → スキーマの email フィールドは `str` を使う**
- **サービスが `db.commit()` を呼ぶため `db.rollback()` では分離不可 → `conftest.py` の `clean_db` autouse fixture が各テスト後に DELETE ALL する**

### 2. フロントエンド

新しいストア・フック・コンポーネントを追加したら `__tests__/` に対応するテストファイルを作成・更新し、すぐに実行する。

```bash
docker compose exec frontend npm test
```

テストの書き方ルール:
- Zustand ストアのテスト: `renderHook` + `act` でストア操作を包む
- コンポーネントのテスト: `I18nextProvider` で i18n をラップしてレンダリングする
- `beforeEach` で `useAuthStore.setState({ user: null, ... })` してストア状態をリセットする

### 3. 実行確認なしに完了とみなさない

実装完了を宣言する前に、必ず `pytest` または `npm test` を実行してすべて PASSED を確認すること。
