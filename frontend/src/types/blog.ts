export enum MediaType {
  IMAGE = "image",
  VIDEO = "video"
}

export interface PostMedia {
  url: string;
  media_type: MediaType;
  width?: number;
  height?: number;
}

export interface PostCreateRequest {
  content: string;
  media?: PostMedia[];
  hashtags?: string[];
}

export interface MediaUploadResponse {
  url: string;
  file_id: string;
  file_name: string;
  media_type: MediaType;
  size_bytes: number;
}