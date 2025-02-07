
from parsers.website.price.deliveroo.deliveroo import DeliverooPriceParser
from database.database import DataBase


import time
from datetime import datetime

from multiprocessing import Pool
import pandas as pd
from functools import wraps
class DeliverooPriceController():

    def __init__(self):
        data_for_scraping = next(next(self.get_data_for_scraping())).iterrows()

        with Pool(processes=1) as pool:
            pool.map(self.scraping, data_for_scraping)

    def get_data_for_scraping(self) -> pd.DataFrame:
        for df in DataBase().get_table('deliveroo_list_urls', chunksize=100):
            yield df


    def __start_scraping(function):
        @wraps(function)
        def wrapper(self, data):
            try:
                _, row = data
                url = row['url']
                post_code_for_search = row['post_code']
                city = row['city']
                function(self, url, post_code_for_search, city)
            except Exception as ex:
                print(ex)
        return wrapper


    @__start_scraping
    def scraping(self, url, post_code_for_search, city):
        date = datetime.now().strftime("%d.%m.%Y")

        with DeliverooPriceParser(url = url) as parser:
            name_place = parser.get_name_place()
            brand = parser.get_brand()

            address = parser.get_address(city)
            post_code = parser.get_post_code(address)



            # time.sleep(3333)
            cards = parser.get_item_cards()
            for card in cards:
                parser.scrolling_page(card)

                price = parser.get_price(card)
                description = parser.get_description(card)
                calories = parser.get_calories(card)
                image_url = parser.get_image_url(card)
                html_card = parser.get_html_card(card)
                title_item = parser.get_title_item(card)

                category = parser.get_category(card)

                parser.modal_window(card)

                print(f'base price     ===============================================  {parser.base_price}')
                print(f'price     ===============================================  {parser.prices}')
                print(f'name size     ===============================================  {parser.sizes}')


                # for price, size in [[(parser.base_price, '')], zip(parser.prices, parser.sizes)][[parser.base_price]<parser.prices]:
                for price, size in zip(parser.prices, parser.sizes):
                    data ={
                            'start_date': date,
                            'end_date': '',
                            'brand': brand,
                            'address': address,
                            'city': city,
                            'post_code': post_code,
                            'segment': '',
                            'category': category,
                            'category_2': size,
                            'category_3': '',
                            'category_4': '',
                            'item': title_item,
                            'source': 'https://deliveroo.co.uk',
                            'region': 'UK',
                            'price': price,
                            'status': 'on',
                            'picture': image_url,
                            'html_cards': html_card,
                            'post_code_address': post_code_for_search,
                            'description': description,
                            'calories': calories,
                            'name_place': name_place,
                            'url': url,
                        }


                    data_frame = pd.DataFrame(data, index=[0])
                    self.to_stg_db(data_frame, 'STG_DELIVEROO_HTML_CARDS')


    def to_stg_db(self, data_frame, name_stg_table):
        DataBase().to_stg_table(data_frame= data_frame, name_stg_table=name_stg_table)

