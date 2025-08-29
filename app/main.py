from fastapi import FastAPI
from .api import posts, comments

app = FastAPI()

app.include_router(posts.router)
app.include_router(comments.router)
