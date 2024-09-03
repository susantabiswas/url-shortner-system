import abc
from pydantic import BaseModel
from sqlalchemy.orm import session
from sqlalchemy import inspect
from url_shortener.models.short_url_model import ShortUrl
from url_shortener.models.user_model import User
from url_shortener.schema.user_schema import UserBase


# Base class for all DAO classes, has db session object
class DaoBase():
    def get_orm_model_attributes(self, obj) -> dict:
        """
            This function effectively creates a dictionary that includes only the 
            attributes of the object that correspond to actual database columns, 
            excluding any SQLAlchemy internal attributes or non-column properties.

            Using the inspect function, it dynamically retrieves the mapping 
            information of the object's class, focusing on the attributes that 
            represent database columns.
        """
        return { 
            attr.key : getattr(obj, attr.key) 
            for attr in inspect(obj.__class__).mapper.column_attrs 
        }


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