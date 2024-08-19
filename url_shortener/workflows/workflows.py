import secrets
import url_shortener.models.short_url as models
import url_shortener.schema.short_url as schema
from ..utils.database import SessionLocal
from ..config import get_settings


BASE_URL = get_settings().base_url + "/shortUrls"

# Class that handles the workflows of URL shortener
class UrlShortenerWorkflow:
    # Contains possible chars: a-zA-Z0-9
    char_set: str = ""

    def __init__(self):
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
            db: SessionLocal,
            url: models.UrlBase) -> models.ShortUrlBase:

        url_hash = await UrlShortenerWorkflow.generate_hash_key()

        # an url hash key is only accepted if it is unique,
        # incase there is already a key, generate another one
        while await UrlShortenerWorkflow.get_short_url_by_hash(db, url_hash):
            url_hash = UrlShortenerWorkflow.generate_hash_key()

        short_url = await UrlShortenerWorkflow.insert_short_url(
            long_url=url.long_url,
            url_hash=url_hash,
            db=db)

        # NOTE: We are returning an object of `models.ShortUrlBase` and not
        # of DB schema `schema.ShortUrl`. Pydantic is able to perform the
        # validation of data since we add the required field (short_url)
        # necessary to have an instance of `models.ShortUrlBase` and marked the
        # pydantic model with following (allows it to interpret ORM class):
        # ```
        #    class Config:
        #        from_attributes = True
        # ```
        short_url.short_url = BASE_URL + "/" + short_url.url_hash

        return short_url

    async def insert_short_url(
        long_url: str,
        url_hash: str,
        db: SessionLocal
    ) -> schema.ShortUrl:

        short_url = schema.ShortUrl(
            long_url=long_url,
            url_hash=url_hash)

        db.add(short_url)
        db.commit()
        db.refresh(short_url)

        return short_url

    # Gets an DB schema ShortUrl object
    async def get_short_url_by_hash(
        db: SessionLocal,
        url_hash: str
    ) -> schema.ShortUrl | None:
        url = (
            db.query(schema.ShortUrl)
            .filter(
                schema.ShortUrl.url_hash == url_hash,
                schema.ShortUrl.is_active)
            .first()
        )

        return url
