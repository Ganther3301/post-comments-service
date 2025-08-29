from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional, List
from pydantic import field_validator


class PostBase(SQLModel):
    title: str
    content: str
    author: str

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class PostCreate(PostBase):
    pass


class PostUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Content cannot be empty")
        return v.strip() if v else v


class PostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    comments_count: int = 0


class PostListResponse(SQLModel):
    posts: List[PostResponse]
    total: int
    page: int
    limit: int
    total_pages: int
