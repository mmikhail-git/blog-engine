from fastapi import FastAPI
from app.routers import posts, tags, comments, auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(posts.router)
app.include_router(tags.router)
app.include_router(comments.router)
app.include_router(auth.router)


