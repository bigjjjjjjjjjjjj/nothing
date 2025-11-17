#!/bin/bash
set -e

# CourseAI 快速啟動腳本

echo "========================================="
echo "  CourseAI 啟動腳本"
echo "========================================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}錯誤: Docker 未安裝${NC}"
    echo "請先安裝 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}錯誤: Docker Compose 未安裝${NC}"
    echo "請先安裝 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 檢查 .env 文件
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}警告: backend/.env 文件不存在${NC}"
    echo "正在從 .env.example 創建..."
    cp backend/.env.example backend/.env
    echo -e "${GREEN}已創建 backend/.env${NC}"
    echo -e "${YELLOW}請編輯 backend/.env 並設定 API 金鑰${NC}"
    echo ""
fi

# 檢查必要的環境變數
echo "檢查環境變數..."
source backend/.env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key" ]; then
    echo -e "${YELLOW}警告: OPENAI_API_KEY 未設定${NC}"
    echo "LLM 功能將無法使用，請在 backend/.env 中設定"
fi

# 停止舊容器
echo ""
echo "停止現有容器..."
docker-compose down 2>/dev/null || true

# 建置並啟動服務
echo ""
echo "建置並啟動服務..."
docker-compose up -d --build

# 等待服務啟動
echo ""
echo "等待服務啟動..."
sleep 5

# 檢查服務狀態
echo ""
echo "檢查服務狀態..."
docker-compose ps

# 執行資料庫遷移
echo ""
echo "執行資料庫遷移..."
docker-compose exec -T backend alembic upgrade head

# 健康檢查
echo ""
echo "執行健康檢查..."
sleep 3

if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ 後端服務正常運行${NC}"
else
    echo -e "${RED}✗ 後端服務啟動失敗${NC}"
    echo "請查看日誌: docker-compose logs backend"
    exit 1
fi

# 顯示服務 URL
echo ""
echo "========================================="
echo -e "${GREEN}CourseAI 啟動成功！${NC}"
echo "========================================="
echo ""
echo "服務端點："
echo "  - 後端 API:    http://localhost:8000"
echo "  - API 文件:    http://localhost:8000/docs"
echo "  - Flower 監控: http://localhost:5555"
echo ""
echo "常用命令："
echo "  - 查看日誌:    docker-compose logs -f"
echo "  - 停止服務:    docker-compose down"
echo "  - 重啟服務:    docker-compose restart"
echo ""
echo "前端開發："
echo "  cd extension && npm install && npm run build"
echo ""
