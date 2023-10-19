from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time as tm
import csv
from lxml import etree
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from datetime import datetime, timezone, timedelta


def main():
    driver = set_up()

    driver.get("https://energy.uwo.ca/enteliweb/earthright#/campus")
    tm.sleep(5)  # Wait for page to load
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/navigation/header/nav/ul/li[2]').click()

    for i in range(77):
        building_values = scrape_building(driver)
        write_to_csv(building_values)


def scrape_building(driver):

    tm.sleep(2)
    building = get_values(driver)

    # Click the down button
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div["
                                                                              "2]/ui-view/div/section/article[2]/div["
                                                                              "1]/img[2]"))).click()
    except StaleElementReferenceException:
        pass

    tm.sleep(2)

    # Click on top result
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/article[2]/div[1]/div[1]').click()

    print(building)

    return building


def get_values(driver):
    """
    Gets the values of electricity, steam and water
    """
    soup = BeautifulSoup(driver.page_source, "lxml")
    dom = etree.HTML(str(soup))

    name = dom.xpath("/html/body/div[1]/div/div[2]/ui-view/div/section/article[2]/div[1]/div[1]/h1/text()")[0]

    if driver.find_elements(By.CSS_SELECTOR, 'gauge-widget[resource-name="TXID_WEB_EARTHRIGHT_ELECTRIC"]'):
        tm.sleep(2)
        electricity = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/article['
                                                    '1]/ul/li[1]/div/gauge-widget')
        try:
            electricity = (electricity.text.split('\n'))[-3]
        except IndexError:  # should not occur
            electricity = None
    else:
        electricity = None

    if driver.find_elements(By.CSS_SELECTOR, 'gauge-widget[resource-name="TXID_WEB_EARTHRIGHT_STEAM"]'):
        tm.sleep(2)
        if electricity:
            steam = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/article[1]/ul/li['
                                                  '2]/div/gauge-widget')
        else:
            steam = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/article[1]/ul/li['
                                                  '1]/div/gauge-widget')
        try:
            steam = (steam.text.split('\n'))[-3]
        except IndexError:
            steam = None
    else:
        steam = None

    if driver.find_elements(By.CSS_SELECTOR, 'gauge-widget[resource-name="TXID_WEB_EARTHRIGHT_WATER"]'):
        tm.sleep(2)

        if not steam and not electricity:
            water = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/article[1]/ul/li['
                                                  '1]/div/gauge-widget')
        elif not (electricity and steam):
            water = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/article[1]/ul/li['
                                                  '2]/div/gauge-widget')
        else:
            water = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/article[1]/ul/li['
                                                  '3]/div/gauge-widget')
        try:
            water = (water.text.split('\n'))[-3]
        except IndexError:
            water = None
    else:
        water = None

    components = [electricity, steam, water]
    for component in components:
        try:
            remove_comma(component)
        except TypeError:
            pass
        except AttributeError:
            pass

    building = [name, electricity, steam, water]
    return building


def set_up():
    """
    A function that sets up the Selenium web driver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("enable-automation")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-gpu")
    options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(options=options)
    return driver


def create_time():
    """
    Gets the current date and time in a usable format
    """
    timezone_offset = -4.0  # Eastern Daylight Time (UTC-4:00)
    tzinfo = timezone(timedelta(hours=timezone_offset))
    now_date = datetime.now(tzinfo).strftime("%Y-%m-%d")
    now_time = datetime.now(tzinfo).strftime("%H:%M")
    return now_date, now_time


def remove_comma(string):
    """
    Removes the commas in numbers.
    """
    return string.replace(",", "")


def write_to_csv(building_values):
    """
    Writes the date, time, electricity and water usage to a CSV file.
    """
    print("csv: ", building_values)
    name, electricity, steam, water = building_values
    now_date, now_time = create_time()
    row = [now_date, now_time, name, electricity, steam, water]
    with open('building_data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)


main()
