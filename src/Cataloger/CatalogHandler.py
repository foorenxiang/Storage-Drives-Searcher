import logging
from json.decoder import JSONDecodeError
import json
from pathlib import Path
from from_root import from_root
from datetime import datetime
import os
import sys
import shutil

sys.path.append(os.getcwd())

from src.utils.SingletonMeta import SingletonMeta
from src.Cataloger.Initializer import Initializer
from src.Cataloger.Cataloger import Cataloger

logger = logging.getLogger(__name__)


class CatalogHandler(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.current_catalog = dict()

    def set_cataloging_time(self):
        self.cataloging_time = str(datetime.now())
        print(f"Cataloging files on {self.drivepath.stem} as of {self.cataloging_time}")

    def manifest_overwriting_protection_check(self):
        if self.catalog_file.exists() and self.catalog_file.stat().st_size:
            received_input = input(
                f"Current drive manifest exists ({self.drivepath.stem}), overwrite it? (y, yes) "
            )
            if not received_input.lower() in ("y", "yes"):
                logger.warning("Quitting utility without overwriting")
                sys.exit()

            logger.warning(
                f"Received valid input! Overwriting manifest for {self.drivepath.stem}"
            )
            return

    def read_current_catalog(self):
        try:
            with open(self.catalog_file, "r", encoding="UTF-8") as fp:
                self.current_catalog[self.catalog_file.stem] = json.load(fp)
        except (JSONDecodeError, FileNotFoundError):
            logger.warning("No current catalog found, creating new empty catalog")
            self.current_catalog[self.catalog_file.stem] = dict()

    def update_existing_catalog(self):
        if self.catalog_file.exists():
            shutil.copy(
                self.catalog_file,
                self.catalog_file.parent
                / f"Z_CATALOGER_BACKUP{self.catalog_file.stem}.json",
            )
        with open(self.catalog_file, "w", encoding="utf8") as fp:
            json.dump(
                {
                    "catalogued_date": self.cataloging_time,
                    "paths_and_stats": self.paths_and_stats,
                },
                fp,
            )
        print(f"Finished cataloging {self.drivepath}")

    def catalog_discovered_drives(self):
        for drivename in Initializer().drivenames:
            self.drivepath = Initializer().os_drives_mounting_point / drivename
            self.catalog_file = (
                from_root("")
                / Initializer().catalogs_path
                / f"{self.drivepath.stem}.json"
            )
            self.read_current_catalog()  # TODO
            self.manifest_overwriting_protection_check()
            self.set_cataloging_time()

            self.paths_and_stats = Cataloger().catalog_files(self.drivepath)
            self.update_existing_catalog()

    def read_catalogs(self):
        catalog_files = Initializer(catalog_drives=False).catalogs_path.glob("*.json")
        for catalog_file in catalog_files:
            self.catalog_file = catalog_file
            self.read_current_catalog()
        return self.current_catalog
