# CourseAI 智慧學習助理 - 技術規格書

**版本：** v1.0
**最後更新：** 2024-11-17
**專案類型：** Chrome/Edge 瀏覽器外掛 + 後端 API 服務

---

## 目錄

1. [系統架構概述](#1-系統架構概述)
2. [前端外掛設計](#2-前端外掛設計)
3. [後端 API 設計](#3-後端-api-設計)
4. [核心功能實作細節](#4-核心功能實作細節)
5. [資料結構定義](#5-資料結構定義)
6. [開發階段規劃](#6-開發階段規劃)

---

## 1. 系統架構概述

### 1.1 整體架構

```
┌─────────────────────────────────────────────────┐
│          Chrome/Edge 瀏覽器外掛                 │
├─────────────────────────────────────────────────┤
│  Content Script (注入 Meet 頁面)                │
│  - 擷取即時音訊                                  │
│  - 渲染側邊欄 UI                                 │
│  - 監聽 DOM 變化                                 │
├─────────────────────────────────────────────────┤
│  Background Script (背景處理)                    │
│  - 管理 WebSocket 連線                          │
│  - 處理 Google Drive API 呼叫                   │
│  - 資料快取與同步                               │
├─────────────────────────────────────────────────┤
│  Popup UI (外掛控制面板)                        │
│  - 設定頁面                                      │
│  - 課程列表                                      │
│  - 題目練習介面                                  │
└─────────────────────────────────────────────────┘
                      ↕ (WebSocket/REST API)
┌─────────────────────────────────────────────────┐
│              後端 API 服務 (FastAPI)            │
├─────────────────────────────────────────────────┤
│  語音轉文字服務                                  │
│  文件解析服務                                    │
│  LLM 整合服務 (GPT OSS120B)                     │
│  題庫管理服務                                    │
│  批改服務                                        │
└─────────────────────────────────────────────────┘
                      ↕
┌─────────────────────────────────────────────────┐
│            外部服務 & 儲存                       │
├─────────────────────────────────────────────────┤
│  Google Speech-to-Text API / Whisper           │
│  Google Drive API                               │
│  PostgreSQL (課程、題庫、使用者資料)            │
│  Redis (快取、即時轉錄暫存)                      │
└─────────────────────────────────────────────────┘
```

### 1.2 技術棧總覽

**前端外掛：**
- TypeScript
- React (UI 元件)
- Chrome Extension Manifest V3
- Web Audio API
- WebSocket Client

**後端服務：**
- Python 3.9+
- FastAPI
- SQLAlchemy (ORM)
- Redis
- Celery (背景任務)

**AI/ML 服務：**
- GPT OSS120B (AMD Instinct MI300X)
- Google Speech-to-Text / Whisper
- PyPDF2, python-docx, python-pptx

---

## 2. 前端外掛設計

### 2.1 檔案結構

```
course-ai-extension/
├── manifest.json              # 外掛設定檔
├── src/
│   ├── content/              # Content Scripts
│   │   ├── index.tsx         # 主入口，注入到 Meet 頁面
│   │   ├── sidebar.tsx       # 側邊欄 UI 元件
│   │   ├── audioCapture.ts   # 音訊擷取模組
│   │   └── meetIntegration.ts # Meet DOM 操作
│   ├── background/           # Background Script
│   │   ├── index.ts          # 背景服務主程式
│   │   ├── websocket.ts      # WebSocket 連線管理
│   │   ├── driveAPI.ts       # Google Drive 整合
│   │   └── storage.ts        # 資料儲存管理
│   ├── popup/                # Popup UI
│   │   ├── index.tsx         # Popup 主頁面
│   │   ├── CourseList.tsx    # 課程列表
│   │   ├── QuizView.tsx      # 題目練習介面
│   │   └── Settings.tsx      # 設定頁面
│   ├── shared/               # 共用模組
│   │   ├── api.ts            # API 呼叫封裝
│   │   ├── types.ts          # TypeScript 型別定義
│   │   └── utils.ts          # 工具函式
│   └── styles/               # CSS 樣式
├── public/
│   ├── icons/                # 外掛圖示
│   └── assets/               # 靜態資源
└── webpack.config.js         # 打包設定
```

### 2.2 Manifest V3 設定

```json
{
  "manifest_version": 3,
  "name": "CourseAI 智慧學習助理",
  "version": "1.0.0",
  "description": "Google Meet 即時轉錄與智慧學習輔助",
  "permissions": [
    "storage",
    "activeTab",
    "tabs"
  ],
  "host_permissions": [
    "https://meet.google.com/*",
    "https://drive.google.com/*",
    "https://api.courseai.example.com/*"
  ],
  "content_scripts": [
    {
      "matches": ["https://meet.google.com/*"],
      "js": ["content.js"],
      "css": ["content.css"]
    }
  ],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "web_accessible_resources": [
    {
      "resources": ["sidebar.html", "assets/*"],
      "matches": ["https://meet.google.com/*"]
    }
  ]
}
```

### 2.3 側邊欄 UI 設計

**側邊欄結構：**

```
┌─────────────────────────┐
│  CourseAI 🎓           │
├─────────────────────────┤
│  [收合/展開按鈕]        │
├─────────────────────────┤
│  📁 上傳講義            │
│  [選擇檔案] PDF/PPT     │
├─────────────────────────┤
│  🎤 即時轉錄            │
│  ┌─────────────────┐   │
│  │ 老師：今天我們... │   │
│  │ [00:05:23]       │   │
│  │                  │   │
│  │ 這個重點很重要... │   │
│  │ [00:08:45]       │   │
│  └─────────────────┘   │
│  [暫停] [清除]         │
├─────────────────────────┤
│  📝 課程重點 (課後)     │
│  [生成重點摘要]        │
├─────────────────────────┤
│  ✏️ 生成試題 (課後)    │
│  [生成試題]            │
└─────────────────────────┘
```

**側邊欄狀態管理：**

```typescript
interface SidebarState {
  isOpen: boolean;              // 側邊欄是否開啟
  currentCourseId: string | null; // 當前課程 ID
  transcription: TranscriptItem[]; // 即時轉錄內容
  isRecording: boolean;         // 是否正在錄音
  uploadedFile: File | null;    // 上傳的講義檔案
  summary: CourseSummary | null; // 課程重點摘要
  quizzes: Quiz[] | null;       // 生成的題目
}

interface TranscriptItem {
  timestamp: string;  // 時間戳記 (格式: HH:MM:SS)
  text: string;       // 轉錄文字
  confidence: number; // 信心分數 (0-1)
}
```

### 2.4 音訊擷取實作

**audioCapture.ts 核心邏輯：**

```typescript
class AudioCapture {
  private mediaStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private websocket: WebSocket | null = null;

  // 初始化音訊擷取
  async startCapture(meetingId: string): Promise<void> {
    // 1. 取得 Meet 的音訊串流
    this.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    // 2. 建立 AudioContext
    this.audioContext = new AudioContext({ sampleRate: 16000 });
    const source = this.audioContext.createMediaStreamSource(this.mediaStream);

    // 3. 建立音訊處理節點
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

    // 4. 連接到 WebSocket，傳送音訊資料
    this.websocket = new WebSocket(`wss://api.courseai.example.com/transcribe?meeting=${meetingId}`);

    // 5. 處理音訊資料
    this.processor.onaudioprocess = (e) => {
      const audioData = e.inputBuffer.getChannelData(0);
      const int16Data = this.floatTo16BitPCM(audioData);

      if (this.websocket?.readyState === WebSocket.OPEN) {
        this.websocket.send(int16Data);
      }
    };

    source.connect(this.processor);
    this.processor.connect(this.audioContext.destination);
  }

  // 停止擷取
  stopCapture(): void {
    this.processor?.disconnect();
    this.mediaStream?.getTracks().forEach(track => track.stop());
    this.websocket?.close();
  }

  // 轉換音訊格式：Float32 → Int16
  private floatTo16BitPCM(float32Array: Float32Array): Int16Array {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
  }
}
```

### 2.5 Meet DOM 整合

**meetIntegration.ts 核心功能：**

```typescript
class MeetIntegration {
  // 偵測 Meet 頁面並注入側邊欄
  injectSidebar(): void {
    const observer = new MutationObserver((mutations) => {
      const meetContainer = document.querySelector('[data-meeting-id]');
      if (meetContainer && !document.getElementById('courseai-sidebar')) {
        this.createSidebar(meetContainer);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  // 建立側邊欄元素
  private createSidebar(container: Element): void {
    const sidebar = document.createElement('div');
    sidebar.id = 'courseai-sidebar';
    sidebar.className = 'courseai-sidebar';

    // 注入 React 元件
    const root = ReactDOM.createRoot(sidebar);
    root.render(<Sidebar />);

    // 插入到 Meet 介面
    container.appendChild(sidebar);
  }

  // 取得當前會議 ID
  getMeetingId(): string | null {
    const url = new URL(window.location.href);
    const meetingId = url.pathname.split('/').pop();
    return meetingId || null;
  }

  // 偵測課程開始/結束
  detectMeetingStatus(): 'started' | 'ended' | 'idle' {
    const leaveButton = document.querySelector('[data-tooltip*="離開通話"]');
    if (leaveButton) return 'started';

    const joinButton = document.querySelector('[data-tooltip*="加入"]');
    if (joinButton) return 'idle';

    return 'ended';
  }
}
```

---

## 3. 後端 API 設計

### 3.1 API 端點總覽

**Base URL:** `https://api.courseai.example.com/v1`

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/courses/create` | 建立新課程 |
| GET | `/courses/{course_id}` | 取得課程資訊 |
| POST | `/courses/{course_id}/upload-slides` | 上傳講義 |
| WS | `/transcribe` | 即時語音轉錄 (WebSocket) |
| POST | `/courses/{course_id}/analyze` | 分析課程內容並生成重點 |
| POST | `/courses/{course_id}/suggest-quiz-scopes` | 建議題目生成範圍 |
| POST | `/quizzes/generate` | 生成題目 |
| POST | `/quizzes/{quiz_id}/submit` | 提交答案 |
| GET | `/quizzes/{quiz_id}/result` | 取得批改結果 |
| GET | `/users/me/stats` | 取得學習統計 |

### 3.2 API 詳細規格

#### 3.2.1 建立課程

```
POST /courses/create
```

**Request Body:**
```json
{
  "meeting_id": "abc-defg-hij",
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "course_name": "資料結構 第三週",
  "started_at": "2024-11-17T10:00:00Z"
}
```

**Response:**
```json
{
  "course_id": "course_123456",
  "status": "created",
  "created_at": "2024-11-17T10:00:05Z"
}
```

#### 3.2.2 上傳講義

```
POST /courses/{course_id}/upload-slides
Content-Type: multipart/form-data
```

**Request:**
```
file: [Binary File Data]
```

**Response:**
```json
{
  "file_id": "file_789",
  "filename": "week3_data_structure.pdf",
  "pages": 25,
  "extracted_text_preview": "第三章：樹狀結構\n3.1 二元樹...",
  "status": "processed"
}
```

#### 3.2.3 即時語音轉錄 (WebSocket)

```
WS /transcribe?meeting=abc-defg-hij&course_id=course_123456
```

**Client → Server (Binary Audio Data):**
```
[Int16Array audio samples]
```

**Server → Client (JSON):**
```json
{
  "type": "transcript",
  "timestamp": "00:05:23",
  "text": "今天我們要講的是二元樹的走訪方法",
  "confidence": 0.92,
  "is_final": true
}
```

#### 3.2.4 分析課程內容

```
POST /courses/{course_id}/analyze
```

**Request Body:**
```json
{
  "include_slides": true,
  "include_transcript": true
}
```

**Response:**
```json
{
  "summary": {
    "key_points": [
      {
        "title": "二元樹定義",
        "content": "每個節點最多有兩個子節點...",
        "slide_page": 3,
        "transcript_timestamps": ["00:05:23", "00:08:45"]
      },
      {
        "title": "走訪方法",
        "content": "前序、中序、後序走訪...",
        "slide_page": 7,
        "transcript_timestamps": ["00:15:30"]
      }
    ],
    "concepts": ["二元樹", "走訪", "遞迴"],
    "formulas": ["T(n) = 2T(n/2) + O(1)"]
  },
  "status": "completed"
}
```

#### 3.2.5 建議題目生成範圍（重點功能）

```
POST /courses/{course_id}/suggest-quiz-scopes
```

**說明：**
使用者點擊「生成試題」後，先呼叫此 API。LLM 會分析課程內容（講義章節 + 語音轉錄），回傳可選擇的範圍選項。

**Request Body:**
```json
{
  "course_id": "course_123456"
}
```

**Response:**
```json
{
  "suggested_scopes": [
    {
      "scope_id": "scope_1",
      "label": "整堂課程",
      "description": "涵蓋本次課程所有內容",
      "estimated_questions": 15
    },
    {
      "scope_id": "scope_2",
      "label": "第三章：二元樹基礎",
      "description": "包含二元樹定義、性質、表示法",
      "slide_pages": [3, 4, 5, 6],
      "estimated_questions": 8
    },
    {
      "scope_id": "scope_3",
      "label": "第四章：樹的走訪",
      "description": "前序、中序、後序走訪及應用",
      "slide_pages": [7, 8, 9, 10],
      "estimated_questions": 10
    },
    {
      "scope_id": "scope_4",
      "label": "老師特別強調的部分",
      "description": "根據語音分析，老師重複說明或強調的內容",
      "transcript_timestamps": ["00:05:23", "00:15:30", "00:32:10"],
      "estimated_questions": 6
    }
  ],
  "default_scope": "scope_1"
}
```

#### 3.2.6 生成題目

```
POST /quizzes/generate
```

**Request Body:**
```json
{
  "course_id": "course_123456",
  "scope_id": "scope_2",  // 使用者選擇的範圍
  "question_types": {
    "multiple_choice": 5,  // 選擇題 5 題
    "fill_in_blank": 3,    // 填充題 3 題
    "short_answer": 2      // 簡答題 2 題
  },
  "difficulty": "medium"   // easy, medium, hard
}
```

**Response:**
```json
{
  "quiz_id": "quiz_456",
  "questions": [
    {
      "question_id": "q1",
      "type": "multiple_choice",
      "question_text": "以下何者是二元樹的特性？",
      "options": [
        "每個節點最多有兩個子節點",
        "每個節點必須有兩個子節點",
        "每個節點最多有一個子節點",
        "節點數量必須是偶數"
      ],
      "correct_answer": "每個節點最多有兩個子節點",
      "explanation": "二元樹的定義是每個節點最多有兩個子節點...",
      "slide_reference": 3,
      "video_timestamp": "00:05:23",
      "difficulty": "easy"
    },
    {
      "question_id": "q2",
      "type": "fill_in_blank",
      "question_text": "二元樹的前序走訪順序是：____、左子樹、右子樹",
      "correct_answer": "根節點",
      "explanation": "前序走訪的順序是先訪問根節點...",
      "slide_reference": 7,
      "video_timestamp": "00:15:30",
      "difficulty": "medium"
    },
    {
      "question_id": "q3",
      "type": "short_answer",
      "question_text": "請說明前序走訪和中序走訪的差異及應用場景",
      "model_answer": "前序走訪先訪問根節點，適合用於複製樹結構...",
      "evaluation_criteria": [
        "說明兩種走訪的順序差異",
        "提到至少一個應用場景",
        "邏輯清晰完整"
      ],
      "slide_reference": 7,
      "video_timestamp": "00:18:45",
      "difficulty": "hard"
    }
  ],
  "created_at": "2024-11-17T11:30:00Z"
}
```

#### 3.2.7 提交答案

```
POST /quizzes/{quiz_id}/submit
```

**Request Body:**
```json
{
  "answers": [
    {
      "question_id": "q1",
      "user_answer": "每個節點最多有兩個子節點"
    },
    {
      "question_id": "q2",
      "user_answer": "根節點"
    },
    {
      "question_id": "q3",
      "user_answer": "前序走訪是根-左-右，中序是左-根-右。前序適合複製樹，中序可以得到排序結果。"
    }
  ]
}
```

**Response:**
```json
{
  "submission_id": "sub_789",
  "status": "grading",
  "estimated_time": "5 seconds"
}
```

#### 3.2.8 取得批改結果

```
GET /quizzes/{quiz_id}/result?submission_id=sub_789
```

**Response:**
```json
{
  "quiz_id": "quiz_456",
  "submission_id": "sub_789",
  "total_questions": 3,
  "correct_count": 2,
  "score": 85,
  "results": [
    {
      "question_id": "q1",
      "is_correct": true,
      "user_answer": "每個節點最多有兩個子節點",
      "feedback": "正確！"
    },
    {
      "question_id": "q2",
      "is_correct": true,
      "user_answer": "根節點",
      "feedback": "完全正確"
    },
    {
      "question_id": "q3",
      "is_correct": false,
      "user_answer": "前序走訪是根-左-右，中序是左-根-右。前序適合複製樹，中序可以得到排序結果。",
      "score": 70,
      "feedback": "回答基本正確，但可以更詳細說明應用場景。例如前序走訪在表達式樹中的應用...",
      "improvement_suggestions": [
        "可以舉更具體的例子說明應用",
        "說明為何中序走訪可得到排序結果"
      ]
    }
  ],
  "weak_concepts": ["樹的走訪應用"],
  "recommended_review": {
    "slide_pages": [7, 8],
    "video_timestamps": ["00:15:30", "00:18:45"]
  }
}
```

---

## 4. 核心功能實作細節

### 4.1 題目生成完整流程

**使用者操作流程：**

```
1. 下課後，使用者點擊側邊欄「生成試題」按鈕
   ↓
2. 外掛呼叫 POST /courses/{course_id}/suggest-quiz-scopes
   顯示 Loading 狀態：「AI 正在分析課程內容...」
   ↓
3. 後端 LLM 分析講義章節結構 + 語音轉錄內容
   識別出：
   - 講義的章節劃分
   - 老師特別強調的部分（重複次數、停頓、語氣）
   - 估計各範圍可以出幾題
   ↓
4. 回傳建議範圍選項
   外掛顯示選項讓使用者選擇：

   ┌────────────────────────────────┐
   │ 請選擇題目生成範圍：           │
   │                                │
   │ ○ 整堂課程 (約 15 題)         │
   │ ● 第三章：二元樹基礎 (約 8 題) │
   │ ○ 第四章：樹的走訪 (約 10 題) │
   │ ○ 老師特別強調的部分 (約 6 題) │
   │                                │
   │ 題型選擇：                     │
   │ ☑ 選擇題 [5] 題               │
   │ ☑ 填充題 [3] 題               │
   │ ☑ 簡答題 [2] 題               │
   │                                │
   │ 難度：○ 簡單 ● 中等 ○ 困難   │
   │                                │
   │        [生成題目]              │
   └────────────────────────────────┘
   ↓
5. 使用者選擇範圍、題型、難度後，點擊「生成題目」
   外掛呼叫 POST /quizzes/generate
   ↓
6. 後端根據選擇的範圍，提取對應的講義內容 + 語音轉錄
   使用 GPT OSS120B 生成題目
   ↓
7. 回傳題目列表
   外掛顯示題目，使用者可以開始作答
```

**後端實作邏輯（pseudocode）：**

```python
# 建議題目範圍 API
@app.post("/courses/{course_id}/suggest-quiz-scopes")
async def suggest_quiz_scopes(course_id: str):
    # 1. 取得課程資料
    course = await db.get_course(course_id)
    slides_text = await db.get_slides_text(course_id)
    transcript = await db.get_transcript(course_id)

    # 2. 使用 LLM 分析內容結構
    prompt = f"""
    分析以下課程內容，建議可以出題的範圍。

    講義內容：
    {slides_text}

    課堂語音轉錄：
    {transcript}

    請識別：
    1. 講義的章節結構（依據標題、頁碼）
    2. 老師特別強調的內容（重複說明、停頓、語氣）
    3. 每個範圍適合出幾題

    請以 JSON 格式回傳：
    {{
      "scopes": [
        {{
          "label": "範圍名稱",
          "description": "範圍說明",
          "slide_pages": [頁碼列表],
          "transcript_timestamps": ["時間戳記"],
          "estimated_questions": 數量
        }}
      ]
    }}
    """

    # 3. 呼叫 GPT OSS120B
    llm_response = await llm_client.generate(prompt)
    scopes = parse_json(llm_response)

    # 4. 回傳建議範圍
    return {
        "suggested_scopes": scopes,
        "default_scope": scopes[0]["scope_id"]
    }


# 生成題目 API
@app.post("/quizzes/generate")
async def generate_quiz(request: GenerateQuizRequest):
    # 1. 根據 scope_id 提取對應內容
    scope = await get_scope_content(request.course_id, request.scope_id)

    # 2. 建構 prompt
    prompt = f"""
    根據以下課程內容，生成 {request.question_types} 題目。

    內容範圍：{scope.description}
    講義內容：{scope.slides_text}
    語音轉錄：{scope.transcript_text}

    要求：
    - 選擇題：{request.question_types.multiple_choice} 題
    - 填充題：{request.question_types.fill_in_blank} 題
    - 簡答題：{request.question_types.short_answer} 題
    - 難度：{request.difficulty}

    每題需包含：
    1. 題目文字
    2. 選項（選擇題）
    3. 正確答案
    4. 詳細解析
    5. 對應的講義頁碼
    6. 對應的錄影時間點

    請以 JSON 格式回傳...
    """

    # 3. 呼叫 LLM 生成題目
    llm_response = await llm_client.generate(prompt)
    questions = parse_json(llm_response)

    # 4. 儲存到資料庫
    quiz_id = await db.save_quiz(request.course_id, questions)

    # 5. 回傳題目
    return {
        "quiz_id": quiz_id,
        "questions": questions
    }
```

### 4.2 即時語音轉錄實作

**WebSocket Handler：**

```python
# 後端 WebSocket 處理
@app.websocket("/transcribe")
async def websocket_endpoint(websocket: WebSocket, meeting: str, course_id: str):
    await websocket.accept()

    # 初始化語音辨識
    speech_client = SpeechClient()
    streaming_config = speech_client.streaming_config(
        language_code="zh-TW",
        enable_automatic_punctuation=True,
        model="latest_long"
    )

    try:
        async for audio_chunk in websocket.iter_bytes():
            # 送入語音辨識
            response = await speech_client.recognize(audio_chunk, streaming_config)

            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                is_final = response.results[0].is_final

                # 取得時間戳記
                timestamp = get_current_meeting_time(meeting)

                # 回傳轉錄結果
                await websocket.send_json({
                    "type": "transcript",
                    "timestamp": timestamp,
                    "text": transcript,
                    "confidence": confidence,
                    "is_final": is_final
                })

                # 如果是最終結果，儲存到資料庫
                if is_final:
                    await db.save_transcript(course_id, timestamp, transcript, confidence)

    except WebSocketDisconnect:
        print(f"Client disconnected: {meeting}")
```

### 4.3 講義與語音同步分析

```python
async def analyze_course_content(course_id: str):
    # 1. 取得講義和語音資料
    slides = await db.get_slides(course_id)
    transcript = await db.get_transcript(course_id)

    # 2. 建構 prompt
    prompt = f"""
    分析以下課程內容，找出講義與語音的對應關係。

    講義內容（依頁碼）：
    {format_slides(slides)}

    語音轉錄（含時間戳記）：
    {format_transcript(transcript)}

    請完成以下任務：
    1. 找出老師在講義中特別強調的段落（語音中重複提及、停頓、語氣加重）
    2. 整理講義未提及但老師口頭補充的重點
    3. 建立講義頁碼與語音時間點的對照表

    回傳 JSON 格式...
    """

    # 3. 呼叫 LLM
    analysis = await llm_client.generate(prompt)

    # 4. 產生重點摘要
    summary = {
        "key_points": [],
        "emphasized_parts": [],  # 老師強調的部分
        "supplementary_content": [],  # 口頭補充內容
        "slide_timestamp_mapping": {}  # 頁碼與時間點對照
    }

    return summary
```

### 4.4 簡答題批改邏輯

```python
async def grade_short_answer(question: Question, user_answer: str):
    prompt = f"""
    請批改以下簡答題。

    題目：{question.question_text}
    標準答案：{question.model_answer}
    評分標準：{question.evaluation_criteria}
    學生答案：{user_answer}

    請評估：
    1. 答案是否涵蓋關鍵概念
    2. 邏輯是否清晰
    3. 是否有錯誤或不完整的地方

    請給予：
    - 分數（0-100）
    - 詳細回饋
    - 改進建議

    回傳 JSON 格式...
    """

    grading_result = await llm_client.generate(prompt)

    return {
        "score": grading_result.score,
        "feedback": grading_result.feedback,
        "improvement_suggestions": grading_result.suggestions
    }
```

---

## 5. 資料結構定義

### 5.1 資料庫 Schema

```sql
-- 課程表
CREATE TABLE courses (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    meeting_id VARCHAR(100) UNIQUE,
    meeting_url VARCHAR(255),
    course_name VARCHAR(255),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(20), -- 'recording', 'processing', 'completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 講義檔案表
CREATE TABLE slides (
    id VARCHAR(50) PRIMARY KEY,
    course_id VARCHAR(50) REFERENCES courses(id),
    filename VARCHAR(255),
    file_path VARCHAR(500),
    total_pages INT,
    extracted_text TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 語音轉錄表
CREATE TABLE transcripts (
    id SERIAL PRIMARY KEY,
    course_id VARCHAR(50) REFERENCES courses(id),
    timestamp VARCHAR(20), -- HH:MM:SS
    text TEXT,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 課程摘要表
CREATE TABLE course_summaries (
    id VARCHAR(50) PRIMARY KEY,
    course_id VARCHAR(50) UNIQUE REFERENCES courses(id),
    summary_json JSONB, -- 包含 key_points, concepts, formulas
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 題庫表
CREATE TABLE quizzes (
    id VARCHAR(50) PRIMARY KEY,
    course_id VARCHAR(50) REFERENCES courses(id),
    scope_id VARCHAR(50),
    questions_json JSONB, -- 題目列表
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 作答紀錄表
CREATE TABLE quiz_submissions (
    id VARCHAR(50) PRIMARY KEY,
    quiz_id VARCHAR(50) REFERENCES quizzes(id),
    user_id VARCHAR(50),
    answers_json JSONB,
    results_json JSONB, -- 批改結果
    score INT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 使用者統計表
CREATE TABLE user_stats (
    user_id VARCHAR(50) PRIMARY KEY,
    total_courses INT DEFAULT 0,
    total_quizzes_taken INT DEFAULT 0,
    average_score FLOAT DEFAULT 0,
    weak_concepts JSONB, -- 弱項概念列表
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 TypeScript 型別定義

```typescript
// 課程
interface Course {
  id: string;
  userId: string;
  meetingId: string;
  meetingUrl: string;
  courseName: string;
  startedAt: string;
  endedAt: string | null;
  status: 'recording' | 'processing' | 'completed';
}

// 講義
interface Slides {
  id: string;
  courseId: string;
  filename: string;
  totalPages: number;
  extractedText: string;
}

// 轉錄項目
interface TranscriptItem {
  timestamp: string; // "HH:MM:SS"
  text: string;
  confidence: number;
}

// 課程摘要
interface CourseSummary {
  keyPoints: KeyPoint[];
  concepts: string[];
  formulas: string[];
}

interface KeyPoint {
  title: string;
  content: string;
  slidePage: number | null;
  transcriptTimestamps: string[];
}

// 題目範圍建議
interface QuizScope {
  scopeId: string;
  label: string;
  description: string;
  slidePages?: number[];
  transcriptTimestamps?: string[];
  estimatedQuestions: number;
}

// 題目
interface Question {
  questionId: string;
  type: 'multiple_choice' | 'fill_in_blank' | 'short_answer';
  questionText: string;
  options?: string[]; // 選擇題選項
  correctAnswer: string;
  explanation: string;
  slideReference: number | null;
  videoTimestamp: string | null;
  difficulty: 'easy' | 'medium' | 'hard';
}

// 測驗
interface Quiz {
  quizId: string;
  courseId: string;
  scopeId: string;
  questions: Question[];
  createdAt: string;
}

// 作答結果
interface QuizResult {
  questionId: string;
  isCorrect: boolean;
  userAnswer: string;
  score?: number; // 簡答題分數
  feedback: string;
  improvementSuggestions?: string[];
}
```

---

## 6. 開發階段規劃

### 6.1 MVP (Minimum Viable Product) - 第一階段

**目標：** 完成核心功能，能夠完整走完一次流程

**功能範圍：**
1. Chrome 外掛基本架構
2. 側邊欄 UI（簡化版）
3. 講義上傳（僅支援 PDF）
4. 即時語音轉錄（使用 Google Speech-to-Text）
5. 課程重點生成（使用 GPT OSS120B）
6. 題目生成（僅選擇題，固定出 5 題）
7. 簡易批改功能

**不包含：**
- Meet 介面變更偵測
- 錯題集
- 學習統計
- 題目範圍建議（直接出整堂課的題目）

**預估時間：** 2 週

### 6.2 第二階段：完整功能

**新增功能：**
1. 題目範圍建議（呼叫 suggest-quiz-scopes API）
2. 支援填充題、簡答題
3. 簡答題 LLM 批改
4. 講義與語音同步分析
5. 時間軸對照（點擊重點跳轉錄影）
6. 錯題集功能
7. 學習統計與弱項分析

**預估時間：** 1.5 週

### 6.3 第三階段：優化與擴充

**優化項目：**
1. Meet 介面變更容錯機制
2. WebSocket 斷線重連
3. 音訊品質優化（降噪、緩衝）
4. LLM prompt 優化（提升準確度）
5. UI/UX 改進

**擴充功能：**
1. 支援 Word、PPT 講義
2. 多份講義整合
3. 題庫匯出功能
4. 分享功能

**預估時間：** 1 週

---

## 附錄

### A. LLM Prompt 範例

**題目生成 Prompt：**

```
你是一位專業的教育工作者，需要根據以下課程內容產生測驗題目。

課程主題：{course_name}
內容範圍：{scope_description}

講義內容：
{slides_text}

課堂語音轉錄（含時間戳記）：
{transcript_with_timestamps}

請產生以下題目：
- 選擇題：5 題（單選，4 個選項）
- 填充題：3 題
- 簡答題：2 題

要求：
1. 題目需涵蓋課程的核心概念
2. 難度分布：簡單 3 題、中等 5 題、困難 2 題
3. 每題需標註對應的講義頁碼和錄影時間點
4. 提供詳細的解析說明

請以以下 JSON 格式回傳：
{
  "questions": [
    {
      "type": "multiple_choice",
      "question_text": "題目文字",
      "options": ["選項A", "選項B", "選項C", "選項D"],
      "correct_answer": "選項A",
      "explanation": "詳細解析",
      "slide_reference": 3,
      "video_timestamp": "00:05:23",
      "difficulty": "easy"
    },
    ...
  ]
}
```

### B. 錯誤處理

**前端錯誤處理：**
- WebSocket 斷線：自動重連（最多 3 次）
- API 呼叫失敗：顯示友善錯誤訊息，提供重試按鈕
- 權限被拒：引導使用者重新授權

**後端錯誤處理：**
- LLM API 超時：設定 timeout 60 秒，超時回傳錯誤
- 語音辨識失敗：記錄錯誤，繼續處理後續音訊
- 資料庫連線失敗：使用連線池，自動重試

### C. 效能優化

**前端優化：**
- 音訊資料分批傳送（每 1 秒傳一次）
- 轉錄文字使用虛擬滾動
- React 元件使用 memo 避免不必要的重渲染

**後端優化：**
- 使用 Redis 快取課程摘要
- LLM 回應使用 streaming（即時顯示部分結果）
- 題目生成使用背景任務（Celery）

---

**文件版本記錄：**
- v1.0 (2024-11-17): 初版，定義核心架構與 API
