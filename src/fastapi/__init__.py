import sys
import os
from pathlib import Path
from fastapi import FastAPI
from types import MethodType

sys.path.append(str(Path(os.getcwd()) / "src"))
from src.fastapi.config import config
from src.fastapi.routes import create_routes


app = FastAPI(**config.FASTAPI)
app.add_middleware(**config.MIDDLEWARE)
app.mount(**config.STATIC_FILES)
created_routes = create_routes(app)

print(config.FASTAPI)
print(config.MIDDLEWARE)
print(config.STATIC_FILES)
print(created_routes)
