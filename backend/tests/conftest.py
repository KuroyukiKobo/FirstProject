# C:\src\FirstProject\backend\tests\conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path 

# .envファイルをテスト時にも読み込むのじゃ (プロジェクトルートの.env)
dotenv_path = Path(os.path.abspath(__file__)).parents[2] / ".env"
load_dotenv(dotenv_path=dotenv_path)# <--- ここも重要！ backend/tests から見て2階層上じゃ

# テスト用データベースURLを構築
TEST_DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_TEST_USER')}:{os.getenv('POSTGRES_TEST_PASSWORD')}@"
    f"localhost:5433/{os.getenv('POSTGRES_TEST_DB')}" # localhostと5433ポートじゃぞ
)

# テスト用DBエンジンとセッションを作成
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# テスト実行前にデータベースをクリアし、テーブルを作成するフィクスチャ
@pytest.fixture(scope="session")
def setup_database():
    from app.database import Base # FastAPIアプリのBaseをインポート
    # データベースのテーブルを全て削除し、再作成する
    # 注意: これはテスト用DBのみで行うこと！
    Base.metadata.drop_all(bind=test_engine) # 既存テーブルを削除
    Base.metadata.create_all(bind=test_engine) # テーブルを再作成
    yield # テストが実行される
    # テスト終了後に再度クリーンアップしたい場合はここに記述

# 各テスト関数にデータベースセッションを提供するフィクスチャ
@pytest.fixture(scope="function")
def db_session(setup_database):
    # テスト中はトランザクションを開始し、テスト終了後にロールバックすることでDBをクリーンに保つ
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session # テスト関数にセッションを渡す

    session.close()
    transaction.rollback() # テスト終了後に変更をロールバック

# FastAPIの依存性注入で、テスト用DBセッションを使うように上書きするフィクスチャ
@pytest.fixture(scope="function")
def client_with_db(db_session):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import get_db

    # get_db依存性をテスト用セッションで上書きする
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear() # 上書きをクリア