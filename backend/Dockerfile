# backend/Dockerfile

# Pythonの公式イメージをベースにするのじゃ
# 今回はPython 3.13を使っているようゆえ、それに合わせる
FROM python:3.13-slim-bookworm

# 作業ディレクトリを設定するのじゃ
# コンテナ内でアプリケーションのファイルが配置される場所じゃな
WORKDIR /app

# ホストの requirements.txt をコンテナの /app にコピーするのじゃ
# Pythonの依存関係をインストールするために必要じゃ
# COPYの順番は、変更頻度の低いものから高いものへがベストプラクティスじゃ
# これにより、requirements.txtが変更されない限り、pip installの層がキャッシュされる
COPY requirements.txt .

# 依存関係をインストールするのじゃ
# --no-cache-dir: キャッシュディレクトリを使用しない（イメージサイズを小さくするため）
# --upgrade pip: pip自体を最新にアップグレードする
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションのコード全てをコンテナの /app にコピーするのじゃ
# .dockerignoreに記載されたファイルは除外される
COPY . .

# ポート 8000 を公開するのじゃ (FastAPIがデフォルトで使うポート)
# これはドキュメンテーション用じゃ。実際にポートをマッピングするのは docker-compose.yml
EXPOSE 8000

# コンテナが起動したときに実行されるコマンドじゃ
# uvicorn app.main:app は、backend/app/main.py の app インスタンスを起動する
# --host 0.0.0.0 は、コンテナ外からのアクセスを許可するために必要じゃ
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]