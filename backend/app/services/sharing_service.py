from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Tuple
from app.models import Recipe, User, RecipeLike, RecipeComment, UserFollow
import json
import qrcode
from io import BytesIO
import httpx
from bs4 import BeautifulSoup


class SharingService:
    """Service for managing recipe sharing and social features."""
    
    # ========================================================================
    # Recipe Visibility and Discovery (Subtask 18.1)
    # ========================================================================
    
    @staticmethod
    def set_recipe_visibility(
        db: Session, 
        recipe_id: int, 
        visibility: str, 
        user_id: int
    ) -> Optional[Recipe]:
        """
        Set recipe visibility (private, public, unlisted).
        Returns None if recipe doesn't exist or user doesn't own it.
        Requirements: 29.1, 29.2, 29.3, 29.4
        """
        # Validate visibility value
        if visibility not in ('private', 'public', 'unlisted'):
            return None
        
        # Get recipe and verify ownership
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.user_id == user_id
        ).first()
        
        if not recipe:
            return None
        
        # Update visibility
        recipe.visibility = visibility
        db.commit()
        db.refresh(recipe)
        return recipe
    
    @staticmethod
    def get_public_recipes(
        db: Session, 
        page: int = 1, 
        limit: int = 20, 
        search: Optional[str] = None
    ) -> Tuple[List[Recipe], int]:
        """
        Get paginated list of public recipes ordered by created_at desc.
        Returns (recipes, total_count).
        Requirements: 29.2, 30.1, 30.2, 30.3
        """
        # Base query for public recipes only
        query = db.query(Recipe).filter(Recipe.visibility == 'public')
        
        # Apply search filter if provided
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Recipe.title.ilike(search_pattern))
        
        # Get total count
        total = query.count()
        
        # Apply ordering and pagination
        recipes = query.order_by(desc(Recipe.created_at)).offset((page - 1) * limit).limit(limit).all()
        
        return recipes, total
    
    @staticmethod
    def get_public_recipe_by_id(db: Session, recipe_id: int) -> Optional[dict]:
        """
        Get public recipe by ID with author info, likes count, and comments.
        Returns None if recipe doesn't exist or is not public/unlisted.
        Requirements: 29.3, 30.1, 30.2, 30.3
        """
        # Get recipe (must be public or unlisted)
        recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.visibility.in_(['public', 'unlisted'])
        ).first()
        
        if not recipe:
            return None
        
        # Get author
        author = db.query(User).filter(User.id == recipe.user_id).first()
        
        # Get likes count
        likes_count = db.query(RecipeLike).filter(RecipeLike.recipe_id == recipe_id).count()
        
        # Get comments
        comments = db.query(RecipeComment).filter(
            RecipeComment.recipe_id == recipe_id
        ).order_by(RecipeComment.created_at).all()
        
        return {
            'recipe': recipe,
            'author': author,
            'likes_count': likes_count,
            'comments': comments
        }
    
    # ========================================================================
    # Recipe Forking (Subtask 18.2)
    # ========================================================================
    
    @staticmethod
    def fork_recipe(db: Session, recipe_id: int, user_id: int) -> Optional[Recipe]:
        """
        Fork a public or unlisted recipe to user's collection.
        Returns None if recipe doesn't exist or is private.
        Requirements: 33.1, 33.2, 33.3, 33.4
        """
        # Get source recipe (must be public or unlisted)
        source_recipe = db.query(Recipe).filter(
            Recipe.id == recipe_id,
            Recipe.visibility.in_(['public', 'unlisted'])
        ).first()
        
        if not source_recipe:
            return None
        
        # Parse JSON fields
        ingredients = json.loads(source_recipe.ingredients) if isinstance(source_recipe.ingredients, str) else source_recipe.ingredients
        steps = json.loads(source_recipe.steps) if isinstance(source_recipe.steps, str) else source_recipe.steps
        tags = json.loads(source_recipe.tags) if source_recipe.tags and isinstance(source_recipe.tags, str) else source_recipe.tags
        
        # Create forked recipe
        forked_recipe = Recipe(
            user_id=user_id,
            title=source_recipe.title,
            image_url=source_recipe.image_url,
            ingredients=json.dumps(ingredients),
            steps=json.dumps(steps),
            tags=json.dumps(tags) if tags else None,
            reference_link=source_recipe.reference_link,
            visibility='private',  # Forked recipes default to private
            servings=source_recipe.servings,
            source_recipe_id=source_recipe.id,
            source_author_id=source_recipe.user_id,
            is_favorite=False
        )
        
        db.add(forked_recipe)
        db.commit()
        db.refresh(forked_recipe)
        return forked_recipe
    
    # ========================================================================
    # Likes and Comments (Subtask 18.3)
    # ========================================================================
    
    @staticmethod
    def like_recipe(db: Session, recipe_id: int, user_id: int) -> Tuple[bool, int]:
        """
        Like a recipe. Returns (liked_status, likes_count).
        Requirements: 32.1, 32.2
        """
        # Check if recipe exists
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return False, 0
        
        # Check if already liked
        existing_like = db.query(RecipeLike).filter(
            RecipeLike.recipe_id == recipe_id,
            RecipeLike.user_id == user_id
        ).first()
        
        if existing_like:
            # Already liked, return current status
            likes_count = db.query(RecipeLike).filter(RecipeLike.recipe_id == recipe_id).count()
            return True, likes_count
        
        # Create new like
        new_like = RecipeLike(
            recipe_id=recipe_id,
            user_id=user_id
        )
        db.add(new_like)
        db.commit()
        
        # Get updated likes count
        likes_count = db.query(RecipeLike).filter(RecipeLike.recipe_id == recipe_id).count()
        return True, likes_count
    
    @staticmethod
    def unlike_recipe(db: Session, recipe_id: int, user_id: int) -> Tuple[bool, int]:
        """
        Unlike a recipe. Returns (liked_status, likes_count).
        Requirements: 32.1, 32.2
        """
        # Find and delete like
        like = db.query(RecipeLike).filter(
            RecipeLike.recipe_id == recipe_id,
            RecipeLike.user_id == user_id
        ).first()
        
        if like:
            db.delete(like)
            db.commit()
        
        # Get updated likes count
        likes_count = db.query(RecipeLike).filter(RecipeLike.recipe_id == recipe_id).count()
        return False, likes_count
    
    @staticmethod
    def add_comment(db: Session, recipe_id: int, user_id: int, comment_text: str) -> Optional[RecipeComment]:
        """
        Add a comment to a recipe.
        Returns None if recipe doesn't exist.
        Requirements: 32.3, 32.4
        """
        # Check if recipe exists
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return None
        
        # Create comment
        comment = RecipeComment(
            recipe_id=recipe_id,
            user_id=user_id,
            comment_text=comment_text
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    
    @staticmethod
    def get_recipe_comments(db: Session, recipe_id: int) -> List[RecipeComment]:
        """
        Get all comments for a recipe ordered by created_at.
        Requirements: 32.3, 32.4
        """
        return db.query(RecipeComment).filter(
            RecipeComment.recipe_id == recipe_id
        ).order_by(RecipeComment.created_at).all()
    
    # ========================================================================
    # User Following (Subtask 18.4)
    # ========================================================================
    
    @staticmethod
    def follow_user(db: Session, follower_id: int, following_id: int) -> Tuple[bool, int]:
        """
        Follow a user. Returns (following_status, followers_count).
        Returns (False, 0) if trying to follow self.
        Requirements: 31.1, 31.2, 31.3, 31.4
        """
        # Validate not following self
        if follower_id == following_id:
            return False, 0
        
        # Check if user exists
        user = db.query(User).filter(User.id == following_id).first()
        if not user:
            return False, 0
        
        # Check if already following
        existing_follow = db.query(UserFollow).filter(
            UserFollow.follower_id == follower_id,
            UserFollow.following_id == following_id
        ).first()
        
        if existing_follow:
            # Already following, return current status
            followers_count = db.query(UserFollow).filter(
                UserFollow.following_id == following_id
            ).count()
            return True, followers_count
        
        # Create new follow
        new_follow = UserFollow(
            follower_id=follower_id,
            following_id=following_id
        )
        db.add(new_follow)
        db.commit()
        
        # Get updated followers count
        followers_count = db.query(UserFollow).filter(
            UserFollow.following_id == following_id
        ).count()
        return True, followers_count
    
    @staticmethod
    def unfollow_user(db: Session, follower_id: int, following_id: int) -> Tuple[bool, int]:
        """
        Unfollow a user. Returns (following_status, followers_count).
        Requirements: 31.1, 31.2, 31.3, 31.4
        """
        # Find and delete follow
        follow = db.query(UserFollow).filter(
            UserFollow.follower_id == follower_id,
            UserFollow.following_id == following_id
        ).first()
        
        if follow:
            db.delete(follow)
            db.commit()
        
        # Get updated followers count
        followers_count = db.query(UserFollow).filter(
            UserFollow.following_id == following_id
        ).count()
        return False, followers_count
    
    @staticmethod
    def get_followers(db: Session, user_id: int) -> List[User]:
        """
        Get list of users following the specified user.
        Requirements: 31.3, 31.4
        """
        # Get follower IDs
        follower_ids = db.query(UserFollow.follower_id).filter(
            UserFollow.following_id == user_id
        ).all()
        
        # Get user objects
        follower_ids = [fid[0] for fid in follower_ids]
        if not follower_ids:
            return []
        
        return db.query(User).filter(User.id.in_(follower_ids)).all()
    
    @staticmethod
    def get_following(db: Session, user_id: int) -> List[User]:
        """
        Get list of users that the specified user is following.
        Requirements: 31.3, 31.4
        """
        # Get following IDs
        following_ids = db.query(UserFollow.following_id).filter(
            UserFollow.follower_id == user_id
        ).all()
        
        # Get user objects
        following_ids = [fid[0] for fid in following_ids]
        if not following_ids:
            return []
        
        return db.query(User).filter(User.id.in_(following_ids)).all()
    
    # ========================================================================
    # Recipe URL Import (Subtask 19.1)
    # ========================================================================
    
    @staticmethod
    def import_recipe_from_url(db: Session, url: str, user_id: int) -> Optional[Recipe]:
        """
        Import recipe from URL by parsing webpage content.
        Returns None if URL is invalid or recipe data cannot be extracted.
        Requirements: 34.1, 34.2, 34.3, 34.4
        """
        try:
            # Fetch webpage content
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to extract recipe data from schema.org structured data
            recipe_data = SharingService._extract_recipe_from_schema(soup)
            
            # If schema extraction fails, try basic HTML parsing
            if not recipe_data:
                recipe_data = SharingService._extract_recipe_from_html(soup)
            
            if not recipe_data:
                return None
            
            # Create recipe with extracted data
            new_recipe = Recipe(
                user_id=user_id,
                title=recipe_data.get('title', 'Imported Recipe'),
                image_url=recipe_data.get('image_url'),
                ingredients=json.dumps(recipe_data.get('ingredients', [])),
                steps=json.dumps(recipe_data.get('steps', [])),
                tags=json.dumps(recipe_data.get('tags', [])) if recipe_data.get('tags') else None,
                reference_link=url,
                visibility='private',
                servings=recipe_data.get('servings', 1),
                is_favorite=False
            )
            
            db.add(new_recipe)
            db.commit()
            db.refresh(new_recipe)
            return new_recipe
            
        except Exception as e:
            # Handle any errors gracefully
            print(f"Error importing recipe from URL: {e}")
            return None
    
    @staticmethod
    def _extract_recipe_from_schema(soup: BeautifulSoup) -> Optional[dict]:
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
    
    @staticmethod
    def _extract_recipe_from_html(soup: BeautifulSoup) -> Optional[dict]:
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
    
    @staticmethod
    def generate_qr_code(recipe_url: str) -> bytes:
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
    
    @staticmethod
    def get_share_metadata(db: Session, recipe_id: int, base_url: str) -> Optional[dict]:
        """
        Get social media share metadata for a recipe.
        Returns metadata formatted for Open Graph and Twitter Cards.
        Requirements: 35.1, 35.2
        """
        # Get recipe
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            return None
        
        # Parse ingredients and steps for description
        ingredients = json.loads(recipe.ingredients) if isinstance(recipe.ingredients, str) else recipe.ingredients
        steps = json.loads(recipe.steps) if isinstance(recipe.steps, str) else recipe.steps
        
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
        if recipe.visibility in ['public', 'unlisted']:
            recipe_url = f"{base_url}/recipes/public/{recipe_id}"
        
        return {
            'title': recipe.title,
            'description': description,
            'image_url': recipe.image_url,
            'url': recipe_url
        }
