from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from sqlalchemy import insert
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.backend.db_depends import get_db
from app.models.pydantic_model import TagResponse, CreateTag
from app.models.orm_models import Tag

router = APIRouter(prefix='/tags', tags=['tags'])


@router.get('/all', response_model=List[TagResponse])
async def get_all_tags(db: AsyncSession = Depends(get_db)):
    tags = db.scalars(select(Tag).where(Tag.is_active == True)).all()
    return tags


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_tag(db: Annotated[Session, Depends(get_db)], create_tag: CreateTag):
    db.execute(
        insert(Tag).values(name=create_tag.name,
                           slug=slugify(create_tag.name)))

    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }
