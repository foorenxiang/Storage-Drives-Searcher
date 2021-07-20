import logging
from json.decoder import JSONDecodeError
from pathlib import Path
import json
from icecream import ic
from from_root import from_root
from datetime import datetime
import os
import sys
import glob
import shutil

sys.path.append(os.getcwd())

from Cataloger.utils.SingletonMeta import SingletonMeta

logger = logging.getLogger(__name__)

OS_HD_LIST = [
    "Macintosh HD",
    "C",
]

OS_MOUNT_POINT = Path("/Volumes")

# RX: TODO: Refactor into smaller, single responsibility classes
class Cataloger(metaclass=SingletonMeta):
    def __init__(self):
        self._set_drives_root()
        self._detect_drives()
        self._warn_unsupported_drives_count()
        self._catalog_discovered_drives()

    def _catalog_discovered_drives(self):
        for drivepath in self.drivepaths:
            self._set_selected_drive_path(drivepath)
            self._get_current_catalog()
            self._manifest_overwriting_protection_check(self.current_catalog)
            self._set_cataloging_time()
            self._catalog_files()
            self.update_existing_catalog()

    def _set_drives_root(self) -> None:
        self.os_drives_mounting_point = OS_MOUNT_POINT

    def _detect_drives(self) -> None:
        self.hd_list = OS_HD_LIST
        self.drivepaths = [
            drivepath.stem
            for drivepath in self.os_drives_mounting_point.glob("*")
            if drivepath.stem not in self.hd_list
        ]
        self._print_detected_drives()

    def _print_detected_drives(self):
        if len(self.drivepaths) > 0:
            print("Drive(s) detected:")
            [print(drive_path) for drive_path in self.drivepaths]

    def _warn_unsupported_drives_count(self):
        detected_drive_count = len(self.drivepaths)
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

    def _set_cataloging_time(self):
        self.cataloging_time = str(datetime.now())

    def _manifest_overwriting_protection_check(self, current_catalog):
        if self.drivepath.stem in current_catalog:
            received_input = input(
                f"Current drive manifest exists ({self.drivepath.stem}), overwrite it? (y, yes) "
            )
            if not received_input.lower() in ("y", "yes"):
                logger.warning("Quitting utility without overwriting")
                sys.exit()

            logger.warning(
                f"Received valid input! Overwriting manifest for {self.drivepath.stem}"
            )

    def _set_selected_drive_path(self, drivepath):
        self.drivepath = self.os_drives_mounting_point / drivepath

    def _get_current_catalog(self):
        print(f"{self.drivepath} detected, cataloging it!")
        try:
            self._resolve_catalog_file_location()
            self._read_catalog_from_file()
            self._verify_read_from_catalog()
        except FileNotFoundError:
            self._handle_no_existing_catalog()

    def _handle_no_existing_catalog(self):
        logger.warning("No current catalog found, creating new empty catalog")
        self._create_new_catalog()

    def _verify_read_from_catalog(self):
        if not isinstance(self.current_catalog, dict):
            logger.warning("No current catalog found, creating new empty catalog")
            self._create_new_catalog()

    def _read_catalog_from_file(self):
        try:
            with open(self.output_file, "r", encoding="UTF-8") as fp:
                self.current_catalog = json.load(fp)
        except JSONDecodeError:
            self.current_catalog = dict()

    def _resolve_catalog_file_location(self):
        self.output_file = from_root("") / "catalog.json"

    def _create_new_catalog(self):
        self.current_catalog = dict()

    def _catalog_files(self):
        print(f"Cataloging files on {self.drivepath.stem} as of {self.cataloging_time}")
        filepaths = list()
        paths_and_stats = list()
        for path in glob.glob(f"{self.drivepath}/**/*", recursive=True):
            if Path(path).is_file:
                path_string = str(Path(path).relative_to(self.drivepath))
                filepaths.append(path_string)
                path = Path(self.drivepath) / path_string
                file_stat = {
                    "path": path_string,
                    "path_size": path.stat().st_size,
                    "path_modified_time": path.stat().st_mtime,
                    "path_accessed_time": path.stat().st_atime,
                }
                paths_and_stats.append(file_stat)

        filepaths = tuple(filepaths)
        paths_and_stats = tuple(paths_and_stats)

        if not filepaths:
            logger.error("Failed to find files on drive, is it plugged in?")
            sys.exit()
        ic(filepaths)
        self.filepaths = filepaths
        self.paths_and_stats = paths_and_stats

    def update_existing_catalog(self):
        if self.output_file.exists():
            shutil.copy(
                self.output_file,
                self.output_file.parent / f"{self.output_file.stem}_backup.json",
            )
        with open(self.output_file, "w", encoding="utf8") as fp:
            self.current_catalog[self.drivepath.stem] = {
                "catalogued_date": self.cataloging_time,
                "paths": self.filepaths,
                "paths_and_stats": self.paths_and_stats,
            }
            json.dump(self.current_catalog, fp)
        print(f"Finished cataloging {self.drivepath}")


if __name__ == "__main__":
    Cataloger()
