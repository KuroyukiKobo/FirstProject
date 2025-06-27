# backend/app/auth.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .schemas import TokenData

# ---------------------------------------------
# ここに秘密情報を設定するのじゃ！
# 本番では.envファイルから読み込むべし！
SECRET_KEY = "Uc207Pr4f57t9" # <-- ここを適当な文字列に変更するのじゃ！
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # トークンの有効期限 (分)
# ---------------------------------------------

# パスワードのハッシュ化と照合のためのコンテキストじゃ
# `bcrypt`というアルゴリズムを使ってパスワードを安全にハッシュ化するのじゃ
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# パスワードをハッシュ化する関数
def get_password_hash(password: str) -> str:
    # 先生のパスワードを安全なハッシュ値に変換する
    return pwd_context.hash(password)

# ハッシュ化されたパスワードが、入力されたパスワードと一致するか照合する関数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWTトークンを作成する関数
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # ここでトークンをエンコードするのじゃ
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWTトークンをデコードして検証する関数
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # トークンのデータを返す
        return TokenData(username=username)
    except JWTError:
        # トークンが無効な場合は例外を発生させる
        raise credentials_exception

# ---------------------------------------------
# 注意: SECRET_KEYは本番では非常に複雑なものを使うべし！
# ---------------------------------------------