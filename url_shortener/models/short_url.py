from pydantic import BaseModel


# Base class to represent a Url
class UrlBase(BaseModel):
    long_url: str
    description: str = None


# Class to represent the URL request for shortening
class UrlCreate(UrlBase):
    pass


# Class to represent the short Url without extra data
class ShortUrlBase(UrlCreate):
    short_url: str

    # This allows pydantic to accept the ORM class object
    # with matching fields. Useful when we want to return the
    # ORM DB row as the response, we don't have to create an instance
    # explicitly of this class and set each field's value from ORM
    # DB object
    class Config:
        from_attributes = True


# Class to represent the short URL with additional data
class ShortUrl(ShortUrlBase):
    is_active: bool = True
    clicks: int = 0

    class Config:
        from_attributes = True
