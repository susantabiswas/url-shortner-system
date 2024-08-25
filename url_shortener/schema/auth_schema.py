from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "test@gmail.com",
                "password": "test123"
            }
        }
