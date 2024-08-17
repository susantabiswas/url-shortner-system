from fastapi import FastAPI
import validators
from .models import shortened_url
from .exceptions import exceptions

app = FastAPI()


@app.get("/")
async def root():
    return "Welcome to URL shortener service."


@app.post("/shortUrls")
async def shorten_url(url: shortened_url.ShortenedUrl):
    if not validators.url(url.long_url):
        exceptions.bad_request_exception(msg="Input URL is not valid.")

    return f"URL: {url.long_url} shortened"
