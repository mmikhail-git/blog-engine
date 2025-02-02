from fastapi import Query

from app.backend.db import SessionLocal


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def pagination_params(
        page: int = Query(default=1, ge=1, description="Номер страницы"),
        size: int = Query(default=10, ge=1, le=100, description="Количество элементов на странице"),
) -> tuple[int, int]:
    return page, size
