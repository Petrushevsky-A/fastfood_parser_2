import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import pandas as pd
import requests
import numpy as np
from multiprocessing import Pool
from database.database import DataBase
import setting





def parse(arg):
    url, brand = arg
    print(f"PARSED {url}")
    options = Options()
    tuple(map(options.add_argument, setting.SELENIUM['options'].values()))
    path = setting.SELENIUM['path']
    options.add_extension(setting.SELENIUM['extension']['path_proxy_plugin_file'])
    driver = webdriver.Chrome(chrome_options=options, executable_path=path)
    driver.get(url=url)
    time.sleep(3)

    try:
        driver.find_element(By.XPATH, '//button[@data-test-id="accept-all-cookies-button"]').click()
        time.sleep(6)
    except:
        pass


    try:
        name_place = driver.find_element(By.XPATH, '//h1[@data-js-test="restaurant-heading"]').text
        address = driver.find_element(By.XPATH, '//span[@data-js-test="header-restaurantAddress"]').text
        post_code = address.split(',')[-1].strip()
        city = address.split(',')[-2].strip()
    except:
        driver.close()
        driver.quit()
        #
        # temp = url.split('/')[-2]
        # pd.DataFrame({
        #     'url': [url],
        # }).to_excel(f'ERROR_{brand}_{temp}_result_menu_price.xlsx')
        return None

    print(url)
    print(brand)
    print(name_place)
    print(address)
    print(post_code)
    print(city)
    menu_list = []

    categorys = driver.find_elements(By.XPATH, '//h2[@data-test-id="menu-category-heading"]')
    if len(categorys) == 0:
        driver.close()
        driver.quit()
        #
        # pd.DataFrame({
        #     'brand': [brand],
        #     'post_code': [post_code],
        #     'url': [url],
        # }).to_excel(f'ERROR_{brand}_{post_code}_result_menu_price.xlsx')
        return None

    date = datetime.now().strftime("%d.%m.%Y")

    for id_cat, category in enumerate(driver.find_elements(By.XPATH, '//section[@data-test-id="menu-category-item"]/header/button/h2'), 1):
        text_category = category.get_attribute('innerHTML').strip()
        print(text_category)
        if 'Allergen' in text_category or 'Limited' in text_category:
            continue


        for id_food, food in enumerate(driver.find_elements(By.XPATH, f'//section[@data-test-id="menu-category-item"][{id_cat}]//div[@data-js-test="menu-item"]'), 1):



            try:
                name = driver.find_element(By.XPATH, f'//section[@data-test-id="menu-category-item"][{id_cat}]//div[@data-js-test="menu-item"][{id_food}]//h3[@data-js-test="menu-item-name"]').get_attribute('innerHTML').replace("<!---->", "").strip()
            except:
                name = 'Not found'
            print(name)
            try:
                price = driver.find_element(By.XPATH, f'//section[@data-test-id="menu-category-item"][{id_cat}]//div[@data-js-test="menu-item"][{id_food}]//p[@data-js-test="menu-item-price"]').get_attribute('innerHTML').strip()
            except:
                price = 'Not found'
            print(price)
            try:

                image = driver.find_element(By.XPATH, f'//section[@data-test-id="menu-category-item"][{id_cat}]//div[@data-js-test="menu-item"][{id_food}]//div[contains(@class, "c-menuItems-imageContainer")]/img')
                driver.execute_script("arguments[0].scrollIntoView();", image)
                time.sleep(1)
                image_source = image.get_attribute('src')
                directory = f"./{brand}/{name}.png"
                try:
                    reponse_img = requests.get(image_source)
                    if reponse_img.status_code == 200:
                        with open(directory, "wb") as file:
                            file.write(reponse_img.content)
                except:
                    print(f"ERROR {image_source}")
            except:
                image_source = 'Not found'
                directory = 'Not found'
            print(image_source)
            print(directory)
            try:
                description = driver.find_element(By.XPATH,f'//section[@data-test-id="menu-category-item"][{id_cat}]//div[@data-js-test="menu-item"][{id_food}]//p[@data-js-test="menu-item-description"]').get_attribute('innerHTML').replace("<!---->", "").strip()
            except:
                description = 'Not found'
            print(description)
            menu_list.append([brand,name_place,address,city,post_code,text_category, name, price, image_source, directory, description, url, date])

    print(len(menu_list))

    driver.close()
    driver.quit()

    menu_list = np.array(menu_list).T.tolist()


    data = {
        'brand':menu_list[0],
        'name_place':menu_list[1],
        'address':menu_list[2],
        'city':menu_list[3],
        'post_code':menu_list[4],
        'text_category':menu_list[5],
        'name':menu_list[6],
        'price':menu_list[7],
        'image_source':menu_list[8],
        'directory':menu_list[9],
        'description':menu_list[10],
        'url':menu_list[11],
        'date':menu_list[12],
    }

    data_frame = pd.DataFrame(data)
    DataBase().to_stg_table(data_frame=data_frame, name_stg_table='STG_JUST_EATS_PRICE_OLD')

def start_just_eats_price():
    data = DataBase().get_table('just_eats_list')
    urls_brands = []
    next(next(data)).apply(lambda x: urls_brands.append(tuple(x)), axis=1)
    with Pool(processes=5) as p:

        p.map(parse, urls_brands)
