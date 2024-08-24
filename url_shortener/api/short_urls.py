from typing import Annotated

from fastapi import Depends, Request, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import validators
from url_shortener.schema import short_url_schema
from url_shortener.utils.database import engine, Base, get_db
from url_shortener.exceptions import exceptions
from url_shortener.workflows.workflows import UrlShortenerWorkflow

router = APIRouter(
    tags=["shorturls"]
)

workflow = UrlShortenerWorkflow()
Base.metadata.create_all(bind=engine)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/shortUrls", response_model=short_url_schema.ShortUrlBaseSchema)
async def shorten_url(
        url: short_url_schema.UrlBaseSchema,
        db: Session = Depends(get_db)) -> short_url_schema.ShortUrlBaseSchema:

    # ensure that the email format is valid
    if not validators.url(url.long_url):
        exceptions.bad_request_exception(msg="Input URL is not valid.")

    return await UrlShortenerWorkflow.create_short_url(db, url)


@router.get("/shortUrls/{url_key}")
async def get_long_url(
        token: Annotated[str, Depends(oauth2_scheme)],
        url_key: str,
        request: Request,
        db: Session = Depends(get_db)):

    url = await UrlShortenerWorkflow.get_short_url_by_hash(db, url_key)

    if url:
        return RedirectResponse(url=url.long_url)
    else:
        exceptions.not_found_exception(request.url)
