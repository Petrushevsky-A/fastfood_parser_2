

# from parser.address.google_maps.google_maps import parse

# from parser.promo.hotukdeals.hotukdeals import *

from parsers.promo.hotukdeals.hotukdeals import HotukdealsParser


from database.database import DataBase
import os
if __name__ == '__main__':
    db = DataBase()
    # print(db.get_urls())

    HotukdealsParser()