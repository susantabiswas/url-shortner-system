import secrets
from url_shortener.schema import short_url_schema
from url_shortener.models import short_url_model
from url_shortener.models import user_model
from url_shortener.schema import user_schema
from sqlalchemy.orm import Session
from url_shortener.config import get_settings
from url_shortener.dao.dao_base import DaoBase, ShortUrlDaoBase, UserDaoBase
from url_shortener.dao.short_url_dao import ShortUrlDao
from url_shortener.dao.user_dao import UserDao
from passlib.context import CryptContext

BASE_URL = get_settings().base_url + "/shortUrls"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Class that handles the workflows of URL shortener
class UrlShortenerWorkflow:
    # Contains possible chars: a-zA-Z0-9
    char_set: str = ""

    def __init__(self, db):
        # To perform the DB operations, we use the DAO object
        # for ShortUrl model
        self.shorturl_dao: ShortUrlDaoBase = ShortUrlDao(db)
        
        # A-Z
        for ch in range(ord('A'), ord('A') + 26):
            UrlShortenerWorkflow.char_set += chr(ch)

        # a-z
        for ch in range(ord('a'), ord('a') + 26):
            UrlShortenerWorkflow.char_set += chr(ch)

        # 0-9
        for ch in range(ord('0'), ord('0') + 10):
            UrlShortenerWorkflow.char_set += chr(ch)

    # Generates a hash key of desired length
    async def generate_hash_key(len: int = 6):
        return "".join(secrets.choice(
                UrlShortenerWorkflow.char_set) for _ in range(len)
            )

    # Insert a short URL object in DB
    async def create_short_url(
            self,
            url: short_url_schema.UrlBaseSchema) -> short_url_schema.ShortUrlBaseSchema:

        url_hash = await UrlShortenerWorkflow.generate_hash_key()

        # an url hash key is only accepted if it is unique,
        # incase there is already a key, generate another one
        while await self.shorturl_dao.get_by_url_hash(url_hash):
            url_hash = UrlShortenerWorkflow.generate_hash_key()

        short_url = await self.shorturl_dao.insert(
            long_url=url.long_url,
            url_hash=url_hash)

        # NOTE: We are returning an object of `schema.ShortUrlBaseSchema` and not
        # of DB schema `models.ShortUrl`. Pydantic is able to perform the
        # validation of data since we add the required field (short_url)
        # necessary to have an instance of `models.ShortUrlBase` and marked the
        # pydantic model with following (allows it to interpret ORM class):
        # ```
        #    class Config:
        #        from_attributes = True
        # ```
        short_url.short_url = BASE_URL + "/" + short_url.url_hash
        return short_url


    async def delete_by_url_hash(self, url_hash: str):
        return await self.shorturl_dao.delete_by_url_hash(url_hash)


class UserWorkflow:
    def __init__(self, db):
        self.user_dao: UserDaoBase = UserDao(db)

    async def get_user(self, user_id: int) -> user_model.User:
        user = await self.user_dao.get_by_user_id(user_id)
        return user

    async def create_user(self, user: user_schema.UserCreate) -> user_model.User:
        # hash the password before storing it in DB
        hashed_password = AuthWorkflow.get_password_hash(user.password)
        user.password = hashed_password
        user = await self.user_dao.insert(user, hashed_password)
        return user

    async def delete_user(self, user_id: int):
        return await self.user_dao.delete_by_user_id(user_id)


class AuthWorkflow:
    def __init__(self, db):
        self.user_dao: UserDaoBase = UserDaoBase(db)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)