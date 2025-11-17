# CourseAI 部署指南

## 快速開始（使用 Docker）

### 前置需求
- Docker 20.10+
- Docker Compose 2.0+

### 1. 克隆專案
```bash
git clone <repository-url>
cd nothing
```

### 2. 設定環境變數
```bash
cd backend
cp .env.example .env
# 編輯 .env 檔案，設定必要的 API 金鑰
```

必須設定的環境變數：
- `OPENAI_API_KEY`: OpenAI API 金鑰
- `GOOGLE_APPLICATION_CREDENTIALS`: Google Cloud 服務帳號 JSON 路徑（如果使用 Google Speech-to-Text）

### 3. 啟動服務
```bash
# 回到專案根目錄
cd ..
docker-compose up -d
```

服務將在以下端口啟動：
- 後端 API: http://localhost:8000
- API 文件: http://localhost:8000/docs
- Flower 監控: http://localhost:5555

### 4. 檢查服務狀態
```bash
docker-compose ps
docker-compose logs -f backend
```

### 5. 停止服務
```bash
docker-compose down
```

---

## 本地開發環境設定

### 後端設定

#### 1. 安裝 Python 依賴
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. 設定資料庫
```bash
# 安裝並啟動 PostgreSQL
# macOS: brew install postgresql && brew services start postgresql
# Ubuntu: sudo apt install postgresql && sudo systemctl start postgresql

# 建立資料庫
createdb courseai

# 執行資料庫遷移
alembic upgrade head
```

#### 3. 啟動 Redis
```bash
# macOS: brew install redis && brew services start redis
# Ubuntu: sudo apt install redis-server && sudo systemctl start redis
```

#### 4. 啟動後端服務
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. 啟動 Celery Worker（可選）
```bash
celery -A app.celery_worker worker --loglevel=info
```

### 前端設定

#### 1. 安裝依賴
```bash
cd extension
npm install
```

#### 2. 建置擴充功能
```bash
# 開發模式（自動重新建置）
npm run dev

# 生產模式
npm run build
```

#### 3. 載入擴充功能到瀏覽器

**Chrome:**
1. 開啟 `chrome://extensions/`
2. 啟用「開發人員模式」
3. 點擊「載入未封裝項目」
4. 選擇 `extension/dist` 目錄

**Edge:**
1. 開啟 `edge://extensions/`
2. 啟用「開發人員模式」
3. 點擊「載入解壓縮的擴充功能」
4. 選擇 `extension/dist` 目錄

---

## 執行測試

### 後端測試
```bash
cd backend

# 執行所有測試
pytest

# 執行特定測試文件
pytest tests/services/test_hint_service.py

# 查看覆蓋率
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 生產環境部署

### 環境需求
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- 至少 2GB RAM
- 至少 10GB 儲存空間

### 安全設定

1. **更改預設密碼**
```bash
# 在 .env 中設定強密碼
SECRET_KEY=<隨機生成的強密碼>
POSTGRES_PASSWORD=<強資料庫密碼>
```

2. **啟用 HTTPS**
建議使用 Nginx 作為反向代理並配置 SSL：
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. **設定防火牆**
```bash
# 只開放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

4. **配置日誌輪替**
已內建在應用中，日誌會自動輪替（10MB，保留 5 個備份）。

### 效能優化

1. **調整 Worker 數量**
```yaml
# docker-compose.yml
celery-worker:
  command: celery -A app.celery_worker worker --concurrency=4 --loglevel=info
```

2. **啟用資料庫連線池**
```python
# 在 .env 中設定
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

3. **設定 Redis 記憶體限制**
```yaml
# docker-compose.yml
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

---

## 監控與維護

### 健康檢查
```bash
curl http://localhost:8000/health
```

### 查看日誌
```bash
# Docker 環境
docker-compose logs -f backend
docker-compose logs -f celery-worker

# 本地開發
tail -f backend/logs/app.log
tail -f backend/logs/error.log
```

### 資料庫備份
```bash
# 備份
docker-compose exec postgres pg_dump -U courseai courseai > backup.sql

# 還原
docker-compose exec -T postgres psql -U courseai courseai < backup.sql
```

### 效能監控
訪問 Flower: http://localhost:5555

---

## 故障排除

### 後端無法啟動
1. 檢查資料庫連線：`docker-compose logs postgres`
2. 檢查環境變數：確認 `.env` 檔案存在且正確
3. 檢查端口占用：`lsof -i :8000`

### WebSocket 連線失敗
1. 確認防火牆設定
2. 檢查 CORS 設定在 `backend/app/core/config.py`
3. 確認前端 WebSocket URL 正確

### 轉錄無聲音
1. 檢查麥克風權限
2. 確認 Chrome 擴充功能有 `tabCapture` 權限
3. 查看瀏覽器控制台錯誤訊息

### 資料庫遷移失敗
```bash
# 重置遷移
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

---

## 更新與升級

### 更新應用程式
```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### 資料庫遷移
```bash
# 建立新的遷移
docker-compose exec backend alembic revision --autogenerate -m "description"

# 執行遷移
docker-compose exec backend alembic upgrade head

# 回滾遷移
docker-compose exec backend alembic downgrade -1
```
