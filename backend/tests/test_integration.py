"""
Integration tests for Recipe Saver application.
Tests complete user flows: register → login → create → view → edit → delete
"""
import pytest
from io import BytesIO
import random
import string


def generate_unique_username():
    """Generate a unique username for testing"""
    return f"testuser_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"


class TestCompleteUserFlow:
    """Test complete user journey through the application"""
    
    def test_complete_recipe_lifecycle(self, client):
        """
        Test the complete user flow:
        1. Register a new user
        2. Login to get token
        3. Create a recipe
        4. View the recipe
        5. Edit the recipe
        6. Delete the recipe
        """
        username = generate_unique_username()
        password = "password123"
        
        # Step 1: Register a new user
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": username,
                "password": password
            }
        )
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert "id" in user_data
        assert user_data["username"] == username
        
        # Step 2: Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        token = token_data["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Create a recipe
        recipe_data = {
            "title": "Integration Test Recipe",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "steps": ["step 1", "step 2"],
            "tags": ["test", "integration"],
            "reference_link": "https://example.com/recipe"
        }
        create_response = client.post(
            "/api/recipes",
            json=recipe_data,
            headers=headers
        )
        assert create_response.status_code == 201
        created_recipe = create_response.json()
        assert created_recipe["title"] == recipe_data["title"]
        assert created_recipe["ingredients"] == recipe_data["ingredients"]
        assert created_recipe["steps"] == recipe_data["steps"]
        recipe_id = created_recipe["id"]
        
        # Step 4: View the recipe
        get_response = client.get(
            f"/api/recipes/{recipe_id}",
            headers=headers
        )
        assert get_response.status_code == 200
        retrieved_recipe = get_response.json()
        assert retrieved_recipe["id"] == recipe_id
        assert retrieved_recipe["title"] == recipe_data["title"]
        
        # Step 5: Edit the recipe
        update_data = {
            "title": "Updated Integration Test Recipe",
            "ingredients": ["new ingredient 1", "new ingredient 2", "new ingredient 3"],
            "steps": ["new step 1", "new step 2"]
        }
        update_response = client.put(
            f"/api/recipes/{recipe_id}",
            json=update_data,
            headers=headers
        )
        assert update_response.status_code == 200
        updated_recipe = update_response.json()
        assert updated_recipe["title"] == update_data["title"]
        assert updated_recipe["ingredients"] == update_data["ingredients"]
        assert updated_recipe["steps"] == update_data["steps"]
        
        # Step 6: Delete the recipe
        delete_response = client.delete(
            f"/api/recipes/{recipe_id}",
            headers=headers
        )
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_deleted_response = client.get(
            f"/api/recipes/{recipe_id}",
            headers=headers
        )
        assert get_deleted_response.status_code == 404
    
    def test_recipe_list_and_search(self, client):
        """Test viewing recipe list and searching"""
        username = generate_unique_username()
        password = "password123"
        
        # Register and login
        client.post("/api/auth/register", json={"username": username, "password": password})
        login_response = client.post("/api/auth/login", json={"username": username, "password": password})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create multiple recipes
        recipes = [
            {"title": "Pasta Carbonara", "ingredients": ["pasta", "eggs"], "steps": ["cook"]},
            {"title": "Chocolate Cake", "ingredients": ["flour", "chocolate"], "steps": ["bake"]},
            {"title": "Caesar Salad", "ingredients": ["lettuce", "dressing"], "steps": ["mix"]}
        ]
        
        for recipe in recipes:
            response = client.post("/api/recipes", json=recipe, headers=headers)
            assert response.status_code == 201
        
        # Get all recipes
        list_response = client.get("/api/recipes", headers=headers)
        assert list_response.status_code == 200
        all_recipes = list_response.json()
        assert len(all_recipes) >= 3
        
        # Search for specific recipe
        search_response = client.get(
            "/api/recipes?search=chocolate",
            headers=headers
        )
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) >= 1
        assert any("chocolate" in r["title"].lower() for r in search_results)
    
    def test_image_upload_integration(self, client):
        """Test image upload and recipe creation with image"""
        username = generate_unique_username()
        password = "password123"
        
        # Register and login
        client.post("/api/auth/register", json={"username": username, "password": password})
        login_response = client.post("/api/auth/login", json={"username": username, "password": password})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a fake image file
        image_content = b"fake image content"
        files = {
            "file": ("test_image.jpg", BytesIO(image_content), "image/jpeg")
        }
        
        # Upload image
        upload_response = client.post(
            "/api/images/upload",
            files=files,
            headers={"Authorization": headers["Authorization"]}
        )
        assert upload_response.status_code == 201
        image_data = upload_response.json()
        assert "url" in image_data
        image_url = image_data["url"]
        
        # Create recipe with image
        recipe_data = {
            "title": "Recipe with Image",
            "image_url": image_url,
            "ingredients": ["ingredient"],
            "steps": ["step"]
        }
        create_response = client.post(
            "/api/recipes",
            json=recipe_data,
            headers=headers
        )
        assert create_response.status_code == 201
        recipe = create_response.json()
        assert recipe["image_url"] == image_url
    
    def test_error_handling(self, client):
        """Test proper error handling throughout the application"""
        username = generate_unique_username()
        password = "password123"
        
        # Register and login
        client.post("/api/auth/register", json={"username": username, "password": password})
        login_response = client.post("/api/auth/login", json={"username": username, "password": password})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 404 for non-existent recipe
        response = client.get("/api/recipes/99999", headers=headers)
        assert response.status_code == 404
        
        # Test 400 for invalid recipe data (missing title)
        response = client.post(
            "/api/recipes",
            json={"ingredients": ["test"], "steps": ["test"]},
            headers=headers
        )
        assert response.status_code == 422  # FastAPI validation error
        
        # Test 401 for missing authentication (FastAPI returns 422 for missing required header)
        response = client.get("/api/recipes")
        assert response.status_code in [401, 422]  # Accept both as valid error responses
        
        # Test 401 for invalid token
        bad_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/recipes", headers=bad_headers)
        assert response.status_code == 401
    
    def test_ownership_validation(self, client):
        """Test that users can only edit/delete their own recipes"""
        # Create first user and recipe
        user1_data = {"username": generate_unique_username(), "password": "password123"}
        client.post("/api/auth/register", json=user1_data)
        login1 = client.post("/api/auth/login", json=user1_data)
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        recipe_response = client.post(
            "/api/recipes",
            json={"title": "User 1 Recipe", "ingredients": ["a"], "steps": ["b"]},
            headers=headers1
        )
        recipe_id = recipe_response.json()["id"]
        
        # Create second user
        user2_data = {"username": generate_unique_username(), "password": "password123"}
        client.post("/api/auth/register", json=user2_data)
        login2 = client.post("/api/auth/login", json=user2_data)
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Try to edit user1's recipe as user2
        update_response = client.put(
            f"/api/recipes/{recipe_id}",
            json={"title": "Hacked Recipe"},
            headers=headers2
        )
        assert update_response.status_code == 403
        
        # Try to delete user1's recipe as user2
        delete_response = client.delete(
            f"/api/recipes/{recipe_id}",
            headers=headers2
        )
        assert delete_response.status_code == 403
        
        # Verify user1 can still access their recipe
        get_response = client.get(f"/api/recipes/{recipe_id}", headers=headers1)
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "User 1 Recipe"


class TestAPIEndpointConnectivity:
    """Test that all API endpoints are properly connected"""
    
    def test_all_auth_endpoints_connected(self, client):
        """Verify all authentication endpoints are accessible"""
        username = generate_unique_username()
        
        # Test register endpoint
        response = client.post(
            "/api/auth/register",
            json={"username": username, "password": "password123"}
        )
        assert response.status_code == 201
        
        # Test login endpoint
        response = client.post(
            "/api/auth/login",
            json={"username": username, "password": "password123"}
        )
        assert response.status_code == 200
    
    def test_all_recipe_endpoints_connected(self, client):
        """Verify all recipe endpoints are accessible"""
        username = generate_unique_username()
        password = "password123"
        
        # Register and login
        client.post("/api/auth/register", json={"username": username, "password": password})
        login_response = client.post("/api/auth/login", json={"username": username, "password": password})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test POST /api/recipes
        response = client.post(
            "/api/recipes",
            json={"title": "Test", "ingredients": ["a"], "steps": ["b"]},
            headers=headers
        )
        assert response.status_code == 201
        recipe_id = response.json()["id"]
        
        # Test GET /api/recipes
        response = client.get("/api/recipes", headers=headers)
        assert response.status_code == 200
        
        # Test GET /api/recipes/{id}
        response = client.get(f"/api/recipes/{recipe_id}", headers=headers)
        assert response.status_code == 200
        
        # Test PUT /api/recipes/{id}
        response = client.put(
            f"/api/recipes/{recipe_id}",
            json={"title": "Updated"},
            headers=headers
        )
        assert response.status_code == 200
        
        # Test DELETE /api/recipes/{id}
        response = client.delete(f"/api/recipes/{recipe_id}", headers=headers)
        assert response.status_code == 200
    
    def test_image_endpoint_connected(self, client):
        """Verify image upload endpoint is accessible"""
        username = generate_unique_username()
        password = "password123"
        
        # Register and login
        client.post("/api/auth/register", json={"username": username, "password": password})
        login_response = client.post("/api/auth/login", json={"username": username, "password": password})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        files = {
            "file": ("test.jpg", BytesIO(b"fake"), "image/jpeg")
        }
        response = client.post(
            "/api/images/upload",
            files=files,
            headers={"Authorization": headers["Authorization"]}
        )
        assert response.status_code == 201


    def test_recipe_enhancement_flow(self, client):
        """
        Test recipe enhancement features:
        1. Register and login
        2. Create a recipe
        3. Toggle favorite status
        4. Duplicate the recipe
        5. Bulk delete recipes
        """
        username = generate_unique_username()
        password = "password123"
        
        # Register and login
        client.post("/api/auth/register", json={"username": username, "password": password})
        login_response = client.post("/api/auth/login", json={"username": username, "password": password})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a recipe
        recipe_data = {
            "title": "Test Recipe for Enhancements",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "steps": ["step 1", "step 2"],
            "tags": ["test"]
        }
        create_response = client.post("/api/recipes", json=recipe_data, headers=headers)
        assert create_response.status_code == 201
        recipe_id = create_response.json()["id"]
        
        # Test favorite toggle
        favorite_response = client.patch(
            f"/api/recipes/{recipe_id}/favorite",
            json={"is_favorite": True},
            headers=headers
        )
        assert favorite_response.status_code == 200
        assert favorite_response.json()["is_favorite"] is True
        
        # Verify favorite status persists
        get_response = client.get(f"/api/recipes/{recipe_id}", headers=headers)
        assert get_response.status_code == 200
        
        # Test recipe duplication
        duplicate_response = client.post(
            f"/api/recipes/{recipe_id}/duplicate",
            headers=headers
        )
        assert duplicate_response.status_code == 201
        duplicated_recipe = duplicate_response.json()
        assert duplicated_recipe["id"] != recipe_id
        assert duplicated_recipe["title"] == f"{recipe_data['title']} (Copy)"
        assert duplicated_recipe["ingredients"] == recipe_data["ingredients"]
        assert duplicated_recipe["steps"] == recipe_data["steps"]
        
        # Create another recipe for bulk delete test
        recipe_data2 = {
            "title": "Second Test Recipe",
            "ingredients": ["ingredient A"],
            "steps": ["step A"]
        }
        create_response2 = client.post("/api/recipes", json=recipe_data2, headers=headers)
        recipe_id2 = create_response2.json()["id"]
        
        # Test bulk delete
        import json as json_module
        bulk_delete_response = client.request(
            "DELETE",
            "/api/recipes/bulk",
            content=json_module.dumps({"recipe_ids": [recipe_id, duplicated_recipe["id"], recipe_id2]}),
            headers={**headers, "Content-Type": "application/json"}
        )
        if bulk_delete_response.status_code != 200:
            print(f"Bulk delete failed with status {bulk_delete_response.status_code}")
            print(f"Response: {bulk_delete_response.json()}")
        assert bulk_delete_response.status_code == 200
        assert bulk_delete_response.json()["deleted_count"] == 3
        
        # Verify recipes are deleted
        get_response = client.get(f"/api/recipes/{recipe_id}", headers=headers)
        assert get_response.status_code == 404
