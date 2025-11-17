/**
 * API 呼叫封裝
 */
import type {
  Course,
  CourseSummary,
  QuizScope,
  Quiz,
  QuizResult,
  TeacherHint,
  Answer,
} from './types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * 建立新課程
   */
  async createCourse(data: {
    meetingId: string;
    meetingUrl: string;
    courseName: string;
    startedAt: string;
  }): Promise<{ courseId: string; status: string; createdAt: string }> {
    const response = await fetch(`${this.baseUrl}/courses/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        meeting_id: data.meetingId,
        meeting_url: data.meetingUrl,
        course_name: data.courseName,
        started_at: data.startedAt,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create course: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      courseId: result.course_id,
      status: result.status,
      createdAt: result.created_at,
    };
  }

  /**
   * 取得課程資訊
   */
  async getCourse(courseId: string): Promise<Course> {
    const response = await fetch(`${this.baseUrl}/courses/${courseId}`);

    if (!response.ok) {
      throw new Error(`Failed to get course: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * 結束課程
   */
  async endCourse(courseId: string): Promise<{ status: string; endedAt: string }> {
    const response = await fetch(`${this.baseUrl}/courses/${courseId}/end`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ended_at: new Date().toISOString(),
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to end course: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      status: result.status,
      endedAt: result.ended_at,
    };
  }

  /**
   * 上傳講義
   */
  async uploadSlides(
    courseId: string,
    file: File
  ): Promise<{
    fileId: string;
    filename: string;
    pages: number;
    extractedTextPreview: string;
  }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${this.baseUrl}/courses/${courseId}/upload-slides`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to upload slides: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      fileId: result.file_id,
      filename: result.filename,
      pages: result.pages,
      extractedTextPreview: result.extracted_text_preview,
    };
  }

  /**
   * 分析課程內容
   */
  async analyzeCourse(
    courseId: string,
    options: { includeSlides?: boolean; includeTranscript?: boolean } = {}
  ): Promise<{ summary: CourseSummary; status: string }> {
    const response = await fetch(`${this.baseUrl}/courses/${courseId}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        include_slides: options.includeSlides ?? true,
        include_transcript: options.includeTranscript ?? true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to analyze course: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * 建議題目生成範圍
   */
  async suggestQuizScopes(courseId: string): Promise<{
    suggestedScopes: QuizScope[];
    defaultScope: string;
    recommendation?: string;
  }> {
    const response = await fetch(
      `${this.baseUrl}/courses/${courseId}/suggest-quiz-scopes`,
      { method: 'POST' }
    );

    if (!response.ok) {
      throw new Error(`Failed to suggest quiz scopes: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      suggestedScopes: result.suggested_scopes,
      defaultScope: result.default_scope,
      recommendation: result.recommendation,
    };
  }

  /**
   * 生成題目
   */
  async generateQuiz(data: {
    courseId: string;
    scopeId: string;
    questionTypes: {
      multipleChoice: number;
      fillInBlank: number;
      shortAnswer: number;
    };
    difficulty: 'easy' | 'medium' | 'hard';
  }): Promise<Quiz> {
    const response = await fetch(`${this.baseUrl}/quizzes/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        course_id: data.courseId,
        scope_id: data.scopeId,
        question_types: {
          multiple_choice: data.questionTypes.multipleChoice,
          fill_in_blank: data.questionTypes.fillInBlank,
          short_answer: data.questionTypes.shortAnswer,
        },
        difficulty: data.difficulty,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate quiz: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      quizId: result.quiz_id,
      courseId: data.courseId,
      scopeId: data.scopeId,
      questions: result.questions,
      createdAt: result.created_at,
    };
  }

  /**
   * 提交答案
   */
  async submitQuiz(
    quizId: string,
    answers: Answer[]
  ): Promise<{ submissionId: string; status: string; estimatedTime: string }> {
    const response = await fetch(`${this.baseUrl}/quizzes/${quizId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit quiz: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      submissionId: result.submission_id,
      status: result.status,
      estimatedTime: result.estimated_time,
    };
  }

  /**
   * 取得批改結果
   */
  async getQuizResult(
    quizId: string,
    submissionId: string
  ): Promise<{
    results: QuizResult[];
    score: number;
    weakConcepts: string[];
  }> {
    const response = await fetch(
      `${this.baseUrl}/quizzes/${quizId}/result?submission_id=${submissionId}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get quiz result: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      results: result.results,
      score: result.score,
      weakConcepts: result.weak_concepts,
    };
  }

  /**
   * 取得老師提示列表
   */
  async getTeacherHints(
    courseId: string,
    options: { hintType?: string; limit?: number } = {}
  ): Promise<{ hints: TeacherHint[]; total: number; byType: Record<string, number> }> {
    const params = new URLSearchParams();
    if (options.hintType) params.append('hint_type', options.hintType);
    if (options.limit) params.append('limit', options.limit.toString());

    const response = await fetch(
      `${this.baseUrl}/teacher-hints/${courseId}?${params.toString()}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get teacher hints: ${response.statusText}`);
    }

    const result = await response.json();
    return {
      hints: result.hints,
      total: result.total,
      byType: result.by_type,
    };
  }

  /**
   * 建立 WebSocket 連線 (用於即時轉錄)
   */
  connectWebSocket(courseId: string): WebSocket {
    const wsUrl = this.baseUrl.replace('http', 'ws');
    return new WebSocket(`${wsUrl}/transcripts/ws/${courseId}`);
  }
}

// 匯出單例
export const apiClient = new ApiClient();
export default apiClient;
