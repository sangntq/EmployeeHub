FROM node:20-alpine

WORKDIR /app

# 依存関係を先にインストール（キャッシュ活用）
COPY package.json package-lock.json* ./
RUN npm install

# アプリケーションコードをコピー
COPY . .

EXPOSE 3000

# 開発環境: Viteホットリロード有効
CMD ["npm", "run", "dev"]
