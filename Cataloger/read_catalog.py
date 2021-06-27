from from_root import from_root
import json
from icecream import ic

catalog_file = from_root("catalog.json")
drive = "WD_BLACK"

with open(catalog_file, "r") as fp:
    drive_descriptor = json.load(fp)

ic(drive_descriptor[drive])

ic(drive_descriptor.keys())
