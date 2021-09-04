import sys
import os
from pathlib import Path
from typing import Optional

sys.path.append(str(Path(os.getcwd()) / "src"))

from src.ReadCatalog import CatalogReader


def get_drive_descriptors():
    return CatalogReader().drive_descriptors


def drive_contents(*, **kwargs) -> dict:
    drive_name = kwargs.get("drive_name")
    
    drive_descriptors = get_drive_descriptors()
    
    no_drive_stated = drive_name is None
    if no_drive_stated:
        return drive_descriptors
    
    drive_descriptor = drive_descriptors.get(drive_name)
    drive_exists = drive_descriptor is None
    if drive_exists:
        return drive_descriptor
    
    no_drive_response = {drive_name: dict()}
    return no_drive_response
