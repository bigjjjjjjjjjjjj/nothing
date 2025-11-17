/**
 * 音訊擷取模組
 * 負責從 Google Meet 擷取音訊並透過 WebSocket 傳送到後端
 */

import { TranscriptItem } from '../shared/types';

export interface AudioCaptureOptions {
  courseId: string;
  wsUrl: string;
  onTranscript: (transcript: TranscriptItem) => void;
  onError: (error: Error) => void;
  onConnectionChange: (connected: boolean) => void;
}

export class AudioCapture {
  private mediaStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private websocket: WebSocket | null = null;
  private isCapturing: boolean = false;
  private options: AudioCaptureOptions;
  private reconnectAttempts: number = 0;
  private readonly MAX_RECONNECT_ATTEMPTS = 5;
  private readonly RECONNECT_DELAY = 2000;

  constructor(options: AudioCaptureOptions) {
    this.options = options;
  }

  /**
   * 開始擷取音訊
   */
  async startCapture(): Promise<void> {
    if (this.isCapturing) {
      console.warn('AudioCapture: Already capturing');
      return;
    }

    try {
      // 建立 WebSocket 連線
      await this.connectWebSocket();

      // 擷取音訊流
      await this.captureAudioStream();

      // 開始錄音
      this.startRecording();

      this.isCapturing = true;
      console.log('AudioCapture: Started successfully');
    } catch (error) {
      this.options.onError(error as Error);
      await this.cleanup();
      throw error;
    }
  }

  /**
   * 停止擷取音訊
   */
  async stopCapture(): Promise<void> {
    if (!this.isCapturing) {
      return;
    }

    console.log('AudioCapture: Stopping...');
    this.isCapturing = false;
    await this.cleanup();
  }

  /**
   * 建立 WebSocket 連線
   */
  private async connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.options.wsUrl}/${this.options.courseId}`;
      console.log('AudioCapture: Connecting to WebSocket:', wsUrl);

      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('AudioCapture: WebSocket connected');
        this.reconnectAttempts = 0;
        this.options.onConnectionChange(true);
        resolve();
      };

      this.websocket.onerror = (error) => {
        console.error('AudioCapture: WebSocket error:', error);
        reject(new Error('Failed to connect to transcription service'));
      };

      this.websocket.onclose = (event) => {
        console.log('AudioCapture: WebSocket closed:', event.code, event.reason);
        this.options.onConnectionChange(false);

        // 如果仍在擷取中，嘗試重新連線
        if (this.isCapturing && this.reconnectAttempts < this.MAX_RECONNECT_ATTEMPTS) {
          this.reconnectAttempts++;
          console.log(`AudioCapture: Reconnecting (${this.reconnectAttempts}/${this.MAX_RECONNECT_ATTEMPTS})...`);
          setTimeout(() => {
            this.connectWebSocket().catch((error) => {
              this.options.onError(error);
            });
          }, this.RECONNECT_DELAY * this.reconnectAttempts);
        }
      };

      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'transcript') {
            const transcript: TranscriptItem = {
              timestamp: data.timestamp,
              text: data.text,
              confidence: data.confidence,
              isFinal: data.is_final,
            };
            this.options.onTranscript(transcript);
          } else if (data.type === 'error') {
            this.options.onError(new Error(data.message));
          }
        } catch (error) {
          console.error('AudioCapture: Failed to parse WebSocket message:', error);
        }
      };
    });
  }

  /**
   * 擷取音訊流
   * 使用 getUserMedia 或 displayMedia API
   */
  private async captureAudioStream(): Promise<void> {
    try {
      // 方法 1: 嘗試擷取系統音訊（需要 Chrome 擴充功能權限）
      // 這需要在 background script 中處理，因為 content script 無法直接使用 chrome.tabCapture

      // 方法 2: 使用 displayMedia API 擷取分頁音訊
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          channelCount: 1,
          sampleRate: 16000,
        }
      });

      this.mediaStream = stream;
      console.log('AudioCapture: Audio stream captured');
    } catch (error) {
      console.error('AudioCapture: Failed to capture audio stream:', error);
      throw new Error('無法擷取音訊，請確認麥克風權限已授予');
    }
  }

  /**
   * 請求 tab capture（需要透過 background script）
   */
  private async requestTabCapture(): Promise<MediaStream> {
    return new Promise((resolve, reject) => {
      // 發送消息到 background script 請求 tab capture
      chrome.runtime.sendMessage(
        { action: 'startTabCapture' },
        (response) => {
          if (response.error) {
            reject(new Error(response.error));
          } else {
            // 透過 streamId 獲取 media stream
            navigator.mediaDevices.getUserMedia({
              audio: {
                mandatory: {
                  chromeMediaSource: 'tab',
                  chromeMediaSourceId: response.streamId,
                },
              } as any,
            })
            .then(resolve)
            .catch(reject);
          }
        }
      );
    });
  }

  /**
   * 開始錄音並傳送音訊
   */
  private startRecording(): void {
    if (!this.mediaStream) {
      throw new Error('No media stream available');
    }

    // 建立 AudioContext 進行音訊處理
    this.audioContext = new AudioContext({ sampleRate: 16000 });
    const source = this.audioContext.createMediaStreamSource(this.mediaStream);

    // 使用 MediaRecorder 錄製音訊
    const mimeType = this.getSupportedMimeType();
    this.mediaRecorder = new MediaRecorder(this.mediaStream, {
      mimeType,
      audioBitsPerSecond: 16000,
    });

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0 && this.websocket?.readyState === WebSocket.OPEN) {
        // 將音訊資料透過 WebSocket 傳送
        event.data.arrayBuffer().then((buffer) => {
          this.websocket?.send(buffer);
        });
      }
    };

    this.mediaRecorder.onerror = (error) => {
      console.error('AudioCapture: MediaRecorder error:', error);
      this.options.onError(new Error('錄音過程發生錯誤'));
    };

    // 每 250ms 送出一次音訊資料
    this.mediaRecorder.start(250);
    console.log('AudioCapture: Recording started');
  }

  /**
   * 取得支援的 MIME 類型
   */
  private getSupportedMimeType(): string {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        console.log('AudioCapture: Using MIME type:', type);
        return type;
      }
    }

    console.warn('AudioCapture: No preferred MIME type supported, using default');
    return '';
  }

  /**
   * 清理資源
   */
  private async cleanup(): Promise<void> {
    // 停止錄音
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
      this.mediaRecorder = null;
    }

    // 關閉音訊串流
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    // 關閉 AudioContext
    if (this.audioContext && this.audioContext.state !== 'closed') {
      await this.audioContext.close();
      this.audioContext = null;
    }

    // 關閉 WebSocket
    if (this.websocket && this.websocket.readyState !== WebSocket.CLOSED) {
      this.websocket.close();
      this.websocket = null;
    }

    console.log('AudioCapture: Cleanup completed');
  }

  /**
   * 檢查是否正在擷取
   */
  isActive(): boolean {
    return this.isCapturing;
  }

  /**
   * 檢查 WebSocket 連線狀態
   */
  isConnected(): boolean {
    return this.websocket?.readyState === WebSocket.OPEN;
  }
}

/**
 * 工廠函數：建立 AudioCapture 實例
 */
export function createAudioCapture(options: AudioCaptureOptions): AudioCapture {
  return new AudioCapture(options);
}
