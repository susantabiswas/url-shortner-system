from url_shortener.dao.dao_base import ShortUrlDaoBase
from url_shortener.models.short_url_model import ShortUrl
from sqlalchemy.orm import Session
from sqlalchemy import delete
from url_shortener.exceptions import exceptions


class ShortUrlDao(ShortUrlDaoBase):
    def __init__(self, db: Session):
        self.db = db


    async def insert(self, long_url: str, url_hash: str) -> ShortUrl:
        short_url = ShortUrl(long_url=long_url, url_hash=url_hash)

        self.db.add(short_url)
        self.db.commit()
        self.db.refresh(short_url)
        return short_url


    async def get_by_url_hash(self, url_hash: str) -> ShortUrl | None:
        url = (
            self.db.query(ShortUrl)
                .filter(
                    ShortUrl.url_hash == url_hash,
                    ShortUrl.is_active)
                .first()
        )

        if not url:
            exceptions.not_found_exception(url_hash)
            
        return url


    async def delete_by_url_hash(self, url_hash: str) -> None:
        rows = self.db.query(ShortUrl).filter(ShortUrl.url_hash == url_hash).delete()
        
        if rows == 0:
            exceptions.not_found_exception(url_hash)
        self.db.commit()

        print(f"URL key: {url_hash} deleted.")
