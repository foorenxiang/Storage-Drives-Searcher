import sys
import os
from pathlib import Path

sys.path.append(str(Path(os.getcwd()) / "src"))
from src.fastapi import app
from src.fastapi.routes_definition.drives_list import drives_list
from src.fastapi.routes_definition.drive_contents import drive_contents
from src.fastapi.routes_definition.search import search
from src.fastapi.routes_definition.delete_drive import delete_drive

__all__ = [
    "delete_drive_endpoint",
    "drive_contents_endpoint",
    "drives_list_endpoint",
    "search_endpoint",
    "app",
]


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
