from typing import Optional, List, Tuple
from bson import ObjectId
import json
import qrcode
from io import BytesIO
import httpx
from bs4 import BeautifulSoup

from app.repositories.recipe_repository import RecipeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.recipe_like_repository import RecipeLikeRepository
from app.repositories.recipe_comment_repository import RecipeCommentRepository
from app.repositories.user_follow_repository import UserFollowRepository


class SharingService:
    """Service for managing recipe sharing and social features."""
    
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        user_repository: UserRepository,
        like_repository: RecipeLikeRepository,
        comment_repository: RecipeCommentRepository,
        follow_repository: UserFollowRepository
    ):
        """
        Initialize sharing service with repositories.
        
        Args:
            recipe_repository: RecipeRepository instance
            user_repository: UserRepository instance
            like_repository: RecipeLikeRepository instance
            comment_repository: RecipeCommentRepository instance
            follow_repository: UserFollowRepository instance
        """
        self.recipe_repo = recipe_repository
        self.user_repo = user_repository
        self.like_repo = like_repository
        self.comment_repo = comment_repository
        self.follow_repo = follow_repository
    
    # ========================================================================
    # Recipe Visibility and Discovery (Subtask 18.1)
    # ========================================================================
    
    async def set_recipe_visibility(
        self, 
        recipe_id: str, 
        visibility: str, 
        user_id: str
    ) -> Optional[dict]:
        """
        Set recipe visibility (private, public, unlisted).
        Returns None if recipe doesn't exist or user doesn't own it.
        Requirements: 29.1, 29.2, 29.3, 29.4
        """
        # Validate visibility value
        if visibility not in ('private', 'public', 'unlisted'):
            return None
        
        # Validate ObjectIds
        if not ObjectId.is_valid(recipe_id) or not ObjectId.is_valid(user_id):
            return None
        
        # Get recipe and verify ownership
        recipe = await self.recipe_repo.find_by_id(recipe_id)
        
        if not recipe or str(recipe.get('user_id')) != user_id:
            return None
        
        # Update visibility
        update_data = {"visibility": visibility}
        success = await self.recipe_repo.update(recipe_id, update_data)
        
        if not success:
            return None
        
        # Return updated recipe
        return await self.recipe_repo.find_by_id(recipe_id)
    
    async def get_public_recipes(
        self, 
        page: int = 1, 
        limit: int = 20, 
        search: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        """
        Get paginated list of public recipes ordered by created_at desc.
        Returns (recipes, total_count).
        Requirements: 29.2, 30.1, 30.2, 30.3
        """
        skip = (page - 1) * limit
        
        # Apply search filter if provided
        if search:
            # Use text search
            recipes = await self.recipe_repo.search(
                search_text=search,
                filters={"visibility": "public"},
                skip=skip,
                limit=limit
            )
        else:
            # Get public recipes with filters
            recipes = await self.recipe_repo.find_with_filters(
                visibility="public",
                skip=skip,
                limit=limit
            )
        
        # Get total count
        total = await self.recipe_repo.count({"visibility": "public"})
        
        return recipes, total
    
    async def get_public_recipe_by_id(self, recipe_id: str) -> Optional[dict]:
        """
        Get public recipe by ID with author info, likes count, and comments.
        Returns None if recipe doesn't exist or is not public/unlisted.
        Requirements: 29.3, 30.1, 30.2, 30.3
        """
        # Validate ObjectId
        if not ObjectId.is_valid(recipe_id):
            return None
        
        # Get recipe (must be public or unlisted)
        recipe = await self.recipe_repo.find_by_id(recipe_id)
        
        if not recipe or recipe.get('visibility') not in ['public', 'unlisted']:
            return None
        
        # Get author
        author = await self.user_repo.find_by_id(str(recipe.get('user_id')))
        
        # Get likes count
        likes_count = await self.like_repo.count_likes(recipe_id)
        
        # Get comments
        comments = await self.comment_repo.find_by_recipe(recipe_id)
        
        return {
            'recipe': recipe,
            'author': author,
            'likes_count': likes_count,
            'comments': comments
        }
    
    # ========================================================================
    # Recipe Forking (Subtask 18.2)
    # ========================================================================
    
    async def fork_recipe(self, recipe_id: str, user_id: str) -> Optional[dict]:
        """
        Fork a public or unlisted recipe to user's collection.
        Returns None if recipe doesn't exist or is private.
        Requirements: 33.1, 33.2, 33.3, 33.4
        """
        # Validate ObjectIds
        if not ObjectId.is_valid(recipe_id) or not ObjectId.is_valid(user_id):
            return None
        
        # Get source recipe (must be public or unlisted)
        source_recipe = await self.recipe_repo.find_by_id(recipe_id)
        
        if not source_recipe or source_recipe.get('visibility') not in ['public', 'unlisted']:
            return None
        
        # Create forked recipe data
        forked_recipe_data = {
            'user_id': ObjectId(user_id),
            'title': source_recipe.get('title'),
            'image_url': source_recipe.get('image_url'),
            'ingredients': source_recipe.get('ingredients', []),
            'steps': source_recipe.get('steps', []),
            'tags': source_recipe.get('tags', []),
            'reference_link': source_recipe.get('reference_link'),
            'visibility': 'private',  # Forked recipes default to private
            'servings': source_recipe.get('servings', 1),
            'source_recipe_id': ObjectId(recipe_id),
            'source_author_id': source_recipe.get('user_id'),
            'is_favorite': False
        }
        
        # Copy nutrition facts if present
        if 'nutrition_facts' in source_recipe:
            forked_recipe_data['nutrition_facts'] = source_recipe['nutrition_facts']
        
        # Copy dietary labels and allergen warnings if present
        if 'dietary_labels' in source_recipe:
            forked_recipe_data['dietary_labels'] = source_recipe['dietary_labels']
        if 'allergen_warnings' in source_recipe:
            forked_recipe_data['allergen_warnings'] = source_recipe['allergen_warnings']
        
        # Create forked recipe
        forked_recipe_id = await self.recipe_repo.create(forked_recipe_data)
        
        # Return the created recipe
        return await self.recipe_repo.find_by_id(forked_recipe_id)
    
    # ========================================================================
    # Likes and Comments (Subtask 18.3)
    # ========================================================================
    
    async def like_recipe(self, recipe_id: str, user_id: str) -> Tuple[bool, int]:
        """
        Like a recipe. Returns (liked_status, likes_count).
        Requirements: 32.1, 32.2
        """
        # Validate ObjectIds
        if not ObjectId.is_valid(recipe_id) or not ObjectId.is_valid(user_id):
            return False, 0
        
        # Check if recipe exists
        recipe = await self.recipe_repo.find_by_id(recipe_id)
        if not recipe:
            return False, 0
        
        # Check if already liked
        already_liked = await self.like_repo.has_liked(user_id, recipe_id)
        
        if already_liked:
            # Already liked, return current status
            likes_count = await self.like_repo.count_likes(recipe_id)
            return True, likes_count
        
        # Create new like
        like_data = {
            'recipe_id': ObjectId(recipe_id),
            'user_id': ObjectId(user_id)
        }
        await self.like_repo.create(like_data)
        
        # Get updated likes count
        likes_count = await self.like_repo.count_likes(recipe_id)
        return True, likes_count
    
    async def unlike_recipe(self, recipe_id: str, user_id: str) -> Tuple[bool, int]:
        """
        Unlike a recipe. Returns (liked_status, likes_count).
        Requirements: 32.1, 32.2
        """
        # Validate ObjectIds
        if not ObjectId.is_valid(recipe_id) or not ObjectId.is_valid(user_id):
            return False, 0
        
        # Find and delete like
        likes = await self.like_repo.find_many({
            'recipe_id': ObjectId(recipe_id),
            'user_id': ObjectId(user_id)
        })
        
        if likes:
            like_id = str(likes[0]['_id'])
            await self.like_repo.delete(like_id)
        
        # Get updated likes count
        likes_count = await self.like_repo.count_likes(recipe_id)
        return False, likes_count
    
    async def add_comment(self, recipe_id: str, user_id: str, comment_text: str) -> Optional[dict]:
        """
        Add a comment to a recipe.
        Returns None if recipe doesn't exist.
        Requirements: 32.3, 32.4
        """
        # Validate ObjectIds
        if not ObjectId.is_valid(recipe_id) or not ObjectId.is_valid(user_id):
            return None
        
        # Check if recipe exists
        recipe = await self.recipe_repo.find_by_id(recipe_id)
        if not recipe:
            return None
        
        # Create comment
        comment_data = {
            'recipe_id': ObjectId(recipe_id),
            'user_id': ObjectId(user_id),
            'comment_text': comment_text
        }
        comment_id = await self.comment_repo.create(comment_data)
        
        # Return the created comment
        return await self.comment_repo.find_by_id(comment_id)
    
    async def get_recipe_comments(self, recipe_id: str) -> List[dict]:
        """
        Get all comments for a recipe ordered by created_at.
        Requirements: 32.3, 32.4
        """
        # Validate ObjectId
        if not ObjectId.is_valid(recipe_id):
            return []
        
        return await self.comment_repo.find_by_recipe(recipe_id)
    
    # ========================================================================
    # User Following (Subtask 18.4)
    # ========================================================================
    
    async def follow_user(self, follower_id: str, following_id: str) -> Tuple[bool, int]:
        """
        Follow a user. Returns (following_status, followers_count).
        Returns (False, 0) if trying to follow self.
        Requirements: 31.1, 31.2, 31.3, 31.4
        """
        # Validate ObjectIds
        if not ObjectId.is_valid(follower_id) or not ObjectId.is_valid(following_id):
            return False, 0
        
        # Validate not following self
        if follower_id == following_id:
            return False, 0
        
        # Check if user exists
        user = await self.user_repo.find_by_id(following_id)
        if not user:
            return False, 0
        
        # Check if already following
        already_following = await self.follow_repo.is_following(follower_id, following_id)
        
        if already_following:
            # Already following, return current status
            followers = await self.follow_repo.find_followers(following_id)
            return True, len(followers)
        
        # Create new follow
        follow_data = {
            'follower_id': ObjectId(follower_id),
            'following_id': ObjectId(following_id)
        }
        await self.follow_repo.create(follow_data)
        
        # Get updated followers count
        followers = await self.follow_repo.find_followers(following_id)
        return True, len(followers)
    
    async def unfollow_user(self, follower_id: str, following_id: str) -> Tuple[bool, int]:
        """
        Unfollow a user. Returns (following_status, followers_count).
        Requirements: 31.1, 31.2, 31.3, 31.4
        """
        # Validate ObjectIds
        if not ObjectId.is_valid(follower_id) or not ObjectId.is_valid(following_id):
            return False, 0
        
        # Find and delete follow
        follows = await self.follow_repo.find_many({
            'follower_id': ObjectId(follower_id),
            'following_id': ObjectId(following_id)
        })
        
        if follows:
            follow_id = str(follows[0]['_id'])
            await self.follow_repo.delete(follow_id)
        
        # Get updated followers count
        followers = await self.follow_repo.find_followers(following_id)
        return False, len(followers)
    
    async def get_followers(self, user_id: str) -> List[dict]:
        """
        Get list of users following the specified user.
        Requirements: 31.3, 31.4
        """
        # Validate ObjectId
        if not ObjectId.is_valid(user_id):
            return []
        
        # Get follower documents
        follow_docs = await self.follow_repo.find_followers(user_id)
        
        # Get user objects for each follower
        follower_ids = [str(doc['follower_id']) for doc in follow_docs]
        if not follower_ids:
            return []
        
        # Fetch all follower users
        users = []
        for follower_id in follower_ids:
            user = await self.user_repo.find_by_id(follower_id)
            if user:
                users.append(user)
        
        return users
    
    async def get_following(self, user_id: str) -> List[dict]:
        """
        Get list of users that the specified user is following.
        Requirements: 31.3, 31.4
        """
        # Validate ObjectId
        if not ObjectId.is_valid(user_id):
            return []
        
        # Get following documents
        follow_docs = await self.follow_repo.find_following(user_id)
        
        # Get user objects for each following
        following_ids = [str(doc['following_id']) for doc in follow_docs]
        if not following_ids:
            return []
        
        # Fetch all following users
        users = []
        for following_id in following_ids:
            user = await self.user_repo.find_by_id(following_id)
            if user:
                users.append(user)
        
        return users
    
    # ========================================================================
    # Recipe URL Import (Subtask 19.1)
    # ========================================================================
    
    async def import_recipe_from_url(self, url: str, user_id: str) -> Optional[dict]:
        """
        Import recipe from URL by parsing webpage content.
        Returns None if URL is invalid or recipe data cannot be extracted.
        Requirements: 34.1, 34.2, 34.3, 34.4
        """
        # Validate ObjectId
        if not ObjectId.is_valid(user_id):
            return None
        
        try:
            # Fetch webpage content
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract recipe data from schema.org structured data
            recipe_data = self._extract_recipe_from_schema(soup)
            
            # If schema extraction fails, try basic HTML parsing
            if not recipe_data:
                recipe_data = self._extract_recipe_from_html(soup)
            
            if not recipe_data:
                return None
            
            # Create recipe with extracted data
            new_recipe_data = {
                'user_id': ObjectId(user_id),
                'title': recipe_data.get('title', 'Imported Recipe'),
                'image_url': recipe_data.get('image_url'),
                'ingredients': recipe_data.get('ingredients', []),
                'steps': recipe_data.get('steps', []),
                'tags': recipe_data.get('tags', []),
                'reference_link': url,
                'visibility': 'private',
                'servings': recipe_data.get('servings', 1),
                'is_favorite': False
            }
            
            recipe_id = await self.recipe_repo.create(new_recipe_data)
            
            # Return the created recipe
            return await self.recipe_repo.find_by_id(recipe_id)
            
        except Exception as e:
            # Handle any errors gracefully
            print(f"Error importing recipe from URL: {e}")
            return None
    
    def _extract_recipe_from_schema(self, soup: BeautifulSoup) -> Optional[dict]:
        """Extract recipe data from schema.org JSON-LD structured data."""
        try:
            # Look for JSON-LD script tags
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle both single object and array of objects
                    if isinstance(data, list):
                        data = next((item for item in data if item.get('@type') == 'Recipe'), None)
                    
                    if data and data.get('@type') == 'Recipe':
                        # Extract recipe data
                        title = data.get('name', '')
                        
                        # Extract ingredients
                        ingredients = []
                        if 'recipeIngredient' in data:
                            ingredients = data['recipeIngredient']
                        elif 'ingredients' in data:
                            ingredients = data['ingredients']
                        
                        # Extract steps
                        steps = []
                        if 'recipeInstructions' in data:
                            instructions = data['recipeInstructions']
                            if isinstance(instructions, list):
                                for instruction in instructions:
                                    if isinstance(instruction, dict):
                                        steps.append(instruction.get('text', ''))
                                    else:
                                        steps.append(str(instruction))
                            elif isinstance(instructions, str):
                                steps = [instructions]
                        
                        # Extract image
                        image_url = None
                        if 'image' in data:
                            image = data['image']
                            if isinstance(image, list) and len(image) > 0:
                                image_url = image[0] if isinstance(image[0], str) else image[0].get('url')
                            elif isinstance(image, dict):
                                image_url = image.get('url')
                            elif isinstance(image, str):
                                image_url = image
                        
                        # Extract servings
                        servings = 1
                        if 'recipeYield' in data:
                            yield_val = data['recipeYield']
                            if isinstance(yield_val, (int, float)):
                                servings = int(yield_val)
                            elif isinstance(yield_val, str):
                                # Try to extract number from string like "4 servings"
                                import re
                                match = re.search(r'\d+', yield_val)
                                if match:
                                    servings = int(match.group())
                        
                        if title and (ingredients or steps):
                            return {
                                'title': title,
                                'ingredients': ingredients,
                                'steps': steps,
                                'image_url': image_url,
                                'servings': servings
                            }
                except (json.JSONDecodeError, KeyError):
                    continue
            
            return None
        except Exception:
            return None
    
    def _extract_recipe_from_html(self, soup: BeautifulSoup) -> Optional[dict]:
        """Extract recipe data from HTML elements (fallback method)."""
        try:
            # Try to find title
            title = None
            title_elem = soup.find('h1')
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            # Try to find ingredients
            ingredients = []
            ingredient_lists = soup.find_all(['ul', 'ol'], class_=lambda x: x and 'ingredient' in x.lower())
            for ing_list in ingredient_lists:
                items = ing_list.find_all('li')
                ingredients.extend([item.get_text(strip=True) for item in items])
            
            # Try to find steps
            steps = []
            step_lists = soup.find_all(['ol', 'ul'], class_=lambda x: x and ('instruction' in x.lower() or 'step' in x.lower()))
            for step_list in step_lists:
                items = step_list.find_all('li')
                steps.extend([item.get_text(strip=True) for item in items])
            
            # Try to find image
            image_url = None
            img_elem = soup.find('img', class_=lambda x: x and ('recipe' in x.lower() or 'featured' in x.lower()))
            if img_elem and img_elem.get('src'):
                image_url = img_elem['src']
            
            if title and (ingredients or steps):
                return {
                    'title': title,
                    'ingredients': ingredients,
                    'steps': steps,
                    'image_url': image_url,
                    'servings': 1
                }
            
            return None
        except Exception:
            return None
    
    # ========================================================================
    # QR Code Generation (Subtask 19.2)
    # ========================================================================
    
    def generate_qr_code(self, recipe_url: str) -> bytes:
        """
        Generate QR code image for recipe URL.
        Returns PNG image bytes.
        Requirements: 36.1, 36.2, 36.3
        """
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(recipe_url)
        qr.make(fit=True)
        
        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()
    
    # ========================================================================
    # Social Media Share Metadata (Subtask 19.3)
    # ========================================================================
    
    async def get_share_metadata(self, recipe_id: str, base_url: str) -> Optional[dict]:
        """
        Get social media share metadata for a recipe.
        Returns metadata formatted for Open Graph and Twitter Cards.
        Requirements: 35.1, 35.2
        """
        # Validate ObjectId
        if not ObjectId.is_valid(recipe_id):
            return None
        
        # Get recipe
        recipe = await self.recipe_repo.find_by_id(recipe_id)
        if not recipe:
            return None
        
        # Get ingredients and steps
        ingredients = recipe.get('ingredients', [])
        steps = recipe.get('steps', [])
        
        # Create description from first few ingredients
        description = "Recipe with "
        if ingredients and len(ingredients) > 0:
            ingredient_preview = ingredients[:3]
            description += ", ".join(ingredient_preview)
            if len(ingredients) > 3:
                description += f" and {len(ingredients) - 3} more ingredients"
        else:
            description += f"{len(steps)} steps"
        
        # Build recipe URL
        recipe_url = f"{base_url}/recipes/{recipe_id}"
        if recipe.get('visibility') in ['public', 'unlisted']:
            recipe_url = f"{base_url}/recipes/public/{recipe_id}"
        
        return {
            'title': recipe.get('title'),
            'description': description,
            'image_url': recipe.get('image_url'),
            'url': recipe_url
        }
