import logging
from json.decoder import JSONDecodeError
from pathlib import Path
import json
from icecream import ic
from from_root import from_root
from datetime import datetime
import sys
import glob
import shutil
from SingletonMeta import SingletonMeta

logger = logging.getLogger(__name__)

# RX: TODO: Refactor into smaller, single responsibility classes
class Cataloger(metaclass=SingletonMeta):
    def __init__(self):
        self._set_drives_root()
        self._detect_drives()
        self._warn_unsupported_drives_count()
        self._set_selected_drive_path()
        self._read_current_catalog()
        self._manifest_overwriting_protection_check(self.current_catalog)
        self._set_cataloging_time()
        self._catalog_files()
        self.update_existing_catalog()

    def _set_drives_root(self) -> None:
        self.os_drive_root = Path("/Volumes")

    def _detect_drives(self) -> None:
        self.hd_list = ["Macintosh HD"]
        self.drivepaths = [
            drivepath.stem
            for drivepath in self.os_drive_root.glob("*")
            if drivepath.stem not in self.hd_list
        ]

    def _warn_unsupported_drives_count(self):
        if len(self.drivepaths) != 1:
            logger.error("More than 1 external drives detected!")
            sys.exit()

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

    def _set_selected_drive_path(self):
        self.drivepath = self.os_drive_root / self.drivepaths[0]

    def _read_current_catalog(self):
        print(f"{self.drivepath} detected, cataloging it!")
        try:
            self.output_file = from_root("") / "catalog.json"
            try:
                with open(self.output_file, "r", encoding="UTF-8") as fp:
                    self.current_catalog = json.load(fp)
            except JSONDecodeError:
                self.current_catalog = dict()

            if not isinstance(self.current_catalog, dict):
                ic("No current catalog found, creating new empty catalog")
                self.current_catalog = dict()

        except FileNotFoundError:
            ic("No current catalog found, creating new empty catalog")
            self.current_catalog = dict()

    def _catalog_files(self):
        print(f"Cataloging files on {self.drivepath.stem} as of {self.cataloging_time}")
        filepaths = tuple(
            [
                str(Path(path).relative_to(self.drivepath))
                for path in glob.glob(f"{self.drivepath}/**/*", recursive=True)
                if Path(path).is_file
            ]
        )

        if not filepaths:
            logger.error("Failed to find files on drive, is it plugged in?")
            sys.exit()

        ic(filepaths)
        self.filepaths = filepaths

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
            }

            json.dump(self.current_catalog, fp)

        print(f"Finished cataloging {self.drivepath}")


if __name__ == "__main__":
    Cataloger()
