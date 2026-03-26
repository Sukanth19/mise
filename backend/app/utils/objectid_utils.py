"""
Utility functions for MongoDB ObjectId conversion and validation.

This module provides helper functions for converting between string IDs
(used in API requests/responses) and ObjectId instances (used internally
with MongoDB).
"""

from bson import ObjectId
from fastapi import HTTPException, status
from typing import Optional, List


def validate_objectid(id_str: str, field_name: str = "id") -> ObjectId:
    """
    Validate and convert a string ID to ObjectId.
    
    Args:
        id_str: String representation of ObjectId
        field_name: Name of the field (for error messages)
        
    Returns:
        ObjectId instance
        
    Raises:
        HTTPException: If the ID is invalid (422 Unprocessable Entity)
    """
    if not ObjectId.is_valid(id_str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {field_name}: '{id_str}' is not a valid ObjectId",
            headers={"error_code": "INVALID_OBJECTID"}
        )
    return ObjectId(id_str)


def validate_objectid_optional(id_str: Optional[str], field_name: str = "id") -> Optional[ObjectId]:
    """
    Validate and convert an optional string ID to ObjectId.
    
    Args:
        id_str: Optional string representation of ObjectId
        field_name: Name of the field (for error messages)
        
    Returns:
        ObjectId instance or None
        
    Raises:
        HTTPException: If the ID is provided but invalid (422 Unprocessable Entity)
    """
    if id_str is None:
        return None
    return validate_objectid(id_str, field_name)


def validate_objectid_list(id_list: List[str], field_name: str = "ids") -> List[ObjectId]:
    """
    Validate and convert a list of string IDs to ObjectIds.
    
    Args:
        id_list: List of string representations of ObjectIds
        field_name: Name of the field (for error messages)
        
    Returns:
        List of ObjectId instances
        
    Raises:
        HTTPException: If any ID is invalid (422 Unprocessable Entity)
    """
    result = []
    for idx, id_str in enumerate(id_list):
        if not ObjectId.is_valid(id_str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid {field_name}[{idx}]: '{id_str}' is not a valid ObjectId",
                headers={"error_code": "INVALID_OBJECTID"}
            )
        result.append(ObjectId(id_str))
    return result


def objectid_to_str(obj_id: Optional[ObjectId]) -> Optional[str]:
    """
    Convert ObjectId to string for JSON serialization.
    
    Args:
        obj_id: ObjectId instance or None
        
    Returns:
        String representation or None
    """
    return str(obj_id) if obj_id is not None else None


def objectid_list_to_str(obj_ids: List[ObjectId]) -> List[str]:
    """
    Convert list of ObjectIds to strings for JSON serialization.
    
    Args:
        obj_ids: List of ObjectId instances
        
    Returns:
        List of string representations
    """
    return [str(obj_id) for obj_id in obj_ids]
