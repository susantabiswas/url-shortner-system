from contextlib import contextmanager
from url_shortener.dao.dao_base import UserDaoBase
from url_shortener.schema.user_schema import UserCreate
from url_shortener.models.user_model import User
from sqlalchemy.orm import Session
from url_shortener.exceptions import exceptions
from url_shortener.utils.database import db_manager


class UserDao(UserDaoBase):
    @contextmanager
    def session_scope(self):
        session: Session = db_manager.get_session()

        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    async def insert(self, user: UserCreate, hashed_password: str) -> User:
        with self.session_scope() as db:
            user = User(
                email=user.email,
                fullname=user.fullname,
                hashed_password=hashed_password
            )

            db.add(user)
            db.flush()
            db.refresh(user)

            # Dev Note: Since we are using a session in the context manager scope,
            # we need to return a new instance of the User model
            # explicitly to avoid the issue of the model being deleted when the session is closed
            # when the scope of context manager ends.
            return User(id=user.id, email=user.email, fullname=user.fullname)


    async def get_by_user_id(self, user_id: int) -> User:
        with self.session_scope() as db:
            user = (
                db.query(User)
                    .filter(User.user_id == user_id)
                    .first()
            )

            if user:
                return User(id=user.id, email=user.email, fullname=user.fullname)

            return None

    async def get_user_by_email(self, email: str) -> User:
        with self.session_scope() as db:
            user = (
                db.query(User)
                    .filter(User.email == email)
                    .first()
            )

            if user:
                return User(id=user.id, email=user.email, fullname=user.fullname)

            return None


    async def delete_by_user_id(self, user_id: int) -> Integer:
        rows = 0
        with self.session_scope() as db:
            rows = db.query(User).filter(User.user_id == user_id).delete()
    
            if rows == 0:
                exceptions.not_found_exception(user_id)

        print(f"user with Id: {user_id} deleted.")
        return rows