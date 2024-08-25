from fastapi import APIRouter, Depends
from typing import Annotated
from url_shortener.models import user_model
from url_shortener.workflows.workflows import UserWorkflow, OAuthWorkflow
from url_shortener.schema import user_schema
from sqlalchemy.orm import Session
from url_shortener.utils.database import get_db
from fastapi.security import OAuth2PasswordBearer

user_router = APIRouter(
    tags=["users"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@user_router.post("/users")
async def create_user(
    user: user_schema.UserCreate,
    db: Session = Depends(get_db)) -> user_schema.UserDetails:
    
    user = await UserWorkflow(db).create_user(user)
    return user


@user_router.get("/users/{user_id}")
async def get_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: int,
    db: Session = Depends(get_db)) -> user_schema.UserDetails:
    
    _ = await OAuthWorkflow(db).get_current_user(token)
    return await UserWorkflow(db).get_user(user_id)


@user_router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    status = await UserWorkflow(db).delete_user(user_id)
    print(status)
    return {"message": f"UserId: {user_id} deleted successfully."}