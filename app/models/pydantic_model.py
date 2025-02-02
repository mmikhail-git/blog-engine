from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class CreateComment(BaseModel):
    author_id: int | None = None
    text: str
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    author_id: int
    author_nickname: str | None = None
    author_fullname: str | None = None
    text: str
    parent_id: int | None = None
    created_at: datetime


class TagResponse(BaseModel):
    id: int
    name: str
    slug: str | None = None


class CreatePost(BaseModel):
    title: str
    content: str
    author_id: int


class UpdatePost(BaseModel):
    title: str
    content: str
    image_url: str | None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    is_active: bool
    tags: List[TagResponse]
    author_id: int
    author_nickname: str | None = None
    author_fullname: str | None = None
    slug: str
    image_url: str | None = None
    created_at: datetime
    comments: List[CommentResponse]


class CreateTag(BaseModel):
    name: str


class Pagination(BaseModel):
    page: int
    size: int
    total: int
    pages: int


class PaginatedPostResponse(BaseModel):
    posts: List[PostResponse]
    pagination: Pagination


class PaginatedCommentResponse(BaseModel):
    comments: List[CommentResponse]
    pagination: Pagination


class CreateUser(BaseModel):
    nickname: str
    fullname: str
    email: str
    password: str

class ResponseUser(BaseModel):
    id: int
    nickname: str
    fullname: str
    email: str