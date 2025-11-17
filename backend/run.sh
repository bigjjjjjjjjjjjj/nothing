#!/bin/bash

# CourseAI 後端啟動腳本

echo "CourseAI Backend Starting..."

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "虛擬環境不存在，正在建立..."
    python -m venv venv
fi

# 啟動虛擬環境
source venv/bin/activate

# 安裝依賴
echo "檢查依賴..."
pip install -r requirements.txt -q

# 檢查環境變數
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，正在複製範例..."
    cp .env.example .env
    echo "請編輯 .env 文件設置必要的環境變數"
fi

# 執行資料庫遷移
echo "執行資料庫遷移..."
alembic upgrade head

# 啟動服務
echo "啟動 FastAPI 服務..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
