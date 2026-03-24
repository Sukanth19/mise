export interface User {
  id: number;
  username: string;
}

export interface Recipe {
  id: number;
  user_id: number;
  title: string;
  image_url?: string;
  ingredients: string[];
  steps: string[];
  tags?: string[];
  reference_link?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RecipeCreate {
  title: string;
  image_url?: string;
  ingredients: string[];
  steps: string[];
  tags?: string[];
  reference_link?: string;
}

export interface RecipeUpdate {
  title?: string;
  image_url?: string;
  ingredients?: string[];
  steps?: string[];
  tags?: string[];
  reference_link?: string;
}

export interface ImageUploadResponse {
  url: string;
}

export interface Rating {
  id: number;
  recipe_id: number;
  user_id: number;
  rating: number;
  created_at: string;
  updated_at: string;
}

export interface RatingCreate {
  rating: number;
}
