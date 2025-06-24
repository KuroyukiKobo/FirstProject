# C:\src\FirstProject\backend\app\schemas.py

from pydantic import BaseModel, ConfigDict # ConfigDictをインポートするのじゃ
from typing import List, Optional

# ユーザー作成時のリクエストボディ用スキーマ
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# ユーザー情報表示時のレスポンス用スキーマ
class User(BaseModel):
    id: int
    username: str
    email: str | None = None # オプションにできる

    model_config = ConfigDict(from_attributes=True) # これを追加するのじゃ！

# アイテム作成時のリクエストボディ用スキーマ
class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    is_offer: bool = False

# アイテム情報表示時のレスポンス用スキーマ
class Item(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    is_offer: bool = False

    model_config = ConfigDict(from_attributes=True) # これを追加するのじゃ！