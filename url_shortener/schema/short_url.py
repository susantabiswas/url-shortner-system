from sqlalchemy import Boolean, Column, Integer, String
from ..utils import database


# DB Schema for storing the ShortUrl details.
class ShortUrl(database.Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True)
    # This represents the unique tiny url suffix, which
    # represents the original long URL
    url_hash = Column(String, unique=True, index=True)
    long_url = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
