# C:\src\FirstProject\backend\app\database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# SQLAlchemy 2.0 以降の推奨されるBaseクラスの定義じゃ
class Base(DeclarativeBase):
    pass

# 環境変数からDBのホスト、ユーザー、パスワード、DB名を取得するのじゃ
# TESTING環境変数でテストDBと本番/開発DBを切り替える
if os.getenv("TESTING"):
    DB_HOST = "localhost" # テスト時はホストPCからアクセスするゆえ、localhost
    DB_PORT = "5433"      # テストDBのポート
    DB_NAME = os.getenv("POSTGRES_TEST_DB")
    DB_USER = os.getenv("POSTGRES_TEST_USER")
    DB_PASSWORD = os.getenv("POSTGRES_TEST_PASSWORD")
else:
    DB_HOST = "db"        # 開発/本番時はDockerネットワーク内のサービス名
    DB_PORT = "5432"      # 開発/本番DBのポート
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# DBエンジンを作成するのじゃ
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# データベースセッションクラスを作成するのじゃ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベースセッションを取得するための依存性注入関数じゃ
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()