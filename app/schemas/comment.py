from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional, List
from pydantic import field_validator


class CommentBase(SQLModel):
    content: str
    author: str
    parent_comment_id: Optional[int] = None

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()

    @field_validator("author")
    @classmethod
    def author_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Author cannot be empty")
        return v.strip()


class CommentCreate(CommentBase):
    pass


class CommentUpdate(SQLModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class CommentResponse(CommentBase):
    id: int
    content: str
    post_id: int
    parent_comment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class CommentListResponse(SQLModel):
    comments: List[CommentResponse]
    total: int
    page: int
    limit: int
    total_pages: int
