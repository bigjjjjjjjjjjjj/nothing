#!/bin/bash

# CourseAI 日誌查看腳本

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_menu() {
    echo ""
    echo "========================================="
    echo "  CourseAI 日誌查看器"
    echo "========================================="
    echo ""
    echo "選擇要查看的日誌："
    echo ""
    echo "  1) 後端服務日誌"
    echo "  2) Celery Worker 日誌"
    echo "  3) PostgreSQL 日誌"
    echo "  4) Redis 日誌"
    echo "  5) 所有服務日誌"
    echo "  6) 錯誤日誌 (backend/logs/error.log)"
    echo "  7) 應用日誌 (backend/logs/app.log)"
    echo "  8) 實時查看所有日誌"
    echo "  0) 退出"
    echo ""
    echo -n "請選擇 [0-8]: "
}

while true; do
    show_menu
    read -r choice

    case $choice in
        1)
            echo -e "${BLUE}查看後端服務日誌...${NC}"
            docker-compose logs --tail=100 backend
            ;;
        2)
            echo -e "${BLUE}查看 Celery Worker 日誌...${NC}"
            docker-compose logs --tail=100 celery-worker
            ;;
        3)
            echo -e "${BLUE}查看 PostgreSQL 日誌...${NC}"
            docker-compose logs --tail=100 postgres
            ;;
        4)
            echo -e "${BLUE}查看 Redis 日誌...${NC}"
            docker-compose logs --tail=100 redis
            ;;
        5)
            echo -e "${BLUE}查看所有服務日誌...${NC}"
            docker-compose logs --tail=50
            ;;
        6)
            echo -e "${BLUE}查看錯誤日誌...${NC}"
            if [ -f "backend/logs/error.log" ]; then
                tail -n 100 backend/logs/error.log
            else
                echo -e "${YELLOW}錯誤日誌文件不存在${NC}"
            fi
            ;;
        7)
            echo -e "${BLUE}查看應用日誌...${NC}"
            if [ -f "backend/logs/app.log" ]; then
                tail -n 100 backend/logs/app.log
            else
                echo -e "${YELLOW}應用日誌文件不存在${NC}"
            fi
            ;;
        8)
            echo -e "${BLUE}實時查看所有日誌 (Ctrl+C 退出)...${NC}"
            docker-compose logs -f
            ;;
        0)
            echo -e "${GREEN}退出${NC}"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}無效選擇，請重新輸入${NC}"
            ;;
    esac

    echo ""
    echo -n "按 Enter 繼續..."
    read
done
