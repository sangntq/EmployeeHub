import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# モデルの Base をインポートして autogenerate を有効にする
from app.core.database import Base  # noqa: F401
import app.models  # noqa: F401 – 全モデルをロードして Base.metadata に登録

config = context.config

# alembic.ini のログ設定を反映
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# 環境変数から同期用 DATABASE_URL を取得（alembic は同期ドライバを使用）
def get_url() -> str:
    return os.environ.get(
        "DATABASE_URL_SYNC",
        config.get_main_option("sqlalchemy.url", ""),
    )


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
