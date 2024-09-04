from fastapi import APIRouter, Depends
from typing import Annotated
from url_shortener.models import user_model
from url_shortener.workflows.workflows import UserWorkflow, OAuthWorkflow
from url_shortener.schema import user_schema
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from url_shortener.exceptions import exceptions
from url_shortener.dao.user_dao import get_user_dao


user_router = APIRouter(
    tags=["users"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@user_router.post("/users")
async def create_user(user: user_schema.UserCreate) -> user_schema.UserDetails:
    
    user = await UserWorkflow(get_user_dao()).create_user(user)
    print('User created: ', user.email, user.user_id, user.fullname, user.is_active)
    return user


@user_router.get("/users/{user_id}")
async def get_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: int) -> user_schema.UserDetails:
    
    # Authenticate user token and then get the user details
    _ = await OAuthWorkflow().get_current_user(token)
    user = await UserWorkflow(get_user_dao()).get_user(user_id)

    if not user:
        exceptions.not_found_exception(user_id)
    return user


@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    status = await UserWorkflow(get_user_dao()).delete_user(user_id)
    print(status)
    return {"message": f"UserId: {user_id} deleted successfully."}