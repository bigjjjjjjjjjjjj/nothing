/**
 * Background Service Worker
 */

console.log('CourseAI: Background service worker started');

// 監聽外掛安裝
chrome.runtime.onInstalled.addListener((details) => {
  console.log('CourseAI: Extension installed', details.reason);

  if (details.reason === 'install') {
    // 首次安裝時的初始化
    chrome.storage.local.set({
      settings: {
        autoStart: false,
        apiUrl: 'http://localhost:8000/api/v1',
      },
    });

    // 開啟歡迎頁面
    chrome.tabs.create({
      url: chrome.runtime.getURL('popup.html'),
    });
  }
});

// 監聽來自 content script 的訊息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('CourseAI: Received message', message);

  switch (message.type) {
    case 'GET_MEETING_ID':
      handleGetMeetingId(sender.tab?.id, sendResponse);
      return true; // 保持訊息通道開啟

    case 'SAVE_COURSE':
      handleSaveCourse(message.data, sendResponse);
      return true;

    case 'GET_STORAGE':
      handleGetStorage(message.key, sendResponse);
      return true;

    case 'START_TAB_CAPTURE':
      handleStartTabCapture(sender.tab?.id, sendResponse);
      return true;

    default:
      sendResponse({ error: 'Unknown message type' });
  }
});

/**
 * 處理取得會議 ID
 */
async function handleGetMeetingId(tabId: number | undefined, sendResponse: (response: any) => void) {
  if (!tabId) {
    sendResponse({ error: 'No tab ID' });
    return;
  }

  try {
    const tab = await chrome.tabs.get(tabId);
    const url = new URL(tab.url || '');
    const meetingId = url.pathname.split('/').pop();

    sendResponse({ meetingId });
  } catch (error) {
    sendResponse({ error: String(error) });
  }
}

/**
 * 處理儲存課程資料
 */
async function handleSaveCourse(data: any, sendResponse: (response: any) => void) {
  try {
    await chrome.storage.local.set({ currentCourse: data });
    sendResponse({ success: true });
  } catch (error) {
    sendResponse({ error: String(error) });
  }
}

/**
 * 處理取得儲存資料
 */
async function handleGetStorage(key: string, sendResponse: (response: any) => void) {
  try {
    const result = await chrome.storage.local.get(key);
    sendResponse({ data: result[key] });
  } catch (error) {
    sendResponse({ error: String(error) });
  }
}

/**
 * 處理開始擷取分頁音訊
 */
async function handleStartTabCapture(tabId: number | undefined, sendResponse: (response: any) => void) {
  if (!tabId) {
    sendResponse({ error: 'No tab ID' });
    return;
  }

  try {
    // 請求擷取分頁音訊
    chrome.tabCapture.capture(
      {
        audio: true,
        video: false,
      },
      (stream) => {
        if (chrome.runtime.lastError) {
          sendResponse({ error: chrome.runtime.lastError.message });
          return;
        }

        if (!stream) {
          sendResponse({ error: 'Failed to capture tab audio' });
          return;
        }

        // 成功擷取，返回 stream ID
        // 注意：實際上我們需要將 stream 傳遞回 content script
        // 這裡簡化處理，實際應用中可能需要更複雜的通訊機制
        sendResponse({ success: true });
      }
    );
  } catch (error) {
    sendResponse({ error: String(error) });
  }
}

// 監聽 tabs 更新
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url?.includes('meet.google.com')) {
    console.log('CourseAI: Google Meet page loaded');
  }
});

export {};
