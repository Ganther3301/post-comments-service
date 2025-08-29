from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict
from datetime import datetime, timezone

from app.database import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentResponse, CommentUpdate

# Create router for direct comment operations
router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)) -> CommentResponse:
    """
    Get a single comment by ID.

    This endpoint allows direct access to any comment regardless of which post it belongs to.

    Args:
        comment_id: Unique identifier of the comment
        db: Database session dependency

    Returns:
        CommentResponse: The requested comment with all details

    Raises:
        HTTPException: 404 if comment not found, 500 for database errors
    """
    try:
        # Fetch comment by primary key
        comment = db.get(Comment, comment_id)

        # Check if comment exists
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found",
            )

        # Build and return response
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            author=comment.author,
            post_id=comment.post_id,
            parent_comment_id=comment.parent_comment_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without modification
        raise
    except Exception as e:
        # Convert unexpected errors to HTTP 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve comment: {str(e)}",
        )


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int, comment_data: CommentUpdate, db: Session = Depends(get_db)
) -> CommentResponse:
    """
    Update a comment's content.

    Only the comment content can be updated. Author, post association, and parent
    comment cannot be changed after creation.

    Args:
        comment_id: Unique identifier of the comment to update
        comment_data: Updated comment data (content only)
        db: Database session dependency

    Returns:
        CommentResponse: The updated comment with new timestamp

    Raises:
        HTTPException: 404 if comment not found, 500 for database errors
    """
    try:
        # Find the comment to update
        comment = db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found",
            )

        # Update the comment content
        comment.content = comment_data.content
        comment.updated_at = datetime.now(timezone.utc)

        # Persist changes
        db.commit()
        db.refresh(comment)

        # Return updated comment
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            author=comment.author,
            post_id=comment.post_id,
            parent_comment_id=comment.parent_comment_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update comment: {str(e)}",
        )


@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(comment_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Delete a comment by ID.

    This will also cascade delete any replies to this comment due to the foreign key
    constraint with ON DELETE CASCADE.

    Args:
        comment_id: Unique identifier of the comment to delete
        db: Database session dependency

    Returns:
        Dict with success message

    Raises:
        HTTPException: 404 if comment not found, 500 for database errors
    """
    try:
        # Find the comment to delete
        comment = db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found",
            )

        # Delete comment (replies will be cascade deleted if any exist)
        db.delete(comment)
        db.commit()

        return {"message": f"Comment with ID {comment_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        # Rollback transaction on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}",
        )
