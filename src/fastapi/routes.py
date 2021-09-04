import sys
import os
from pathlib import Path
from types import FunctionType
from typing import Tuple
from fastapi import FastAPI

sys.path.append(str(Path(os.getcwd()) / "src"))
from src.fastapi.routes_definition.drives_list import drives_list
from src.fastapi.routes_definition.drive_contents import drive_contents
from src.fastapi.routes_definition.search import search
from src.fastapi.routes_definition.delete_drive import delete_drive
from typing import Optional


def _catalog_functions(*funcs: Tuple[FunctionType]):
    return tuple(func.__name__ for func in funcs)


def create_routes(app: FastAPI):
    @app.get("/drives-list")
    def drives_list_endpoint() -> dict:
        return drives_list()

    @app.get("/catalog")
    def drive_contents_endpoint(drive_name: Optional[str] = None) -> dict:
        return drive_contents(drive_name)

    @app.post("/search")
    def search_endpoint(search_str: str) -> dict:
        return search(search_str)

    @app.delete("/delete_drive")
    def delete_drive_endpoint(drive_name: str) -> dict:
        return delete_drive(drive_name)

    return _catalog_functions(
        drives_list_endpoint,
        drive_contents_endpoint,
        search_endpoint,
        delete_drive_endpoint,
    )
