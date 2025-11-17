# CourseAI 待實作功能清單

## ✅ 已完成

- [x] 專案基礎架構建立
- [x] 後端 FastAPI 專案設置
- [x] 資料庫模型定義
- [x] API 路由架構
- [x] Pydantic Schemas
- [x] 前端 Chrome Extension 架構
- [x] Content Script 側邊欄 UI
- [x] Popup UI 基礎介面
- [x] API 客戶端封裝

## 🚧 進行中

### 後端服務實作

- [ ] **檔案處理服務** (`backend/app/services/slide_service.py`)
  - [ ] PDF 文字擷取 (PyPDF2)
  - [ ] PowerPoint 文字擷取 (python-pptx)
  - [ ] Word 文字擷取 (python-docx)
  - [ ] 檔案儲存到本地/雲端

- [ ] **語音轉文字服務** (`backend/app/services/speech_service.py`)
  - [ ] Google Speech-to-Text 整合
  - [ ] Whisper 整合（本地）
  - [ ] 音訊格式轉換
  - [ ] 即時轉錄處理

- [ ] **LLM 整合服務** (`backend/app/services/llm_service.py`)
  - [ ] GPT API 呼叫封裝
  - [ ] 課程內容分析
  - [ ] 章節結構識別
  - [ ] 題目生成邏輯
  - [ ] 簡答題批改邏輯
  - [ ] Prompt 模板管理

- [ ] **老師提示識別** (`backend/app/services/hint_service.py`)
  - [ ] 關鍵字匹配
  - [ ] LLM 上下文分析
  - [ ] 提示類型分類
  - [ ] 信心分數計算

- [ ] **課程分析服務** (`backend/app/services/course_service.py`)
  - [ ] 講義與轉錄同步分析
  - [ ] 時間軸對照建立
  - [ ] 重點摘要生成
  - [ ] 範圍建議生成

### 前端功能實作

- [ ] **音訊擷取** (`extension/src/content/audioCapture.ts`)
  - [ ] Web Audio API 整合
  - [ ] 麥克風權限處理
  - [ ] 音訊格式轉換
  - [ ] WebSocket 串流傳送

- [ ] **WebSocket 客戶端** (`extension/src/shared/websocket.ts`)
  - [ ] 連線管理
  - [ ] 斷線重連
  - [ ] 訊息處理
  - [ ] 錯誤處理

- [ ] **題目練習介面** (`extension/src/popup/QuizView.tsx`)
  - [ ] 題目顯示
  - [ ] 答案輸入
  - [ ] 提交與批改
  - [ ] 結果顯示

- [ ] **課程列表介面** (`extension/src/popup/CourseList.tsx`)
  - [ ] 課程列表顯示
  - [ ] 課程詳情頁
  - [ ] 轉錄內容查看
  - [ ] 重點摘要顯示

- [ ] **老師提示查看** (`extension/src/popup/HintsView.tsx`)
  - [ ] 提示列表顯示
  - [ ] 類型篩選
  - [ ] 跳轉播放功能

### 資料庫與 Alembic

- [ ] **Alembic 遷移設置**
  ```bash
  cd backend
  alembic init alembic
  ```

- [ ] **建立初始遷移**
  ```bash
  alembic revision --autogenerate -m "Initial schema"
  alembic upgrade head
  ```

### 測試

- [ ] **後端單元測試**
  - [ ] API 端點測試
  - [ ] 服務層測試
  - [ ] 模型測試

- [ ] **前端測試**
  - [ ] 元件測試
  - [ ] API 客戶端測試
  - [ ] 整合測試

## 📦 優化項目

### 效能優化

- [ ] Redis 快取實作
  - [ ] 課程摘要快取
  - [ ] 轉錄資料快取
  - [ ] API 響應快取

- [ ] 資料庫查詢優化
  - [ ] 索引優化
  - [ ] N+1 查詢問題
  - [ ] 連線池設定

- [ ] 前端效能
  - [ ] React.memo 優化
  - [ ] 虛擬滾動
  - [ ] 圖片/資源懶載入

### 使用者體驗

- [ ] **錯誤處理**
  - [ ] 友善錯誤訊息
  - [ ] 載入狀態顯示
  - [ ] 重試機制

- [ ] **UI/UX 改進**
  - [ ] 響應式設計
  - [ ] 無障礙功能 (a11y)
  - [ ] 深色模式

- [ ] **國際化**
  - [ ] i18n 設置
  - [ ] 多語言支援（中文、英文）

### 安全性

- [ ] **認證與授權**
  - [ ] JWT Token 驗證
  - [ ] 使用者註冊/登入
  - [ ] 權限管理

- [ ] **資料保護**
  - [ ] 敏感資料加密
  - [ ] SQL Injection 防護
  - [ ] XSS 防護

## 🎯 進階功能

### Phase 3 功能

- [ ] **錯題集**
  - [ ] 錯題記錄
  - [ ] 錯題複習
  - [ ] 錯題統計

- [ ] **學習統計**
  - [ ] 學習時數統計
  - [ ] 答題正確率
  - [ ] 弱項分析

- [ ] **智慧搜尋**
  - [ ] 語意搜尋
  - [ ] 自然語言問答
  - [ ] 搜尋結果排序

- [ ] **社交功能**
  - [ ] 題目分享
  - [ ] 課程分享
  - [ ] 學習小組

### 整合功能

- [ ] **Google Drive 整合**
  - [ ] 錄影自動上傳
  - [ ] 講義同步
  - [ ] OAuth 認證

- [ ] **行事曆整合**
  - [ ] 自動建立課程
  - [ ] 課程提醒

- [ ] **其他平台支援**
  - [ ] Microsoft Teams
  - [ ] Zoom
  - [ ] Discord

## 📝 文件

- [ ] **API 文件**
  - [ ] 詳細的 API 說明
  - [ ] 請求/響應範例
  - [ ] 錯誤代碼說明

- [ ] **使用者手冊**
  - [ ] 安裝指南
  - [ ] 功能說明
  - [ ] 常見問題

- [ ] **開發者文件**
  - [ ] 架構說明
  - [ ] 擴充指南
  - [ ] 貢獻指南

## 🚀 部署

- [ ] **Docker 化**
  - [ ] Dockerfile 編寫
  - [ ] docker-compose.yml
  - [ ] 容器化最佳實踐

- [ ] **CI/CD**
  - [ ] GitHub Actions 設置
  - [ ] 自動測試
  - [ ] 自動部署

- [ ] **監控與日誌**
  - [ ] 應用監控 (Prometheus)
  - [ ] 錯誤追蹤 (Sentry)
  - [ ] 日誌管理 (ELK)

---

## 優先級說明

🔴 **高優先級** - MVP 必須功能
🟡 **中優先級** - 完整版功能
🟢 **低優先級** - 優化與進階功能

### 當前建議開發順序

1. 🔴 實作檔案處理服務（講義上傳功能）
2. 🔴 實作語音轉文字服務（即時轉錄）
3. 🔴 實作 LLM 題目生成（基礎版）
4. 🔴 完成音訊擷取功能
5. 🟡 實作老師提示識別
6. 🟡 實作課程分析與範圍建議
7. 🟡 實作簡答題批改
8. 🟢 錯題集與學習統計
9. 🟢 智慧搜尋
10. 🟢 社交功能

---

**最後更新**: 2024-11-17
