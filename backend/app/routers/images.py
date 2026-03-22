from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File
from app.schemas import ImageUploadResponse
from app.services.image_service import ImageHandler
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/images", tags=["images"])


def get_current_user_id(authorization: str = Header(...)) -> int:
    """Extract and verify user ID from JWT token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"error_code": "INVALID_AUTH_HEADER"}
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = AuthService.verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"error_code": "INVALID_TOKEN"}
        )
    
    return user_id


@router.post("/upload", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    """
    Upload an image file for a recipe.
    
    Accepts JPEG, PNG, and WebP formats up to 5MB.
    Returns the URL path to the uploaded image.
    """
    url = await ImageHandler.save_image(file)
    return ImageUploadResponse(url=url)
