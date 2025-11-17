/**
 * TypeScript 型別定義
 */

// 課程
export interface Course {
  id: string;
  userId: string;
  meetingId: string;
  meetingUrl: string;
  courseName: string;
  startedAt: string;
  endedAt: string | null;
  status: 'recording' | 'processing' | 'completed';
}

// 轉錄項目
export interface TranscriptItem {
  timestamp: string; // "HH:MM:SS"
  text: string;
  confidence: number;
  isFinal?: boolean;
}

// 講義
export interface Slide {
  id: string;
  courseId: string;
  filename: string;
  totalPages: number;
  extractedText: string;
}

// 重點項目
export interface KeyPoint {
  title: string;
  content: string;
  slidePage: number | null;
  transcriptTimestamps: string[];
}

// 課程摘要
export interface CourseSummary {
  keyPoints: KeyPoint[];
  concepts: string[];
  formulas: string[];
}

// 題目範圍
export interface QuizScope {
  scopeId: string;
  label: string;
  description: string;
  slidePages?: number[];
  transcriptTimestamps?: string[];
  estimatedQuestions: number;
  coverage: 'all' | 'section' | 'subsection' | 'important';
  teacherHints?: TeacherHintInScope[];
}

// 範圍內的老師提示
export interface TeacherHintInScope {
  timestamp: string;
  hintText: string;
  relatedConcept: string;
  slidePage: number | null;
}

// 題目
export interface Question {
  questionId: string;
  type: 'multiple_choice' | 'fill_in_blank' | 'short_answer';
  questionText: string;
  options?: string[];
  correctAnswer: string;
  explanation: string;
  slideReference: number | null;
  videoTimestamp: string | null;
  difficulty: 'easy' | 'medium' | 'hard';
}

// 測驗
export interface Quiz {
  quizId: string;
  courseId: string;
  scopeId: string;
  questions: Question[];
  createdAt: string;
}

// 答案
export interface Answer {
  questionId: string;
  userAnswer: string;
}

// 批改結果
export interface QuizResult {
  questionId: string;
  isCorrect: boolean;
  userAnswer: string;
  score?: number;
  feedback: string;
  improvementSuggestions?: string[];
}

// 老師提示
export interface TeacherHint {
  id: number;
  timestamp: string;
  hintText: string;
  hintType: 'exam' | 'important' | 'attention' | 'common_mistake' | 'reminder';
  relatedConcept: string | null;
  slidePage: number | null;
  confidence: number;
  videoUrl?: string;
}

// 側邊欄狀態
export interface SidebarState {
  isOpen: boolean;
  currentCourseId: string | null;
  transcription: TranscriptItem[];
  isRecording: boolean;
  uploadedFile: File | null;
  summary: CourseSummary | null;
  quizzes: Quiz[] | null;
  teacherHints: TeacherHint[];
}

// API 響應
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}
