from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import Optional, List


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    author: Optional[str] = Field(default=None, max_length=100)
    post_id: int = Field(foreign_key="posts.id")
    parent_comment_id: Optional[int] = Field(default=None, foreign_key="comments.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    post: "Post" = Relationship(back_populates="comments")
    parent: Optional["Comment"] = Relationship(
        back_populates="replies", sa_relationship_kwargs={"remote_side": "Comment.id"}
    )
    replies: List["Comment"] = Relationship(back_populates="parent")
