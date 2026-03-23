from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import NoteCreate, NoteResponse
from app.models import RecipeNote, Recipe
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/recipes", tags=["notes"])


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


@router.post("/{recipe_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    recipe_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new note for a recipe."""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Create the note
    note = RecipeNote(
        recipe_id=recipe_id,
        user_id=user_id,
        note_text=note_data.note_text
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    return note


@router.get("/{recipe_id}/notes", response_model=List[NoteResponse])
def get_notes(
    recipe_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get all notes for a recipe, ordered by created_at."""
    # Check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
            headers={"error_code": "RECIPE_NOT_FOUND"}
        )
    
    # Get notes ordered by created_at
    notes = db.query(RecipeNote).filter(
        RecipeNote.recipe_id == recipe_id
    ).order_by(RecipeNote.created_at.asc()).all()
    
    return notes


@router.delete("/{recipe_id}/notes/{note_id}", status_code=status.HTTP_200_OK)
def delete_note(
    recipe_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a note."""
    # Get the note
    note = db.query(RecipeNote).filter(
        RecipeNote.id == note_id,
        RecipeNote.recipe_id == recipe_id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
            headers={"error_code": "NOTE_NOT_FOUND"}
        )
    
    # Check if user owns the note
    if note.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this note",
            headers={"error_code": "FORBIDDEN"}
        )
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}
