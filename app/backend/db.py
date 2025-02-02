import datetime

from sqlalchemy import create_engine, TIMESTAMP, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

engine = create_engine('postgresql://postgres_user:postgres_@db:5432/postgres_database', echo=False)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())



