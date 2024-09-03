from contextlib import contextmanager
from typing import Annotated
from fastapi import Depends
from url_shortener.dao.dao_base import ShortUrlDaoBase
from url_shortener.models.short_url_model import ShortUrl
from sqlalchemy.orm import Session
from sqlalchemy import delete
from url_shortener.exceptions import exceptions
from url_shortener.utils.database import db_manager


class ShortUrlDao(ShortUrlDaoBase):
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

    async def insert(self, long_url: str, url_hash: str) -> ShortUrl:
        with self.session_scope() as db:
            short_url = ShortUrl(long_url=long_url, url_hash=url_hash)

            db.add(short_url)
            db.flush()
            db.refresh(short_url)

            # Dev Note: Since we are using a session in the context manager scope,
            # we need to return a new instance of the ShortUrl model
            # explicitly to avoid the issue of the model being deleted when the session is closed
            # when the scope of context manager ends.
            return ShortUrl(id=short_url.id, long_url=short_url.long_url, url_hash=short_url.url_hash)


    async def get_by_url_hash(self, url_hash: str) -> ShortUrl | None:
        with self.session_scope() as db:
            url = (
                db.query(ShortUrl)
                    .filter(
                        ShortUrl.url_hash == url_hash,
                        ShortUrl.is_active
                    )
                .first()
            )

            return url


    async def delete_by_url_hash(self, url_hash: str) -> None:
        with self.session_scope() as db:
            rows = db.query(ShortUrl).filter(ShortUrl.url_hash == url_hash).delete()
            
            if rows == 0:
                exceptions.not_found_exception(url_hash)

        print(f"URL key: {url_hash} deleted.")


def get_shorturl_dao(db: Session = Depends(get_db)) -> ShortUrlDao:
    return ShortUrlDao(db)

