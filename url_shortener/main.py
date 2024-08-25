from fastapi import Depends, FastAPI
from url_shortener.api import short_urls, users, auth
from url_shortener.utils.database import db_manager, Base
from url_shortener.config import get_settings
import uvicorn

app = FastAPI()

app.include_router(auth.oauth2_router)
app.include_router(
    short_urls.shorturl_router)
app.include_router(users.user_router)

# Create the associated ORM tables
db_manager.create_tables()


@app.get("/")
async def root():
    return "Welcome to URL shortener."


if __name__ == "__main__":
    uvicorn.run("url_shortener.main:app", host="0.0.0.0", port=8002, reload=True)