from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.orm_models import User
from app.models.pydantic_model import CreateUser
from app.backend.db_depends import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError


SECRET_KEY = '76cf9af5c7ce008b1959755a37b2e795c96a77ab543064610d395244c54a8c10'
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')







@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(create_user: CreateUser, db: AsyncSession = Depends(get_db)):
    db.execute(insert(User).values(nickname=create_user.nickname,
                                   fullname=create_user.fullname,
                                   email=create_user.email,
                                   hashed_password=bcrypt_context.hash(create_user.password)
                                   ))

    db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nickname: str = payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: str = payload.get('is_admin')
        is_user: str = payload.get('is_user')
        expire = payload.get('exp')
        if nickname is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        return {
            'nickname': nickname,
            'id': user_id,
            'is_admin': is_admin,
            'is_user': is_user
        }
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired!"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )

@router.get('/read_current_user')
async def read_current_user(user: dict = Depends(get_current_user)):
    return {'User': user}


async def create_access_token(nickname: str, user_id: int, is_admin: bool, is_user: bool, expires_delta: timedelta):
    encode = {'sub': nickname, 'id': user_id, 'is_admin': is_admin, 'is_user': is_user}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = db.scalar(select(User).where(User.nickname == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post('/token')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)

    token = await create_access_token(user.nickname, user.id, user.is_admin, user.is_user,
                                expires_delta=timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': 'bearer'
    }