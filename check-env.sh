#!/bin/bash
set -e

# CourseAI 環境檢查腳本

echo "========================================="
echo "  CourseAI 環境檢查"
echo "========================================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 檢查結果計數
PASS=0
WARN=0
FAIL=0

# 檢查函數
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASS++))
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        ((FAIL++))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASS++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $2"
        ((WARN++))
        return 1
    fi
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} 端口 $1 已被占用"
        ((WARN++))
        return 1
    else
        echo -e "${GREEN}✓${NC} 端口 $1 可用"
        ((PASS++))
        return 0
    fi
}

# 1. 檢查系統工具
echo "1. 系統工具檢查"
echo "-------------------"
check_command "docker" "Docker 已安裝"
check_command "docker-compose" "Docker Compose 已安裝"
check_command "git" "Git 已安裝"
check_command "node" "Node.js 已安裝"
check_command "npm" "npm 已安裝"
check_command "python3" "Python 3 已安裝"
check_command "curl" "curl 已安裝"
echo ""

# 2. 檢查 Python 版本
echo "2. Python 版本檢查"
echo "-------------------"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9.0"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo -e "${GREEN}✓${NC} Python 版本: $PYTHON_VERSION (>= 3.9)"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Python 版本: $PYTHON_VERSION (需要 >= 3.9)"
    ((FAIL++))
fi
echo ""

# 3. 檢查 Node.js 版本
echo "3. Node.js 版本檢查"
echo "-------------------"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d 'v' -f 2)
    echo -e "${GREEN}✓${NC} Node.js 版本: $NODE_VERSION"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Node.js 未安裝"
    ((FAIL++))
fi
echo ""

# 4. 檢查配置文件
echo "4. 配置文件檢查"
echo "-------------------"
check_file "backend/.env" ".env 配置文件存在"
check_file "backend/requirements.txt" "requirements.txt 存在"
check_file "extension/package.json" "package.json 存在"
check_file "docker-compose.yml" "docker-compose.yml 存在"
echo ""

# 5. 檢查環境變數
echo "5. 環境變數檢查"
echo "-------------------"
if [ -f "backend/.env" ]; then
    source backend/.env

    if [ -n "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "your-openai-api-key" ]; then
        echo -e "${GREEN}✓${NC} OPENAI_API_KEY 已設定"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠${NC} OPENAI_API_KEY 未設定或使用預設值"
        ((WARN++))
    fi

    if [ -n "$DATABASE_URL" ]; then
        echo -e "${GREEN}✓${NC} DATABASE_URL 已設定"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} DATABASE_URL 未設定"
        ((FAIL++))
    fi
else
    echo -e "${RED}✗${NC} .env 文件不存在"
    ((FAIL++))
fi
echo ""

# 6. 檢查端口可用性
echo "6. 端口可用性檢查"
echo "-------------------"
check_port 8000
check_port 5432
check_port 6379
check_port 5555
echo ""

# 7. 檢查 Docker 狀態
echo "7. Docker 狀態檢查"
echo "-------------------"
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker daemon 正在運行"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Docker daemon 未運行"
    ((FAIL++))
fi
echo ""

# 8. 檢查磁盤空間
echo "8. 磁盤空間檢查"
echo "-------------------"
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo -e "${GREEN}✓${NC} 磁盤使用率: ${DISK_USAGE}%"
    ((PASS++))
else
    echo -e "${YELLOW}⚠${NC} 磁盤使用率: ${DISK_USAGE}% (建議清理)"
    ((WARN++))
fi
echo ""

# 總結
echo "========================================="
echo "檢查結果總結"
echo "========================================="
echo -e "${GREEN}通過: $PASS${NC}"
echo -e "${YELLOW}警告: $WARN${NC}"
echo -e "${RED}失敗: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ 環境檢查通過，可以啟動 CourseAI${NC}"
    exit 0
else
    echo -e "${RED}✗ 發現 $FAIL 個問題，請修復後再啟動${NC}"
    exit 1
fi
