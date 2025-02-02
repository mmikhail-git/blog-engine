from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from typing import List, Optional
from app.backend.db import *

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    fullname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    hashed_password = Column(String)
    email = Column(String, unique=True)
    is_admin = Column(Boolean, default=False)
    is_user = Column(Boolean, default=False)

    posts: Mapped[List['Post']] = relationship('Post', back_populates='author')
    comments: Mapped[List['Comment']] = relationship('Comment', back_populates='author')


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String(250), index=True, unique=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    author_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    tags: Mapped[list['Tag']] = relationship(secondary='post_tags', back_populates='posts')

    class Config:
        from_attributes = True  # Enable from_orm feature

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    slug: Mapped[str] = mapped_column(String(250), index=True, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    posts: Mapped[list['Post']] = relationship(secondary='post_tags', back_populates='tags')


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), primary_key=True)

    __table_args__ = (
        UniqueConstraint('post_id', 'tag_id', name='uq_post_tag'),
    )

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    author_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = mapped_column(Integer, ForeignKey('posts.id'), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('comments.id'), nullable=True)

    author = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')
    parent: Mapped[Optional["Comment"]] = relationship("Comment", remote_side=[id])



#from sqlalchemy.schema import CreateTable
#print(CreateTable(User.__table__))
#print(CreateTable(Post.__table__))
#print(CreateTable(Tag.__table__))
#print(CreateTable(PostTag.__table__))
#print(CreateTable(Comment.__table__))

