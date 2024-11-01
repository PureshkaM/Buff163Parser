import requests
import time
import os
import datetime
import random

import json
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

def get_data_buff():

    time_difference = datetime.timedelta(days=2)
    if os.path.isfile('cookiesbuff163.pkl'):
        file_path = 'cookiesbuff163.pkl'

        file_time = os.path.getmtime(file_path)

        file_date = datetime.datetime.fromtimestamp(file_time)

        current_date = datetime.datetime.now()

        time_difference = current_date - file_date

    if (not os.path.isfile('cookiesbuff163.pkl')) or (not time_difference < datetime.timedelta(days=1)):
        driver = webdriver.Chrome()

        driver.get(
            'https://buff.163.com/account/login?back_url=/market/steam_inventory%3Fgame%3Dcsgo#page_num=1&page_size=50&search=&state=all')
        try:
            element = WebDriverWait(driver, 1000).until(
                EC.presence_of_element_located((By.ID, 'j_mybuying'))
            )
            with open('cookiesbuff163.pkl', 'wb') as f:
                pickle.dump(driver.get_cookies(), f)
            driver.quit()
        except:
            print("Error")
            return 0

    session = requests.Session()
    with open('cookiesbuff163.pkl', 'rb') as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

    result = []

    offset = 0
    size_list = 20
    page = 1
    control = 0
    counter = 0
    while True:
        print("Page: " + str(page) + "\n")
        for item in range(offset, offset + size_list, size_list):
            response = session.get(
                url=(f"https://buff.163.com/api/market/goods?game=csgo&page_num={str(page)}&tab=selling&use_suggestion=0&_=1710077203803"),
                timeout=10
            )

            if response.status_code != 200:
                print("Site error! Chilling...\n")
                time.sleep(random.randint(13, 15))
                continue

            offset += size_list
            page += 1
            resp = response.json()
            data = resp.get('data')
            if data is None:
                page -= 1
                offset -= size_list
                counter += 1
                print("Data error! Trying again...")
                if counter >= 3:
                    break
                continue
            else:
                counter = 0
                items = data.get('items')
                control = len(items)
                for i in items:
                    result.append(
                        {
                            'name': i.get('market_hash_name'),
                            'price': i.get('sell_min_price'),
                            'url': i.get('steam_market_url')
                        }
                    )

        time.sleep(random.randint(1, 3))
        if control < size_list:
            break
    with open("resultbuff163.json", "w", encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    return len(result)


def main():
    buff163 = get_data_buff()
    if buff163 == 0:
        return 0
    df1 = pd.DataFrame()
    df1.to_excel('buff163.xlsx', index=False)

    with open('resultbuff163.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.read_excel('buff163.xlsx')

    count = 1
    for item in data:
        df.at[count, 'Items name'] = item['name']
        df.at[count, 'Link'] = item['url']
        df.at[count, 'Price'] = item['price']
        count+=1

    df.to_excel('buff163.xlsx', index=False)


if __name__ == '__main__':
    main()