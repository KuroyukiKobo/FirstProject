# frontend/Dockerfile

# Node.js の公式イメージをベースにするのじゃ
# ReactはNode.jsでビルドされるゆえ必要じゃ。最新のLTSバージョンが推奨される
FROM node:lts-alpine

# 作業ディレクトリを設定する
WORKDIR /app

# package.json と package-lock.json をコンテナにコピーする
# 依存関係をインストールするために必要。キャッシュを活用できるよう、先にコピーする
COPY package*.json ./

# Node.jsの依存関係をインストールする
# --legacy-peer-deps: 一部の警告を回避するため（必要であれば）
RUN npm install --legacy-peer-deps

# フロントエンドのソースコード全てをコンテナにコピーする
COPY . .

# Reactアプリケーションをビルドするのじゃ
# 開発用ではなく、本番環境向けの静的ファイル生成じゃ
RUN npm run build

# Nginxなど、軽量なWebサーバーをベースイメージとして使うのじゃ
# 実際には、開発時はVite開発サーバー、本番時はこのNginxで静的ファイルを提供する
FROM nginx:stable-alpine

# Nginxの設定ファイルをコピーするのじゃ
# プロジェクトのルートに nginx.conf を作成する必要がある
# ここでは仮のパスとして nginx/default.conf とするが、実態に合わせて変更する
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# 前のステージでビルドしたReactの静的ファイルをNginxのWebルートにコピーするのじゃ
COPY --from=0 /app/dist /usr/share/nginx/html

# ポート 80 を公開するのじゃ (Nginxのデフォルトポート)
EXPOSE 80

# Nginxを起動するのじゃ
CMD ["nginx", "-g", "daemon off;"]