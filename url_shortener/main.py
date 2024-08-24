from fastapi import FastAPI
from url_shortener.api import short_urls


app = FastAPI()
app.include_router(short_urls.shorturl_router)


@app.get("/")
async def root():
    return "Welcome to URL shortener."