import sys
import os
from pathlib import Path

sys.path.append(str(Path(os.getcwd()) / "src"))

from src.fastapi import app

app
