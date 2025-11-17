/**
 * Popup 主應用
 */
import React, { useState, useEffect } from 'react';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'courses' | 'quizzes' | 'settings'>('courses');
  const [courses, setCourses] = useState<any[]>([]);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    // TODO: 從 storage 或 API 載入課程列表
    const result = await chrome.storage.local.get('courses');
    setCourses(result.courses || []);
  };

  return (
    <div className="popup-container">
      <header className="popup-header">
        <h1>CourseAI</h1>
        <p className="popup-subtitle">智慧學習助理</p>
      </header>

      <nav className="popup-nav">
        <button
          className={`nav-btn ${activeTab === 'courses' ? 'active' : ''}`}
          onClick={() => setActiveTab('courses')}
        >
          課程列表
        </button>
        <button
          className={`nav-btn ${activeTab === 'quizzes' ? 'active' : ''}`}
          onClick={() => setActiveTab('quizzes')}
        >
          題目練習
        </button>
        <button
          className={`nav-btn ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          設定
        </button>
      </nav>

      <main className="popup-content">
        {activeTab === 'courses' && <CoursesTab courses={courses} />}
        {activeTab === 'quizzes' && <QuizzesTab />}
        {activeTab === 'settings' && <SettingsTab />}
      </main>

      <footer className="popup-footer">
        <p>CourseAI v1.0.0</p>
      </footer>
    </div>
  );
};

// 課程列表頁籤
const CoursesTab: React.FC<{ courses: any[] }> = ({ courses }) => {
  if (courses.length === 0) {
    return (
      <div className="empty-state">
        <p>尚無課程記錄</p>
        <p className="hint">請在 Google Meet 課程中使用側邊欄開始記錄</p>
      </div>
    );
  }

  return (
    <div className="courses-list">
      {courses.map((course, index) => (
        <div key={index} className="course-item">
          <h3>{course.name}</h3>
          <p className="course-date">{new Date(course.date).toLocaleDateString()}</p>
          <button className="btn-small">查看詳情</button>
        </div>
      ))}
    </div>
  );
};

// 題目練習頁籤
const QuizzesTab: React.FC = () => {
  return (
    <div className="quizzes-container">
      <p className="info-text">請先在課程中生成題目</p>
      <button className="btn-primary">開始練習</button>
    </div>
  );
};

// 設定頁籤
const SettingsTab: React.FC = () => {
  const [apiUrl, setApiUrl] = useState('http://localhost:8000/api/v1');
  const [autoStart, setAutoStart] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    const result = await chrome.storage.local.get('settings');
    if (result.settings) {
      setApiUrl(result.settings.apiUrl || 'http://localhost:8000/api/v1');
      setAutoStart(result.settings.autoStart || false);
    }
  };

  const saveSettings = async () => {
    await chrome.storage.local.set({
      settings: { apiUrl, autoStart },
    });
    alert('設定已儲存！');
  };

  return (
    <div className="settings-container">
      <div className="setting-item">
        <label htmlFor="api-url">API 位址</label>
        <input
          id="api-url"
          type="text"
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          placeholder="http://localhost:8000/api/v1"
        />
      </div>

      <div className="setting-item">
        <label>
          <input
            type="checkbox"
            checked={autoStart}
            onChange={(e) => setAutoStart(e.target.checked)}
          />
          進入會議自動開始錄音
        </label>
      </div>

      <button className="btn-primary" onClick={saveSettings}>
        儲存設定
      </button>

      <div className="info-box">
        <h4>使用說明</h4>
        <ol>
          <li>加入 Google Meet 課程</li>
          <li>點擊右側側邊欄開始錄音</li>
          <li>上傳課程講義 (PDF/PPT/Word)</li>
          <li>課後生成重點與題目</li>
        </ol>
      </div>
    </div>
  );
};

export default App;
