"""
Posts API endpoints for the Post-Comments Service.

This module handles all post-related operations including:
- Creating, reading, and deleting posts
- Managing comments on posts (nested under posts resource)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from datetime import datetime, timezone
from typing import Dict

from app.database import get_db
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.post import PostCreate, PostResponse, PostListResponse
from app.schemas.comment import CommentListResponse, CommentResponse, CommentCreate

# Create router with common prefix and tags for OpenAPI documentation
router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    """
    Create a new post.

    Args:
        post_data: Post creation data including title, content, and optional author
        db: Database session dependency

    Returns:
        PostResponse: The created post with generated ID and timestamps

    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        # Create new post instance with current timestamps
        db_post = Post(
            title=post_data.title,
            content=post_data.content,
            author=post_data.author,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Persist to database
        db.add(db_post)
        db.commit()
        db.refresh(db_post)  # Refresh to get auto-generated fields

        # Build response with comments count (will be 0 for new post)
        return PostResponse(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            author=db_post.author,
            created_at=db_post.created_at,
            updated_at=db_post.updated_at,
            comments_count=len(db_post.comments) if db_post.comments else 0,
        )
    except Exception as e:
        # Rollback transaction on any error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}",
        )


@router.get("/", response_model=PostListResponse)
def get_posts(
    page: int = 1, limit: int = 10, db: Session = Depends(get_db)
) -> PostListResponse:
    """
    Get paginated list of posts.

    Args:
        page: Page number (starts from 1)
        limit: Number of posts per page (1-100)
        db: Database session dependency

    Returns:
        PostListResponse: Paginated list of posts with metadata

    Raises:
        HTTPException: 400 for invalid pagination parameters, 500 for database errors
    """
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Page must be >= 1"
        )
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100",
        )

    try:
        # Calculate offset for pagination
        offset = (page - 1) * limit

        # Get total count efficiently using SQL COUNT
        total = db.exec(select(func.count()).select_from(Post)).one()

        # Fetch posts with pagination and ordering
        statement = (
            select(Post)
            .offset(offset)
            .limit(limit)
            .order_by(Post.created_at.desc())  # Latest posts first
        )
        posts = db.exec(statement).all()

        # Convert to response format with comments count
        post_responses = [
            PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                author=post.author,
                created_at=post.created_at,
                updated_at=post.updated_at,
                comments_count=len(post.comments) if post.comments else 0,
            )
            for post in posts
        ]

        # Calculate total pages for pagination metadata
        total_pages = (total + limit - 1) // limit

        return PostListResponse(
            posts=post_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch posts: {str(e)}",
        )


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)) -> PostResponse:
    """
    Get a single post by ID.

    Args:
        post_id: Unique identifier of the post
        db: Database session dependency

    Returns:
        PostResponse: The requested post with comments count

    Raises:
        HTTPException: 404 if post not found, 500 for database errors
    """
    try:
        # Fetch post by primary key
        post = db.get(Post, post_id)

        # Check if post exists
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found",
            )

        # Build response with current comments count
        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author=post.author,
            created_at=post.created_at,
            updated_at=post.updated_at,
            comments_count=len(post.comments) if post.comments else 0,
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without modification
        raise
    except Exception as e:
        # Convert unexpected errors to HTTP 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve post: {str(e)}",
        )


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(post_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Delete a post by ID.

    Note: This will cascade delete all associated comments due to foreign key constraints.

    Args:
        post_id: Unique identifier of the post to delete
        db: Database session dependency

    Returns:
        Dict with success message

    Raises:
        HTTPException: 404 if post not found, 500 for database errors
    """
    try:
        # Find the post to delete
        post = db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found",
            )

        # Delete post (comments will be cascade deleted)
        db.delete(post)
        db.commit()

        return {"message": f"Post with ID {post_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete post: {str(e)}",
        )


# Comments endpoints (nested under posts resource)


@router.get("/{post_id}/comments", response_model=CommentListResponse)
def get_comments(
    post_id: int, page: int = 1, limit: int = 20, db: Session = Depends(get_db)
) -> CommentListResponse:
    """
    Get paginated comments for a specific post.

    Args:
        post_id: ID of the post to get comments for
        page: Page number (starts from 1)
        limit: Number of comments per page (1-100)
        db: Database session dependency

    Returns:
        CommentListResponse: Paginated list of comments with metadata

    Raises:
        HTTPException: 400 for invalid parameters, 404 if post not found, 500 for database errors
    """
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Page must be >= 1"
        )
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100",
        )

    try:
        # Verify post exists
        post = db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found",
            )

        # Calculate pagination
        offset = (page - 1) * limit

        # Get total comments count for this post
        total_query = (
            select(func.count()).select_from(Comment).where(Comment.post_id == post_id)
        )
        total = db.exec(total_query).one()

        # Fetch comments with pagination
        statement = (
            select(Comment)
            .where(Comment.post_id == post_id)
            .offset(offset)
            .limit(limit)
            .order_by(Comment.created_at.asc())  # Chronological order for comments
        )
        comments = db.exec(statement).all()

        # Convert to response format
        comment_responses = [
            CommentResponse(
                id=comment.id,
                content=comment.content,
                author=comment.author,
                post_id=comment.post_id,
                parent_comment_id=comment.parent_comment_id,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
            for comment in comments
        ]

        # Calculate pagination metadata
        total_pages = (total + limit - 1) // limit

        return CommentListResponse(
            comments=comment_responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch comments: {str(e)}",
        )


@router.post(
    "/{post_id}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentResponse,
)
def create_comment(
    post_id: int, comment_data: CommentCreate, db: Session = Depends(get_db)
) -> CommentResponse:
    """
    Create a new comment on a post.

    Supports nested comments via parent_comment_id for bonus functionality.

    Args:
        post_id: ID of the post to comment on
        comment_data: Comment creation data including content, author, and optional parent_comment_id
        db: Database session dependency

    Returns:
        CommentResponse: The created comment with generated ID and timestamps

    Raises:
        HTTPException: 404 if post or parent comment not found, 500 for database errors
    """
    try:
        # Verify the post exists
        post = db.get(Post, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found",
            )

        # If this is a reply, verify the parent comment exists and belongs to the same post
        if comment_data.parent_comment_id is not None:
            parent_comment = db.get(Comment, comment_data.parent_comment_id)
            if not parent_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent comment with ID {comment_data.parent_comment_id} not found",
                )
            # Ensure parent comment belongs to the same post
            if parent_comment.post_id != post_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment must belong to the same post",
                )

        # Create new comment
        db_comment = Comment(
            content=comment_data.content,
            author=comment_data.author,
            post_id=post_id,
            parent_comment_id=comment_data.parent_comment_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Persist to database
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return CommentResponse(
            id=db_comment.id,
            content=db_comment.content,
            author=db_comment.author,
            post_id=db_comment.post_id,
            parent_comment_id=db_comment.parent_comment_id,
            created_at=db_comment.created_at,
            updated_at=db_comment.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}",
        )
