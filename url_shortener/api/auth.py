from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from url_shortener.schema import auth_schema
from url_shortener.workflows.workflows import OAuthWorkflow
from url_shortener.utils.database import get_db
from sqlalchemy.orm import Session

oauth2_router = APIRouter(
    tags=["oauth2"]
)


@oauth2_router.post("/token")
async def authenticate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)) -> auth_schema.Token:

    username, password = form_data.username, form_data.password
    return await OAuthWorkflow(db).authenticate(username, password)
