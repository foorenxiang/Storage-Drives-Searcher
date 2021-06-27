from json.decoder import JSONDecodeError
from pathlib import Path
import json
from icecream import ic
from from_root import from_root
from datetime import datetime
import sys
import logging
import glob
import shutil


logger = logging.getLogger(__name__)

os_drive_root = Path("/Volumes")

drivepaths = [
    drivepath.stem
    for drivepath in os_drive_root.glob("*")
    if drivepath.stem != "Macintosh HD"
]

if len(drivepaths) != 1:
    logger.error("More than 1 external drives detected!")
    sys.exit()

drivepath = os_drive_root / drivepaths[0]

print(f"{drivepath} detected, cataloging it!")

alternate_drive_name = None

try:
    output_file = from_root("") / "catalog.json"
    try:
        with open(output_file, "r", encoding="UTF-8") as fp:
            current_catalog = json.load(fp)
    except JSONDecodeError:
        current_catalog = dict()

    if not isinstance(current_catalog, dict):
        ic("No current catalog found, creating new empty catalog")
        current_catalog = dict()

except FileNotFoundError:
    ic("No current catalog found, creating new empty catalog")
    current_catalog = dict()


if alternate_drive_name in current_catalog or drivepath.stem in current_catalog:
    received_input = input(
        f"Current drive manifest exists ({alternate_drive_name if alternate_drive_name else drivepath.stem}), overwrite it? (y, yes) "
    )
    if not received_input.lower() in ("y", "yes"):
        logger.warning("Quitting utility without overwriting")
        sys.exit()

    logger.warning(
        f"Received valid input! Overwriting manifest for {alternate_drive_name}"
    )

cataloging_time = str(datetime.now())
print(f"Cataloging files on {drivepath.stem} as of {cataloging_time}")

filepaths = tuple(
    [
        str(Path(path).relative_to(drivepath))
        for path in glob.glob(f"{drivepath}/**/*", recursive=True)
        if Path(path).is_file
    ]
)

if not filepaths:
    logger.error("Failed to find files on drive, is it plugged in?")
    sys.exit()


ic(filepaths)

shutil.copy(output_file, output_file.parent / f"{output_file.stem}_backup.json")

with open(output_file, "w", encoding="utf8") as fp:
    current_catalog[alternate_drive_name or drivepath.stem] = {
        "catalogued_date": cataloging_time,
        "paths": filepaths,
    }

    json.dump(current_catalog, fp)

print(f"Finished cataloging {drivepath}")
