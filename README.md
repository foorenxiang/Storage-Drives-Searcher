# Storage-Drives-Searcher
Catalog multiple external drives. Fuzzy search a file to find the right drive!

## Setup
1. git clone https://github.com/foorenxiang/Storage-Drives-Searcher
2. cd Storage-Drives-Searcher
3. python3 -m venv venv
4. source venv/bin/activate (Always call this when using the utilities)
5. pip3 install -r requirements.txt

## Utilities (Currently supporting mac, other OS coming soon):
1. USB Drive Cataloguer: python3 -m Cataloger/CatalogDrive.py
2. Catalog Reading Utility: python3 -m Cataloger/ReadCatalog.py
3. Fuzzy search a file to identify the drive and path it is sitting at: python3 -m Cataloger/FileSearcher.py
