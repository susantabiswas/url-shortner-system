from typing import Annotated

from fastapi import Depends, Request, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import validators
from url_shortener.schema import short_url_schema
from url_shortener.exceptions import exceptions
from url_shortener.workflows.workflows import UrlShortenerWorkflow, OAuthWorkflow
from url_shortener.utils.database import get_db
from url_shortener.models import user_model


shorturl_router = APIRouter(
    tags=["shorturls"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@shorturl_router.post("/shortUrls", response_model=short_url_schema.ShortUrlBaseSchema)
async def shorten_url(
        token: Annotated[str, Depends(oauth2_scheme)],
        url: short_url_schema.UrlBaseSchema,
        db: Session = Depends(get_db),
        user: user_model.User = Depends(OAuthWorkflow())) -> short_url_schema.ShortUrlBaseSchema:
    
    # ensure that the email format is valid
    if not validators.url(url.long_url):
        exceptions.bad_request_exception(msg="Input URL is not valid.")

    return await UrlShortenerWorkflow(db).create_short_url(url)


@shorturl_router.get("/shortUrls/{url_key}")
async def get_long_url(
        token: Annotated[str, Depends(oauth2_scheme)],
        url_key: str,
        request: Request,
        db: Session = Depends(get_db),
        user: user_model.User = Depends(OAuthWorkflow())):

    if url:
        return RedirectResponse(url=url.long_url)
    else:
        exceptions.not_found_exception(request.url)


@shorturl_router.delete("/shortUrls/{url_key}")
async def delete_shorturl(
        url_key: str, 
        db: Session = Depends(get_db),
        user: user_model.User = Depends(OAuthWorkflow())):
        
    _ = await UrlShortenerWorkflow(db).delete_by_url_hash(url_key)
    return {"message": f"URL key: {url_key} deleted successfully."}