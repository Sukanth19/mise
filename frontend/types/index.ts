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
  visibility?: 'private' | 'public' | 'unlisted';
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

export interface Collection {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  cover_image_url?: string;
  parent_collection_id?: number | null;
  nesting_level: number;
  share_token?: string;
  recipe_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CollectionCreate {
  name: string;
  description?: string;
  cover_image_url?: string;
  parent_collection_id?: number;
}

export interface CollectionUpdate {
  name?: string;
  description?: string;
  cover_image_url?: string;
}

export interface MealPlan {
  id: number;
  user_id: number;
  recipe_id: number;
  recipe?: Recipe;
  meal_date: string;
  meal_time: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  created_at: string;
}

export interface MealPlanCreate {
  recipe_id: number;
  meal_date: string;
  meal_time: 'breakfast' | 'lunch' | 'dinner' | 'snack';
}

export interface MealPlanUpdate {
  meal_date?: string;
  meal_time?: 'breakfast' | 'lunch' | 'dinner' | 'snack';
}

export interface MealPlanTemplate {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  items: MealPlanTemplateItem[];
  created_at: string;
}

export interface MealPlanTemplateItem {
  id: number;
  template_id: number;
  recipe_id: number;
  recipe?: Recipe;
  day_offset: number;
  meal_time: 'breakfast' | 'lunch' | 'dinner' | 'snack';
}

export interface TemplateCreate {
  name: string;
  description?: string;
  items: {
    recipe_id: number;
    day_offset: number;
    meal_time: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  }[];
}

export interface ShoppingList {
  id: number;
  user_id: number;
  name: string;
  share_token?: string;
  items?: ShoppingListItem[];
  created_at: string;
}

export interface ShoppingListItem {
  id: number;
  shopping_list_id: number;
  ingredient_name: string;
  quantity?: string;
  category: 'produce' | 'dairy' | 'meat' | 'pantry' | 'other';
  is_checked: boolean;
  is_custom: boolean;
  recipe_id?: number;
  created_at: string;
}

export interface ShoppingListCreate {
  name: string;
  recipe_ids?: number[];
  meal_plan_start_date?: string;
  meal_plan_end_date?: string;
}

export interface CustomItemCreate {
  ingredient_name: string;
  quantity?: string;
  category?: 'produce' | 'dairy' | 'meat' | 'pantry' | 'other';
}

export interface NutritionFacts {
  id: number;
  recipe_id: number;
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
  created_at: string;
  updated_at: string;
}

export interface NutritionCreate {
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
}

export interface NutritionUpdate {
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
}

export interface DietaryLabelsRequest {
  labels: string[];
}

export interface AllergensRequest {
  allergens: string[];
}

export interface DailyNutrition {
  date: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
}

export interface NutritionSummaryResponse {
  daily_totals: DailyNutrition[];
  weekly_total: NutritionFacts;
  missing_nutrition_count: number;
}

// Social Features Types
export interface PublicRecipe extends Recipe {
  author: User;
  likes_count: number;
  comments_count: number;
  visibility: 'private' | 'public' | 'unlisted';
}

export interface Comment {
  id: number;
  recipe_id: number;
  user_id: number;
  comment_text: string;
  created_at: string;
  author: User;
}

export interface CommentCreate {
  comment_text: string;
}

export interface ShareMetadata {
  title: string;
  description: string;
  image_url?: string;
  url: string;
}

export interface FollowResponse {
  following: boolean;
  followers_count: number;
}

export interface LikeResponse {
  liked: boolean;
  likes_count: number;
}

export interface UserFollowersResponse {
  followers: User[];
  count: number;
}

export interface UserFollowingResponse {
  following: User[];
  count: number;
}

export interface Note {
  id: number;
  recipe_id: number;
  user_id: number;
  note_text: string;
  created_at: string;
  updated_at: string;
}

export interface NoteCreate {
  note_text: string;
}
