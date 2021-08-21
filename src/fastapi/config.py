from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


class Config:
    MIDDLEWARE = {
        "middleware_class": CORSMiddleware,
        "allow_origins": ["http://localhost:3000", "localhost:3000"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    FASTAPI = {
        "title": "Storage Drives Searcher API",
        "docs_url": "/swagger",
        "swagger_ui_oauth2_redirect_url": "/swagger/auth",
    }
    STATIC_FILES = {
        "path": "/",
        "app": StaticFiles(directory="src/fastapi/static"),
        "name": "static",
    }
