export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  profile_picture?: string
  bio?: string
  is_verified: boolean
  created_at: string
}

export interface Video {
  id: number
  user: number
  title: string
  description: string
  video_file: string
  thumbnail?: string
  duration?: string
  file_size?: number
  status: 'uploading' | 'processing' | 'ready' | 'failed'
  transcription?: string
  tags: Tag[]
  is_public: boolean
  created_at: string
  updated_at: string
}

export interface Tag {
  id: number
  name: string
  created_at: string
}

export interface SocialAccount {
  id: number
  provider: 'google' | 'instagram' | 'youtube' | 'twitter' | 'tiktok'
  social_id: string
  is_active: boolean
  created_at: string
}

export interface VideoProcessingTask {
  id: number
  video: number
  task_type: 'transcription' | 'thumbnail_generation' | 'video_compression' | 'content_analysis'
  status: string
  result?: any
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface YouTubeDownload {
  id: number
  youtube_url: string
  video?: number
  status: string
  error_message?: string
  created_at: string
}

export interface ApiResponse<T> {
  results: T[]
  count: number
  next?: string
  previous?: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  first_name: string
  last_name: string
  password: string
  password_confirm: string
}

export interface VideoUpload {
  title: string
  description?: string
  video_file: File
  is_public?: boolean
}

export interface SocialUploadData {
  video_id: number
  platforms: string[]
  caption?: string
  schedule_date?: string
}
