from fastapi import APIRouter, Depends
from url_shortener.models import user_model
from url_shortener.workflows.workflows import UserWorkflow
from url_shortener.schema import user_schema
from sqlalchemy.orm import Session
from url_shortener.utils.database import get_db

user_router = APIRouter(
    tags=["users"]
)


@user_router.post("/users")
async def create_user(
    user: user_schema.UserCreate,
    db: Session = Depends(get_db)) -> user_schema.UserDetails:
    
    user = await UserWorkflow(db).create_user(user)
    return user


@user_router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)) -> user_schema.UserDetails:
    
    return await UserWorkflow(db).get_user(user_id)


@user_router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    status = await UserWorkflow(db).delete_user(user_id)
    print(status)
    return {"message": f"UserId: {user_id} deleted successfully."}