import secrets
from url_shortener.schema import short_url_schema
from url_shortener.models import short_url_model
from url_shortener.models import user_model
from url_shortener.schema import user_schema, auth_schema
from sqlalchemy.orm import Session
from url_shortener.config import get_settings
from url_shortener.dao.dao_base import DaoBase, ShortUrlDaoBase, UserDaoBase
from url_shortener.dao.short_url_dao import ShortUrlDao, get_shorturl_dao
from url_shortener.dao.user_dao import UserDao, get_user_dao
from passlib.context import CryptContext
from url_shortener.exceptions import exceptions
from fastapi import Request, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt

BASE_URL = get_settings().base_url + "/shortUrls"
JWT_SECRET_KEY = get_settings().jwt_secret_key
JWT_TOKEN_EXPIRY_IN_MINUTES = get_settings().jwt_token_expiry_in_minutes
JWT_ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Class that handles the workflows of URL shortener
class UrlShortenerWorkflow:
    # Contains possible chars: a-zA-Z0-9
    char_set: str = ""

    def __init__(self):
        # To perform the DB operations, we use the DAO object
        # for ShortUrl model
        self.shorturl_dao: ShortUrlDaoBase = get_shorturl_dao()
        
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

    async def get_short_url_by_hash(self, url_hash: str):
        url = await self.shorturl_dao.get_by_url_hash(url_hash)
        if not url:
            exceptions.not_found_exception(url_hash)
        return url


    async def delete_by_url_hash(self, url_hash: str):
        return await self.shorturl_dao.delete_by_url_hash(url_hash)


class UserWorkflow:
    def __init__(self):
        self.user_dao: UserDaoBase = get_user_dao()

    async def get_user(self, user_id: int) -> user_model.User:
        user = await self.user_dao.get_by_user_id(user_id)
        return user

    async def create_user(self, user: user_schema.UserCreate) -> user_model.User:
        if await self.user_dao.get_user_by_email(user.email):
            exceptions.already_exists_exception(user.email)

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

    @staticmethod
    async def validate_password(plain_pwd: str, hashed_pwd: str):
        return pwd_context.verify(plain_pwd, hashed_pwd)


class OAuthWorkflow(HTTPBearer):
    # OAuth2
    # 1. fetch username and pwd from request
    # 2. check if user exists
    # 3. validate pwd for valid user
    # 4. if valid, generate and return a JWT token with updated TTL expiry

    def __init__(self, auto_error: bool = True):
        super(OAuthWorkflow, self).__init__(auto_error=auto_error)
        self.user_dao: UserDaoBase = UserDao()

    # Callable, when the object is called, then this will fetch the user
    # corresponding to the JWT token. In case the token is invalid, exception is raised
    # using this, we can directly use this class as a dependency in the FastAPI routes
    async def __call__(self, request: Request):
        self.user_dao: UserDaoBase = UserDao()
        credentials: HTTPAuthorizationCredentials = await super(OAuthWorkflow, self).__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Invalid Authorization token.")

        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Invalid Authentication scheme.")

        user = await self.get_current_user(credentials.credentials)
        return user


    # Creates a JWT token
    @staticmethod
    async def create_jwt_access_token(payload: dict):
        jwt_expiry = datetime.utcnow() + \
            timedelta(minutes=JWT_TOKEN_EXPIRY_IN_MINUTES)

        payload['exp'] = jwt_expiry
        jwt_token = jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return jwt_token


    async def authenticate(self, username: str, plain_password: str) -> auth_schema.Token:
        # Check if the user exists
        user = await self.user_dao.get_user_by_email(username)

        # Dev Note: Don't throw exception specifying that the user doesnt
        # exists, as that can acts as a predicate for checking if an email
        # exists in case of a brute force attack by an attacker
        if not user or \
            (not await AuthWorkflow.validate_password(plain_password, user.hashed_password)):
            raise HTTPException(
                status_code=401, 
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"})

        # Generate a JWT token for the valid user
        jwt = await OAuthWorkflow.create_jwt_access_token({"sub": username})
        return auth_schema.Token(access_token=jwt, token_type="bearer")


    async def get_current_user(self, token: auth_schema.Token) -> user_model.User:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            expiry = payload.get("exp")
            if expiry is None or expiry < datetime.utcnow().timestamp():
                raise HTTPException(status_code=401, detail="Token is expired")

        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        print(f"JWT decoded for username: {username}")
        user = await self.user_dao.get_user_by_email(username)

        if user is None:
            raise HTTPException(status_code=404, detail=f"JWT User {username} not found")

        print(f"User: {username} authenticated")
        return user


