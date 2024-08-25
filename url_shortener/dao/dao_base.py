import abc
from pydantic import BaseModel
from sqlalchemy.orm import Session

from url_shortener.models.short_url_model import ShortUrl
from url_shortener.models.user_model import User
from url_shortener.schema.user_schema import UserBase


# Base class for all DAO classes, has db session object
class DaoBase():
    pass


# Base class for ShortUrl DAO
class ShortUrlDaoBase(abc.ABC, DaoBase):

    @abc.abstractmethod
    async def insert(self, long_url: str, url_hash: str) -> ShortUrl:
        pass

    @abc.abstractmethod
    async def get_by_url_hash(self, url_hash: str) -> ShortUrl | None:
        pass

    @abc.abstractmethod
    async def delete_by_url_hash(self, url_hash: str) -> None:
        pass


class UserDaoBase(abc.ABC, DaoBase):

    @abc.abstractmethod
    async def insert(self, user: UserBase) -> User:
        pass


    @abc.abstractclassmethod
    async def get_by_user_id(self, user_id: int) -> User:
        pass


    @abc.abstractclassmethod
    async def delete_by_user_id(self, user_id: int) -> None:
        pass