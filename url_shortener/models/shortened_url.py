from pydantic import BaseModel


class ShortenedUrl(BaseModel):
    short_url: str = None
    long_url: str
    is_active: bool = None
    clicks: int = None
    description: str = None

    class Config:
        from_attributes = True
