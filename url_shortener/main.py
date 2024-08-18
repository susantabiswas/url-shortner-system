from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
import secrets
from sqlalchemy.orm import Session
import validators
import url_shortener.models.short_url as models
import url_shortener.schema.short_url as schema
from .utils.database import engine, SessionLocal, Base
from .exceptions import exceptions
from .workflows import workflows

app = FastAPI()
workflow = workflows.UrlShortenerWorkflow()
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

    # TODO: This code can possibly have hash collision, add loop based
    # key creation till unique
    # generate a unique hash key for the URL
    url_hash = await workflow.generate_hash_key()

    url = schema.ShortUrl(
        long_url=url.long_url,
        url_hash=url_hash
    )

    db.add(url)
    db.commit()
    # fetch the data for this entity from DB.
    # To get the values which were generated while inserting the row
    db.refresh(url)
    url.short_url = url_hash

    return url


@app.get("/shortUrls/{url_hash}")
async def get_long_url(
        url_hash: str,
        request: Request,
        db: Session = Depends(get_db)
    ):

    url = (
        db.query(schema.ShortUrl)
        .filter(
            schema.ShortUrl.url_hash == url_hash,
            schema.ShortUrl.is_active)
        .first()
    )

    if url:
        return RedirectResponse(url=url.long_url)
    else:
        exceptions.not_found_exception(request.url)
