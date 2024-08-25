from url_shortener.dao.dao_base import UserDaoBase
from url_shortener.schema.user_schema import UserBase, UserCreate
from url_shortener.models.user_model import User
from sqlalchemy.orm import Session
from url_shortener.exceptions import exceptions

class UserDao(UserDaoBase):
    def __init__(self, db: Session):
        self.db = db


    async def insert(self, user: UserCreate, hashed_password: str) -> User:
        user = User(
            email=user.email,
            fullname=user.fullname,
            hashed_password=hashed_password
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user


    async def get_by_user_id(self, user_id: int) -> User:
        user = (
            self.db.query(User)
                .filter(User.user_id == user_id)
                .first()
        )
    
        return user

    async def get_user_by_email(self, email: str) -> User:
        user = (
            self.db.query(User)
                .filter(User.email == email)
                .first()
        )
    
        return user


    async def delete_by_user_id(self, user_id: int) -> None:
        rows = self.db.query(User).filter(User.user_id == user_id).delete()

        if rows == 0:
            exceptions.not_found_exception(user_id)
        self.db.commit()
        print(f"user with Id: {user_id} deleted.")

        return rows