import markdown2
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated, List
from sqlalchemy import func
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.operators import and_
from app.backend.db_depends import get_db, pagination_params
from app.models.pydantic_model import CreatePost, PostResponse, UpdatePost, PaginatedPostResponse, Pagination, TagResponse, \
    CommentResponse, ResponseUser
from app.models.orm_models import Post, Tag
from .auth import get_current_user

router = APIRouter(prefix='/posts', tags=['posts'])

PaginationParams = Annotated[tuple[int, int], Depends(pagination_params)]


@router.get('/all', response_model=PaginatedPostResponse)
async def get_all_posts(
        pagination: PaginationParams,
        db: AsyncSession = Depends(get_db)
):

    page, size = pagination
    offset = (page - 1) * size

    result = db.execute(
        select(Post).where(Post.is_active == True).offset(offset).limit(size)
    )
    posts = result.scalars().all()

    total_result = db.execute(
        select(func.count()).select_from(Post).where(Post.is_active == True)
    )
    total = total_result.scalar_one()
    pages = (total + size - 1) // size

    return PaginatedPostResponse(
        posts=[
            PostResponse(
                id=post.id,
                title=post.title,
                author_id=post.author_id,
                author_nickname=post.author.nickname,
                author_fullname=post.author.fullname,
                slug=post.slug,
                image_url=post.image_url,
                content=markdown2.markdown(post.content),
                is_active=post.is_active,
                created_at=post.created_at,
                tags=[TagResponse(id=tag.id, name=tag.name, slug=tag.slug) for tag in post.tags],
                comments=[CommentResponse(id=comment.id, author_id=comment.author_id, text=comment.text, parent_id=comment.parent_id, created_at=comment.created_at, author_nickname=comment.author.nickname, author_fullname=comment.author.fullname) for comment in post.comments]
            ) for post in posts
        ],
        pagination=Pagination(
            page=page,
            size=size,
            total=total,
            pages=pages
        ),
    )


@router.get('/all/{tag_id}', response_model=PaginatedPostResponse)
async def get_all_posts_by_tag(tag_id: int, pagination: PaginationParams, db: AsyncSession = Depends(get_db)):
    page, size = pagination
    offset = (page - 1) * size

    result = db.execute(
        select(Post).where(and_(Post.is_active == True, Post.tags.any(id=tag_id))).offset(offset).limit(size)
    )
    posts = result.scalars().all()

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    total_result = db.execute(
        select(func.count()).select_from(Post).where(and_(Post.is_active == True, Post.tags.any(id=tag_id)))
    )
    total = total_result.scalar_one()
    pages = (total + size - 1) // size

    return PaginatedPostResponse(
        posts=[
            PostResponse(
                id=post.id,
                title=post.title,
                author_id=post.author_id,
                author_nickname=post.author.nickname,
                author_fullname=post.author.fullname,
                slug=post.slug,
                image_url=post.image_url,
                content=post.content,
                is_active=post.is_active,
                created_at=post.created_at,
                tags=[TagResponse(id=tag.id, name=tag.name, slug=tag.slug) for tag in post.tags],
                comments=[CommentResponse(id=comment.id, author_id=comment.author_id, text=comment.text, parent_id=comment.parent_id, created_at=comment.created_at, author_nickname=comment.author.nickname, author_fullname=comment.author.fullname) for comment in post.comments]
            ) for post in posts
        ],
        pagination=Pagination(
            page=page,
            size=size,
            total=total,
            pages=pages
        )
    )


@router.get('/{id}', response_model=PostResponse)
async def get_one_post(id: int, db: AsyncSession = Depends(get_db)):

    result = db.execute(
        select(Post).where(and_(Post.is_active == True, Post.id == id))
    )
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return PostResponse(
                id=post.id,
                title=post.title,
                author_id=post.author_id,
                author_nickname=post.author.nickname,
                author_fullname=post.author.fullname,
                slug=post.slug,
                image_url=post.image_url,
                content=post.content,
                is_active=post.is_active,
                created_at=post.created_at,
                tags=[TagResponse(id=tag.id, name=tag.name, slug=tag.slug) for tag in post.tags],
                comments=[CommentResponse(id=comment.id, author_id=comment.author_id, text=comment.text, parent_id=comment.parent_id, created_at=comment.created_at, author_nickname=comment.author.nickname, author_fullname=comment.author.fullname) for comment in post.comments]
            )


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_post(create_post: CreatePost, tags: List[str] = [], db: AsyncSession = Depends(get_db),
                      current_user: ResponseUser = Depends(get_current_user)):

    print(current_user)

    new_post = Post(
        title=create_post.title,
        content=create_post.content,
        author_id=current_user['id'],  # Используем ID из токена
        slug=slugify(create_post.title)
    )

    db.add(new_post)

    db.commit()  # Не забывайте, что используете асинхронный запрос

    for tag_name in tags:
        # Проверяем, существует ли тег
        result = db.execute(select(Tag).where(Tag.name == tag_name))
        tag = result.scalars().first()

        # Если тег не существует, создаём его
        if not tag:
            tag = Tag(name=tag_name, slug=slugify(tag_name))
            db.add(tag)

        # Связываем тег с постом
        new_post.tags.append(tag)

    db.commit()  # Не забывайте о втором коммите

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.delete('/{id}', response_model=PostResponse)
async def delete_post(id: int, get_user: Annotated[dict, Depends(get_current_user)], db: AsyncSession = Depends(get_db)):

    result = db.execute(select(Post).where(Post.id == id))
    post = result.scalars().first()

    # Проверяем, существует ли пост
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Проверяем, является ли текущий пользователь автором поста
    if post.author_id != get_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to edit this post")

    post.is_active = False
    db.commit()

    return post

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED, response_model=PostResponse)
async def update_post(
    id: int,
    update_post: UpdatePost,
    get_user: Annotated[dict, Depends(get_current_user)],
    tags: List[str] = [],
    db: AsyncSession = Depends(get_db)
):
    result = db.execute(select(Post).where(Post.id == id))
    post = result.scalars().first()

    # Проверяем, существует ли пост
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Проверяем, является ли текущий пользователь автором поста
    if post.author_id != get_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to edit this post")

    post.title = update_post.title
    post.content = update_post.content
    post.slug = slugify(update_post.title)

    db.commit()

    post.tags.clear()

    for tag_name in tags:
        # Проверяем, существует ли тег
        result = db.execute(select(Tag).where(Tag.name == tag_name))
        tag = result.scalars().first()

        # Если тег не существует, создаем его
        if not tag:
            tag = Tag(name=tag_name, slug=slugify(tag_name))
            db.add(tag)

        if tag not in post.tags:
            post.tags.append(tag)

    db.commit()

    return post
