import logging
from pathlib import Path
import os
import sys

sys.path.append(os.getcwd())

from src.utils.SingletonMeta import SingletonMeta

logger = logging.getLogger(__name__)

_OS_HD_LIST = ["Macintosh HD", "C", "com.apple.TimeMachine"]
_OS_MOUNT_POINT = Path("/Volumes")


class Initializer(metaclass=SingletonMeta):
    def __init__(self, catalog_drives=True):
        self.app_folder = Path.home() / ".Storage Drive Searcher"
        self.catalogs_path = self.app_folder / "drive_catalogs"
        self.os_drives_mounting_point = _OS_MOUNT_POINT
        self.hd_list = _OS_HD_LIST

        self.app_folder.mkdir(exist_ok=True)

        if catalog_drives:
            self._detect_drives()
            self._warn_unsupported_drives_count()
            self.create_catalog_path()

    def create_catalog_path(self):
        self.catalogs_path.mkdir(exist_ok=True)

    def _detect_drives(self) -> None:
        self.drivenames = [
            drivepath.stem
            for drivepath in self.os_drives_mounting_point.glob("*")
            if drivepath.stem not in self.hd_list
        ]
        self._print_detected_drives()

    def _warn_unsupported_drives_count(self):
        detected_drive_count = len(self.drivenames)
        if detected_drive_count == 0:
            print("Did not detect any external drives.")
            print("Exiting...")
            sys.exit()

        if detected_drive_count > 0:
            logger.warning(f"{detected_drive_count} external drives detected!\n")
            continue_ = input(
                "Would you like to catalog all detected drives? (y, yes): "
            )
            if continue_.lower() not in ["y", "yes"]:
                print("Exiting...")
                sys.exit()
            return

    def _print_detected_drives(self):
        if len(self.drivenames) > 0:
            print("Drive(s) detected:")
            [print(drive_path) for drive_path in self.drivenames]
