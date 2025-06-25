# C:\src\FirstProject\backend\app\main.py

import requests
import os

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)  # 認証のために必要じゃ
from fastapi.middleware.cors import CORSMiddleware  # CORS対応のために必要じゃ
from pydantic import BaseModel
from contextlib import asynccontextmanager  # これを追加するのじゃ
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from . import models, schemas, crud  # 新しく作ったファイルからインポート
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)  # 認証関連の関数をインポートするのじゃ
from .database import engine, Base, get_db  # database.pyからインポートする

# .envファイルを読み込むのじゃ
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)  # OAuth2のトークンURLを設定するのじゃ


# アプリケーションのライフサイクルイベントを定義するのじゃ！
@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時の処理
    # データベースのテーブルを作成するのじゃ
    # これは開発用じゃ。本番ではalembicでマイグレーションを行う
    Base.metadata.create_all(bind=engine)
    print("データベーステーブルが作成されたのじゃ！")  # 確認用のメッセージ
    yield  # アプリケーションが動作する間
    # アプリケーション終了時の処理があればここに記述する


# FastAPIアプリケーションのインスタンスを作成するのじゃ
app = FastAPI(
    title="キサキの天気API",
    description="FastAPIとReactの連携テストじゃ",
    version="0.1.0",
    lifespan=lifespan,  # <-- ここにlifespanを設定するのじゃ！
)

# CORS (Cross-Origin Resource Sharing) の設定じゃ
# これは、異なるオリジン（ドメイン、ポートなど）からAPIへのアクセスを許可するための設定じゃ
# React開発サーバーがFastAPIとは異なるポートで動くため、必須となるのじゃ
origins = [
    "*",  # 全てのオリジンを許可するのじゃ (開発中は便利じゃが、本番では注意が必要じゃ)
    "http://localhost:5173",  # Vite (React) のデフォルト開発サーバーのURLじゃ
    "http://127.0.0.1:5173",  # 念のためこちらも追加
    "http://localhost",  # Nginx経由のアクセス元として追加 (ポート80)
    "http://127.0.0.1",  # 念のため
    # 先生がReactアプリをデプロイする際のURLも追加するのじゃ
    # "https://your-frontend-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 全てのHTTPメソッドを許可する
    allow_headers=["*"],  # 全てのヘッダーを許可する
)


# Pydanticモデルを定義するのじゃ (外部APIのレスポンスや、フロントエンドに返すデータの構造)
class WeatherData(BaseModel):
    city_name: str
    temperature: float
    description: str
    icon_url: str


# ルートパスへのGETリクエストに対する処理
@app.get("/")
async def read_root():
    return {"message": "ハロー、先生！FastAPIバックエンドが起動しておるぞ！"}


@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # ユーザー名が既に存在するか確認するのじゃ
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400, detail="そのユーザー名は既に使用されておる！"
        )

    # 新しいユーザーを作成するのじゃ
    return crud.create_user(
        db=db, username=user.username, email=user.email, password=user.password
    )


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user:
        raise HTTPException(
            status_code=400, detail="ユーザー名またはパスワードが間違っておる！"
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="ユーザー名またはパスワードが間違っておる！"
        )

    # トークンを作成するのじゃ
    access_token_expires = timedelta(
        minutes=30
    )  # トークンの有効期限を30分に設定するのじゃ
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 天気情報を取得するAPIエンドポイント
@app.get("/weather/{city_name}", response_model=WeatherData)
async def get_weather(city_name: str):
    # .envからAPIキーを読み込むのじゃ
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        # APIキーが設定されていない場合はエラーを返すのじゃ
        raise HTTPException(
            status_code=500,
            detail="APIキーが設定されておらぬ！バックエンドの.envファイルを確認するのじゃ。",
        )

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",  # 摂氏で取得するのじゃ
        "lang": "ja",  # 日本語で天候情報を取得するのじゃ
    }

    try:
        # requestsライブラリを使ってOpenWeatherMap APIにリクエストを送信するのじゃ
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # HTTPステータスコードが4xx/5xxの場合に例外を発生させる

        data = response.json()

        # OpenWeatherMap APIが都市を見つけられなかった場合もエラーを返すのじゃ
        if data.get("cod") == "404":
            raise HTTPException(
                status_code=404,
                detail=f"指定された都市 '{city_name}' の天候は見つからぬ！",
            )

        # 必要な情報を抽出して、定義したPydanticモデルの形式で返すのじゃ
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        icon_code = data["weather"][0]["icon"]
        icon_url = (
            f"http://openweathermap.org/img/wn/{icon_code}@2x.png"  # 天気アイコンのURL
        )

        return WeatherData(
            city_name=city_name,
            temperature=temperature,
            description=description,
            icon_url=icon_url,
        )
    except requests.exceptions.RequestException as e:
        # requests関連のネットワークエラーなどを捕捉するのじゃ
        raise HTTPException(
            status_code=500, detail=f"外部APIへのリクエストに失敗したのじゃ: {e}"
        )
    except Exception as e:
        # その他の予期せぬエラーを捕捉するのじゃ
        raise HTTPException(
            status_code=500,
            detail=f"天候情報の取得中に予期せぬエラーが発生したのじゃ: {e}",
        )


# ユーザー関連API
@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400, detail="そのユーザー名は既に登録されておる！"
        )
    return crud.create_user(
        db=db, username=user.username, email=user.email, password=user.password
    )


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{username}", response_model=schemas.User)
def read_user_by_username(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つからぬ！")
    return db_user


@app.get("/users/me/", response_model=schemas.User)
def read_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # トークンからユーザー名を取得するのじゃ
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効じゃ！",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = crud.verify_access_token(token, credentials_exception)

    # ユーザー名からユーザー情報を取得するのじゃ
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# アイテム関連API (例)
@app.post("/items/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
def create_new_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items
