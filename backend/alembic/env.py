# C:\src\FirstProject\backend\alembic\env.py

import os
import sys
from pathlib import Path

# your_project_name/backend ディレクトリをPythonのパスに追加
# これにより、alembicが `app` パッケージをインポートできるようになる
sys.path.append(str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# FastAPIアプリケーションのSQLAlchemyモデルをインポートするのじゃ！
from app.models import Base # <---- ここ！

# この部分を、後で定義するBaseクラスのmetadataにするのじゃ！
target_metadata = Base.metadata # <---- ここも確認！

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# 環境変数からDBのホスト、ユーザー、パスワード、DB名を取得するのじゃ
# AlembicがDBに接続するためのURLを動的に設定する
# Alembicは通常、Dockerネットワーク内ではなく、ホストから直接DBに接続する
# そのため、ホストのlocalhostとポートを使うのじゃ
if os.getenv("TESTING"): # もしTESTING環境変数があれば、テスト用DBに接続
    DB_HOST = "localhost"
    DB_PORT = "5433"
    DB_NAME = os.getenv("POSTGRES_TEST_DB")
    DB_USER = os.getenv("POSTGRES_TEST_USER")
    DB_PASSWORD = os.getenv("POSTGRES_TEST_PASSWORD")
else: # それ以外の場合は、開発/本番用DBに接続
    DB_HOST = "localhost" # 開発環境のAlembicからはlocalhostでアクセス
    DB_PORT = "5432"
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# SQLAlchemy URLを構築
alembic_sqlalchemy_url = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # url = config.get_main_option("sqlalchemy.url") # この行は使わない
    context.configure(
        url=alembic_sqlalchemy_url, # ここをalembic_sqlalchemy_urlに修正する
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        # url=alembic_sqlalchemy_url, # この行は不要、engine_from_configが内部で処理
        poolclass=pool.NullPool,
    )

    # config.set_main_option("sqlalchemy.url", alembic_sqlalchemy_url) # これも不要

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # alembicが直接DBに接続できるように、環境変数からURLを設定
    # Alembicの実行はホストPCからゆえ、Dockerコンテナのdb/db_testサービスにlocalhostでアクセス
    # この部分はalembic.iniで設定することもできるが、env.pyで動的に設定するならこのように
    config.set_main_option("sqlalchemy.url", alembic_sqlalchemy_url) # <-- ここを追加！
    run_migrations_online()