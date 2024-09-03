from pydantic import BaseModel, HttpUrl


# Base class to represent a Url
class UrlBaseSchema(BaseModel):
    long_url: HttpUrl
    description: str = None

    class Config:
        # For swagger spec example
        json_schema_extra = {
            "example": {
                "long_url": "https://www.google.com",
                "description": "Google search engine"
            }
        }


# Class to represent the URL request for shortening
class UrlCreateSchema(UrlBaseSchema):
    pass


# Class to represent the short Url without extra data
class ShortUrlBaseSchema(UrlCreateSchema):
    short_url: str

    # DEV NOTE
    # This allows pydantic to accept the ORM class object
    # with matching fields. Useful when we want to return the
    # ORM DB row as the response, we don't have to create an instance
    # explicitly of this class and set each field's value from ORM
    # DB object
    class Config:
        from_attributes = True


# Class to represent the short URL with additional data
class ShortUrlSchema(ShortUrlBaseSchema):
    is_active: bool = True
    clicks: int = 0

    class Config:
        from_attributes = True
        
