from fastapi import Depends, Request, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import validators
import url_shortener.models.short_url as models
from url_shortener.utils.database import engine, Base, get_db
from url_shortener.exceptions import exceptions
from url_shortener.workflows.workflows import UrlShortenerWorkflow

router = APIRouter(
    tags=["shorturls"]
)

workflow = UrlShortenerWorkflow()
Base.metadata.create_all(bind=engine)


@router.post("/shortUrls", response_model=models.ShortUrlBase)
async def shorten_url(
        url: models.UrlBase,
        db: Session = Depends(get_db)
):

    # ensure that the email format is valid
    if not validators.url(url.long_url):
        exceptions.bad_request_exception(msg="Input URL is not valid.")

    return await UrlShortenerWorkflow.create_short_url(db, url)


@router.get("/shortUrls/{url_hash}")
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
