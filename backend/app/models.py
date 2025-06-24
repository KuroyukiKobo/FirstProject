# C:\src\FirstProject\backend\app\models.py

from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base # database.py で定義したBaseをインポートするのじゃ

# ユーザーテーブルのモデル定義
class User(Base):
    __tablename__ = "users" # データベース内のテーブル名

    id = Column(Integer, primary_key=True, index=True) # 主キーでインデックス付き
    username = Column(String, unique=True, index=True) # ユニークでインデックス付き
    email = Column(String, unique=True, index=True, nullable=True) # Nullを許容
    hashed_password = Column(String) # パスワードのハッシュ

# アイテムテーブルのモデル定義 (例)
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True) # Nullを許容
    price = Column(Float)
    is_offer = Column(Boolean, default=False) # デフォルト値を設定