import logging
import os
import sys

sys.path.append(os.getcwd())

from src.utils.SingletonMeta import SingletonMeta
from src.Cataloger.Initializer import Initializer
from src.Cataloger.CatalogHandler import CatalogHandler

logger = logging.getLogger(__name__)


class CatalogerUtility(metaclass=SingletonMeta):
    def catalog(self):
        Initializer()
        CatalogHandler().catalog_discovered_drives()


if __name__ == "__main__":
    CatalogerUtility().catalog()
