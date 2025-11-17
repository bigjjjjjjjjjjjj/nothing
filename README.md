# CourseAI 智慧學習助理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9+-blue.svg)](https://www.typescriptlang.org/)

一款結合 AI 的 Chrome/Edge 瀏覽器外掛，為 Google Meet 線上課程提供即時轉錄、智能題目生成和學習輔助功能。

## 核心功能

- **即時語音轉錄**: Google Meet 課程即時轉文字
- **講義智能解析**: 支援 PDF/PPT/Word 格式
- **AI 課程分析**: 自動生成課程重點摘要
- **智能題目生成**: 選擇題、填充題、簡答題自動生成
- **自動批改**: AI 批改簡答題並提供詳細反饋
- **重點提示識別**: 自動識別「老師說會考的部分」
- **智慧搜尋**: 自然語言搜尋課程內容

## 技術架構

### 前端 (Chrome Extension)
- **語言**: TypeScript
- **框架**: React 18
- **構建工具**: Webpack 5
- **API 通訊**: WebSocket + REST

### 後端 (API Server)
- **語言**: Python 3.9+
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **任務隊列**: Celery
- **快取**: Redis
- **資料庫**: PostgreSQL

### AI/ML 服務
- **LLM**: GPT OSS120B (AMD Instinct MI300X)
- **語音轉文字**: Google Speech-to-Text / Whisper
- **文件解析**: PyPDF2, python-docx, python-pptx

## 專案結構

```
course-ai/
├── backend/                 # 後端 API 服務
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 資料庫模型
│   │   ├── services/       # 業務邏輯
│   │   └── schemas/        # Pydantic 模型
│   ├── tests/              # 後端測試
│   └── requirements.txt    # Python 依賴
├── extension/              # Chrome 外掛
│   ├── src/
│   │   ├── content/        # Content Scripts
│   │   ├── background/     # Background Script
│   │   ├── popup/          # Popup UI
│   │   ├── shared/         # 共用模組
│   │   └── styles/         # 樣式檔案
│   ├── public/             # 靜態資源
│   └── manifest.json       # 外掛配置
├── docs/                   # 文件
└── README.md
```

## 快速開始

### 環境需求

- **Node.js**: 16.x 或更高版本
- **Python**: 3.9 或更高版本
- **PostgreSQL**: 13 或更高版本
- **Redis**: 6.x 或更高版本

### 後端設置

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt

# 設置環境變數
cp .env.example .env
# 編輯 .env 填入必要的配置

# 初始化資料庫
alembic upgrade head

# 啟動服務
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端設置

```bash
# 進入前端目錄
cd extension

# 安裝依賴
npm install

# 開發模式構建
npm run dev

# 生產構建
npm run build
```

### Chrome 外掛安裝

1. 打開 Chrome 瀏覽器，進入 `chrome://extensions/`
2. 開啟「開發者模式」
3. 點擊「載入未封裝項目」
4. 選擇 `extension/dist` 目錄

## API 文件

後端服務啟動後，訪問以下 URL 查看 API 文件：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 測試

### 後端測試
```bash
cd backend
pytest tests/ -v --cov=app
```

### 前端測試
```bash
cd extension
npm test
```

## 開發階段

- [x] **Phase 1**: 專案架構建立
- [ ] **Phase 2**: MVP 核心功能 (轉錄、講義、基本題目)
- [ ] **Phase 3**: 完整功能 (範圍分類、提示識別)
- [ ] **Phase 4**: 優化與擴充

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

## 授權

本專案採用 MIT 授權條款

## 聯繫方式

如有問題或建議，請開 Issue 或聯繫專案維護者。

---

**版本**: v1.0.0
**最後更新**: 2024-11-17