# C:\src\FirstProject\backend\app\crud.py

from sqlalchemy.orm import Session
from . import models # models.py で定義したDBモデルをインポート
from . import schemas # スキーマ（Pydanticモデル）をインポート

# ユーザーを作成する関数
def create_user(db: Session, username: str, email: str, password: str):
    # 実際にはパスワードをハッシュ化するのじゃ！
    fake_hashed_password = password + "notreallyhashed"
    db_user = models.User(username=username, email=email, hashed_password=fake_hashed_password)
    db.add(db_user) # セッションに追加
    db.commit() # データベースにコミット
    db.refresh(db_user) # データベースから最新の情報を取得（IDなど）
    return db_user

# ユーザーを読み取る関数
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# アイテムを作成する関数 (例)
def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump()) # Pydanticモデルから辞書に変換して展開
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item