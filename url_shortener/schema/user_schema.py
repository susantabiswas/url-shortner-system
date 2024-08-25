from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    fullname: str


class UserCreate(UserBase):
    password: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "test@gmail.com",
                "fullname": "Test User",
                "password": "test123"
            }
        }


# For public facing response
class UserDetails(UserBase):
    user_id: int
    is_active: bool = True

    class Config:
        from_attributes = True


# For internal usage
class UserInternal(UserDetails):
    hashed_password: str

    class Config:
        from_attributes = True
