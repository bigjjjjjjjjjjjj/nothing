/**
 * 側邊欄 UI 元件
 */
import React, { useState, useEffect } from 'react';
import { apiClient } from '../shared/api';
import type { TranscriptItem, TeacherHint } from '../shared/types';

interface SidebarProps {
  meetingId: string | null;
}

const Sidebar: React.FC<SidebarProps> = ({ meetingId }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [courseId, setCourseId] = useState<string | null>(null);
  const [transcripts, setTranscripts] = useState<TranscriptItem[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [teacherHints, setTeacherHints] = useState<TeacherHint[]>([]);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  // 初始化：建立課程
  useEffect(() => {
    if (meetingId && !courseId) {
      initializeCourse();
    }
  }, [meetingId]);

  const initializeCourse = async () => {
    try {
      const result = await apiClient.createCourse({
        meetingId: meetingId!,
        meetingUrl: window.location.href,
        courseName: `課程 ${new Date().toLocaleDateString()}`,
        startedAt: new Date().toISOString(),
      });

      setCourseId(result.courseId);
      console.log('CourseAI: Course created:', result.courseId);
    } catch (error) {
      console.error('Failed to create course:', error);
    }
  };

  // 開始/停止錄音
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = () => {
    if (!courseId) return;

    console.log('CourseAI: Starting recording');
    setIsRecording(true);

    // TODO: 實作音訊擷取和 WebSocket 連線
    // 這裡需要整合 audioCapture.ts
  };

  const stopRecording = () => {
    console.log('CourseAI: Stopping recording');
    setIsRecording(false);

    // TODO: 停止音訊擷取和關閉 WebSocket
  };

  // 處理檔案上傳
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !courseId) return;

    try {
      console.log('CourseAI: Uploading file:', file.name);
      const result = await apiClient.uploadSlides(courseId, file);
      setUploadedFile(file);
      console.log('CourseAI: File uploaded:', result);
      alert(`檔案上傳成功！${result.pages} 頁`);
    } catch (error) {
      console.error('Failed to upload file:', error);
      alert('檔案上傳失敗');
    }
  };

  // 生成課程重點
  const generateSummary = async () => {
    if (!courseId) return;

    try {
      console.log('CourseAI: Generating summary');
      const result = await apiClient.analyzeCourse(courseId);
      console.log('CourseAI: Summary generated:', result);
      alert('課程重點已生成！');
      // TODO: 顯示摘要內容
    } catch (error) {
      console.error('Failed to generate summary:', error);
      alert('生成重點失敗');
    }
  };

  // 生成試題
  const generateQuiz = async () => {
    if (!courseId) return;

    try {
      console.log('CourseAI: Generating quiz');
      const scopes = await apiClient.suggestQuizScopes(courseId);
      console.log('CourseAI: Quiz scopes:', scopes);

      // 使用第一個範圍生成題目
      const quiz = await apiClient.generateQuiz({
        courseId,
        scopeId: scopes.suggestedScopes[0].scopeId,
        questionTypes: {
          multipleChoice: 5,
          fillInBlank: 3,
          shortAnswer: 2,
        },
        difficulty: 'medium',
      });

      console.log('CourseAI: Quiz generated:', quiz);
      alert(`題目已生成！共 ${quiz.questions.length} 題`);
      // TODO: 開啟 Popup 顯示題目
    } catch (error) {
      console.error('Failed to generate quiz:', error);
      alert('生成試題失敗');
    }
  };

  if (!isOpen) {
    return (
      <div className="courseai-sidebar collapsed">
        <button
          className="courseai-toggle-btn"
          onClick={() => setIsOpen(true)}
          title="展開 CourseAI"
        >
          CourseAI
        </button>
      </div>
    );
  }

  return (
    <div className="courseai-sidebar open">
      <div className="courseai-header">
        <h3>CourseAI</h3>
        <button
          className="courseai-close-btn"
          onClick={() => setIsOpen(false)}
          title="收合"
        >
          ✕
        </button>
      </div>

      <div className="courseai-content">
        {/* 上傳講義 */}
        <section className="courseai-section">
          <h4>上傳講義</h4>
          <input
            type="file"
            accept=".pdf,.ppt,.pptx,.doc,.docx"
            onChange={handleFileUpload}
            className="courseai-file-input"
          />
          {uploadedFile && (
            <p className="courseai-file-name">{uploadedFile.name}</p>
          )}
        </section>

        {/* 即時轉錄 */}
        <section className="courseai-section">
          <h4>即時轉錄</h4>
          <button
            className={`courseai-btn ${isRecording ? 'recording' : ''}`}
            onClick={toggleRecording}
          >
            {isRecording ? '暫停錄音' : '開始錄音'}
          </button>

          <div className="courseai-transcripts">
            {transcripts.length === 0 ? (
              <p className="courseai-empty">點擊「開始錄音」開始轉錄</p>
            ) : (
              transcripts.map((item, index) => (
                <div key={index} className="courseai-transcript-item">
                  <span className="transcript-time">[{item.timestamp}]</span>
                  <p className="transcript-text">{item.text}</p>
                </div>
              ))
            )}
          </div>
        </section>

        {/* 老師重點提示 */}
        {teacherHints.length > 0 && (
          <section className="courseai-section">
            <h4>重點提示 ({teacherHints.length})</h4>
            <div className="courseai-hints">
              {teacherHints.map((hint) => (
                <div key={hint.id} className="courseai-hint-item">
                  <span className="hint-icon">
                    {hint.hintType === 'exam' ? '[重要]' : '[注意]'}
                  </span>
                  <span className="hint-time">[{hint.timestamp}]</span>
                  <p className="hint-text">{hint.hintText}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* 課後功能 */}
        <section className="courseai-section">
          <h4>課後功能</h4>
          <button className="courseai-btn" onClick={generateSummary}>
            生成課程重點
          </button>
          <button className="courseai-btn" onClick={generateQuiz}>
            生成試題
          </button>
        </section>
      </div>
    </div>
  );
};

export default Sidebar;
