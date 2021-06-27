from from_root import from_root
import json
from icecream import ic

catalog_file = from_root("catalog.json")
drive = "WD_BLACK"

with open(catalog_file, "r") as fp:
    drive_descriptors = json.load(fp)


drives_catalogued = drive_descriptors.keys()

enumerated_drives = tuple(enumerate(drives_catalogued))

items_catalogued = 0
for descriptor in drive_descriptors.values():
    items_catalogued += len(descriptor["paths"])


items_catalogued = 0
for descriptor in drive_descriptors.values():
    items_catalogued += len(descriptor["paths"])
print("\nFiles catalogued:", items_catalogued)
print("\nDrives catalogued:")
# [print(drive) for drive in drives_catalogued]

[print(f"{drive_name}:", enum) for enum, drive_name in enumerated_drives]
selected_drive_index = input("\nSelect drive index to show manifest for: ")

try:
    print("Loading...")
    selected_drive_name = enumerated_drives[int(selected_drive_index)][1]
    ic(drive_descriptors[selected_drive_name])
except IndexError:
    print("Invalid selection!")
