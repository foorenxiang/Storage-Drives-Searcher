import sys
import os
from pathlib import Path
from fastapi import FastAPI


sys.path.append(str(Path(os.getcwd()) / "src"))
from src.fastapi.config import Config
from src.fastapi.routes import create_routes


app = FastAPI(**Config.FASTAPI)
app.add_middleware(**Config.MIDDLEWARE)
app.mount(**Config.STATIC_FILES)
create_routes(app)
