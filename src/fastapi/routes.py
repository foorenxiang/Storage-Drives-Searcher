import sys
import os
from pathlib import Path
from fastapi import FastAPI

sys.path.append(str(Path(os.getcwd()) / "src"))
from src.fastapi.routes_definition.drives_list import drives_list
from src.fastapi.routes_definition.drive_contents import drive_contents
from src.fastapi.routes_definition.search import search
from src.fastapi.routes_definition.delete_drive import delete_drive


def create_routes(app: FastAPI):
    @app.get("/drives-list")
    def drives_list_endpoint() -> dict:
        return drives_list()

    @app.get("/catalog-{drive_name}")
    def drive_contents_endpoint(drive_name: str) -> dict:
        return drive_contents(drive_name)

    @app.post("/search")
    def search_endpoint(search_str: str) -> dict:
        return search(search_str)

    @app.delete("/delete_drive")
    def delete_drive_endpoint(drive_name: str) -> dict:
        return delete_drive(drive_name)

    return (
        drives_list_endpoint,
        drive_contents_endpoint,
        search_endpoint,
        delete_drive_endpoint,
    )
