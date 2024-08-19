from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import validators
import url_shortener.models.short_url as models
import url_shortener.schema.short_url as schema
from .utils.database import engine, SessionLocal, Base
from .exceptions import exceptions
from .workflows.workflows import UrlShortenerWorkflow


app = FastAPI()
workflow = UrlShortenerWorkflow()
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return "Welcome to URL shortener service."


@app.post("/shortUrls", response_model=models.ShortUrlBase)
async def shorten_url(
        url: models.UrlBase,
        db: Session = Depends(get_db)):

    # ensure that the email format is valid
    if not validators.url(url.long_url):
        exceptions.bad_request_exception(msg="Input URL is not valid.")

    return await UrlShortenerWorkflow.create_short_url(db, url)


@app.get("/shortUrls/{url_hash}")
async def get_long_url(
        url_hash: str,
        request: Request,
        db: Session = Depends(get_db)
):

    url = await UrlShortenerWorkflow.get_short_url_by_hash(db, url_hash)

    if url:
        return RedirectResponse(url=url.long_url)
    else:
        exceptions.not_found_exception(request.url)
