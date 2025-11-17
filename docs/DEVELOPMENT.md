# CourseAI 開發指南

## 📋 目錄

- [環境設置](#環境設置)
- [後端開發](#後端開發)
- [前端開發](#前端開發)
- [測試指南](#測試指南)
- [部署流程](#部署流程)

---

## 環境設置

### 必要軟體

1. **Python 3.9+**
   ```bash
   python --version  # 檢查版本
   ```

2. **Node.js 16+**
   ```bash
   node --version    # 檢查版本
   npm --version
   ```

3. **PostgreSQL 13+**
   ```bash
   psql --version    # 檢查版本
   ```

4. **Redis 6+**
   ```bash
   redis-server --version  # 檢查版本
   ```

### 資料庫設置

#### PostgreSQL

```bash
# 建立資料庫
createdb courseai

# 建立使用者
psql -d courseai
CREATE USER courseai WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE courseai TO courseai;
```

#### Redis

```bash
# 啟動 Redis 服務
redis-server

# 測試連線
redis-cli ping  # 應回應 PONG
```

---

## 後端開發

### 1. 安裝依賴

```bash
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 環境變數設置

複製並編輯環境變數檔案：

```bash
cp .env.example .env
nano .env  # 或使用其他編輯器
```

必須設置的變數：
- `DATABASE_URL`: PostgreSQL 連線字串
- `REDIS_URL`: Redis 連線字串
- `SECRET_KEY`: JWT 加密金鑰（請使用隨機字串）
- `OPENAI_API_KEY`: OpenAI API 金鑰（如果使用 GPT）

### 3. 資料庫遷移

```bash
# 初始化 Alembic（僅第一次）
alembic init alembic

# 建立遷移檔案
alembic revision --autogenerate -m "Initial migration"

# 執行遷移
alembic upgrade head
```

### 4. 啟動開發伺服器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

訪問 API 文件：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. 後端專案結構

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   ├── courses.py    # 課程相關 API
│   │   ├── quizzes.py    # 題目相關 API
│   │   ├── transcripts.py # WebSocket 轉錄
│   │   └── teacher_hints.py # 老師提示 API
│   ├── core/             # 核心配置
│   │   ├── config.py     # 設定管理
│   │   └── database.py   # 資料庫連線
│   ├── models/           # 資料庫模型
│   ├── schemas/          # Pydantic 模型
│   ├── services/         # 業務邏輯層
│   └── main.py           # FastAPI 主程式
├── tests/                # 測試檔案
└── requirements.txt      # Python 依賴
```

---

## 前端開發

### 1. 安裝依賴

```bash
cd extension

# 安裝 npm 套件
npm install
```

### 2. 開發模式構建

```bash
# 開發模式（自動監聽變更）
npm run dev

# 生產構建
npm run build
```

### 3. 安裝 Chrome 外掛

1. 開啟 Chrome 瀏覽器
2. 進入 `chrome://extensions/`
3. 開啟右上角「開發者模式」
4. 點擊「載入未封裝項目」
5. 選擇 `extension/dist` 目錄
6. 外掛已安裝完成！

### 4. 前端專案結構

```
extension/
├── src/
│   ├── content/          # Content Scripts
│   │   ├── index.tsx     # 主入口
│   │   ├── Sidebar.tsx   # 側邊欄元件
│   │   └── styles.css    # 樣式
│   ├── background/       # Background Service Worker
│   │   └── index.ts      # 背景腳本
│   ├── popup/            # Popup UI
│   │   ├── index.tsx     # Popup 入口
│   │   ├── App.tsx       # Popup 主元件
│   │   └── popup.css     # Popup 樣式
│   └── shared/           # 共用模組
│       ├── api.ts        # API 客戶端
│       ├── types.ts      # TypeScript 型別
│       └── utils.ts      # 工具函式
├── public/               # 靜態資源
│   ├── popup.html
│   └── icons/
├── manifest.json         # 外掛配置
├── package.json
├── tsconfig.json
└── webpack.config.js
```

---

## 測試指南

### 後端測試

```bash
cd backend

# 執行所有測試
pytest tests/ -v

# 執行特定測試檔案
pytest tests/test_courses.py -v

# 測試覆蓋率
pytest tests/ --cov=app --cov-report=html
```

### 前端測試

```bash
cd extension

# 執行測試
npm test

# TypeScript 類型檢查
npm run type-check

# ESLint 檢查
npm run lint
```

### 手動測試流程

1. **啟動後端服務**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **構建並載入外掛**
   ```bash
   cd extension
   npm run dev
   ```

3. **在 Google Meet 中測試**
   - 建立或加入 Google Meet 會議
   - 確認右側出現 CourseAI 側邊欄
   - 測試各項功能：
     - ✅ 上傳講義
     - ✅ 開始/停止錄音
     - ✅ 生成課程重點
     - ✅ 生成試題

---

## 部署流程

### 後端部署

#### 使用 Docker

1. **建立 Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **構建映像**
   ```bash
   docker build -t courseai-backend .
   ```

3. **執行容器**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e DATABASE_URL="..." \
     -e REDIS_URL="..." \
     --name courseai-backend \
     courseai-backend
   ```

#### 使用 Heroku

```bash
# 登入 Heroku
heroku login

# 建立應用
heroku create courseai-api

# 設置環境變數
heroku config:set DATABASE_URL="..."
heroku config:set REDIS_URL="..."

# 部署
git push heroku main
```

### 前端部署（Chrome Web Store）

1. **建立生產構建**
   ```bash
   cd extension
   npm run build
   ```

2. **打包外掛**
   ```bash
   cd dist
   zip -r courseai-extension.zip *
   ```

3. **上傳到 Chrome Web Store**
   - 訪問 [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   - 點擊「新增項目」
   - 上傳 `courseai-extension.zip`
   - 填寫外掛資訊
   - 提交審核

---

## 常見問題

### Q: 資料庫連線失敗？
A: 檢查 `.env` 中的 `DATABASE_URL` 是否正確，確認 PostgreSQL 服務已啟動。

### Q: WebSocket 連線失敗？
A: 確認後端服務正在運行，檢查防火牆設定。

### Q: 外掛無法載入？
A: 檢查 `manifest.json` 格式是否正確，確認已開啟開發者模式。

### Q: CORS 錯誤？
A: 檢查後端 `config.py` 中的 `CORS_ORIGINS` 設定。

---

## 開發建議

### 程式碼風格

**Python**
```bash
# 使用 Black 格式化
black app/

# 使用 Flake8 檢查
flake8 app/
```

**TypeScript**
```bash
# 使用 ESLint
npm run lint

# 自動修復
npm run lint -- --fix
```

### Git 工作流程

```bash
# 建立功能分支
git checkout -b feature/new-feature

# 提交變更
git add .
git commit -m "Add new feature"

# 推送到遠端
git push origin feature/new-feature

# 建立 Pull Request
```

### 版本控制

遵循 [Semantic Versioning](https://semver.org/)：
- MAJOR.MINOR.PATCH
- 例如：1.0.0, 1.1.0, 1.1.1

---

## 相關資源

- [FastAPI 文件](https://fastapi.tiangolo.com/)
- [React 文件](https://react.dev/)
- [Chrome Extension 文件](https://developer.chrome.com/docs/extensions/)
- [SQLAlchemy 文件](https://docs.sqlalchemy.org/)

---

**最後更新**: 2024-11-17
