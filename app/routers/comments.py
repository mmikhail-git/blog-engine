from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.operators import and_

from app.backend.db_depends import get_db, pagination_params
from app.models.pydantic_model import PaginatedCommentResponse, Pagination, CommentResponse, CreateComment, ResponseUser
from app.models.orm_models import Comment, Post
from app.routers.auth import get_current_user

router = APIRouter(prefix='/comments', tags=['comments'])

PaginationParams = Annotated[tuple[int, int], Depends(pagination_params)]


@router.get('/{post_id}/post', response_model=PaginatedCommentResponse)
async def get_all_comments_by_post(
        post_id: int,
        pagination: PaginationParams,
        db: AsyncSession = Depends(get_db)
):
    page, size = pagination
    offset = (page - 1) * size

    result = db.execute(
        select(Comment)
        .where(and_(Comment.is_active == True, Comment.post_id == post_id))
        .offset(offset)
        .limit(size)
    )

    comments = result.scalars().all()

    total_result = db.execute(
        select(func.count()).select_from(Comment).where(and_(Comment.is_active == True, Comment.post_id == post_id))
    )
    total = total_result.scalar_one()
    pages = (total + size - 1) // size

    return PaginatedCommentResponse(
        comments=[
            CommentResponse(
                id=comment.id,
                text=comment.text,
                author_id=comment.author_id,
                parent_id=comment.parent_id,
                is_active=comment.is_active,
                created_at=comment.created_at
            ) for comment in comments
        ],
        pagination=Pagination(
            page=page,
            size=size,
            total=total,
            pages=pages
        )
    )


@router.post('/{post_id}/post')
async def create_comment(
        post_id: int,
        create_comment: CreateComment,
        db: AsyncSession = Depends(get_db), current_user: ResponseUser = Depends(get_current_user)
):

    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if create_comment.parent_id is not None:
        result = db.execute(select(Comment).where(Comment.id == create_comment.parent_id))
        parent_comment = result.scalars().first()
        if parent_comment is None:
            raise HTTPException(status_code=400, detail=f"Parent comment with id {create_comment.parent_id} does not exist.")

    new_comment = Comment(
        post_id=post_id,
        text=create_comment.text,
        parent_id=create_comment.parent_id,
        author_id=current_user['id'],
        is_active=True
    )

    db.add(new_comment)
    db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }
