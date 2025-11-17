/**
 * Content Script - 注入到 Google Meet 頁面
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import Sidebar from './Sidebar';
import './styles.css';

console.log('CourseAI: Content script loaded');

/**
 * 偵測 Google Meet 頁面並注入側邊欄
 */
function injectSidebar() {
  // 等待 Meet 頁面載入
  const observer = new MutationObserver(() => {
    // 檢查是否在會議中
    const meetContainer = document.querySelector('[data-meeting-state]');

    if (meetContainer && !document.getElementById('courseai-sidebar')) {
      console.log('CourseAI: Injecting sidebar');
      createSidebar();
      observer.disconnect();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  // 如果頁面已經載入完成，直接注入
  setTimeout(() => {
    const meetContainer = document.querySelector('[data-meeting-state]');
    if (meetContainer && !document.getElementById('courseai-sidebar')) {
      createSidebar();
    }
  }, 2000);
}

/**
 * 建立側邊欄元素
 */
function createSidebar() {
  // 建立容器
  const container = document.createElement('div');
  container.id = 'courseai-sidebar';
  container.className = 'courseai-sidebar-container';

  // 插入到頁面
  document.body.appendChild(container);

  // 取得當前會議 ID
  const meetingId = getMeetingId();
  console.log('CourseAI: Meeting ID:', meetingId);

  // 渲染 React 元件
  const root = ReactDOM.createRoot(container);
  root.render(
    <React.StrictMode>
      <Sidebar meetingId={meetingId} />
    </React.StrictMode>
  );
}

/**
 * 取得當前會議 ID
 */
function getMeetingId(): string | null {
  const url = new URL(window.location.href);
  const pathParts = url.pathname.split('/');
  return pathParts[pathParts.length - 1] || null;
}

/**
 * 偵測會議狀態
 */
function detectMeetingStatus(): 'started' | 'ended' | 'idle' {
  // Google Meet 的按鈕選擇器可能會變動，需要定期更新
  const leaveButton = document.querySelector('[data-tooltip*="離開"]') ||
                     document.querySelector('[aria-label*="Leave"]');

  if (leaveButton) return 'started';

  const joinButton = document.querySelector('[data-tooltip*="加入"]') ||
                    document.querySelector('[aria-label*="Join"]');

  if (joinButton) return 'idle';

  return 'ended';
}

// 初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', injectSidebar);
} else {
  injectSidebar();
}

// 監聽頁面變化
window.addEventListener('popstate', () => {
  const status = detectMeetingStatus();
  console.log('CourseAI: Meeting status changed:', status);
});
