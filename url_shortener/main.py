from fastapi import FastAPI
from .api import short_urls


app = FastAPI()
app.include_router(short_urls.router)


@app.get("/")
async def root():
    return "Welcome to URL shortener."