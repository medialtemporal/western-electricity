from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, timezone, timedelta
import time as tm
import csv
from lxml import etree


def main():
    driver = set_up()
    all_electricity, all_water, all_steam = get_values(driver)  # whole campus
    now_date, now_time = create_time()
    write_to_csv(now_date, now_time, all_electricity, all_water, all_steam)


def set_up():
    """
    A function that sets up the Selenium web driver
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver


def get_values(driver):
    """
    Gets the values of electricity, steam and water
    """
    driver.get("https://energy.uwo.ca/enteliweb/earthright#/campus")
    tm.sleep(10)  # Wait for page to load
    soup = BeautifulSoup(driver.page_source, "lxml")
    dom = etree.HTML(str(soup))
    all_electricity = dom.xpath(
        '/html/body/div[1]/div/div[2]/ui-view/div/section/section/article/gauge-widget/div/div[2]/h2/text()')[0]

    driver.find_element(
        By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/section/article/ul/li[2]').click()  # click on steam
    tm.sleep(2)
    soup = BeautifulSoup(driver.page_source, "lxml")
    dom = etree.HTML(str(soup))
    all_steam = dom.xpath(
        '/html/body/div[1]/div/div[2]/ui-view/div/section/section/article/gauge-widget/div/div[2]/h2/text()')[0]

    driver.find_element(
        By.XPATH, '/html/body/div[1]/div/div[2]/ui-view/div/section/section/article/ul/li[3]').click()  # click on water
    tm.sleep(2)
    soup = BeautifulSoup(driver.page_source, "lxml")
    dom = etree.HTML(str(soup))
    all_water = dom.xpath(
        '/html/body/div[1]/div/div[2]/ui-view/div/section/section/article/gauge-widget/div/div[2]/h2/text()')[0]

    return remove_comma(all_electricity), remove_comma(all_steam), remove_comma(all_water)


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


def write_to_csv(now_date, now_time, all_electricity, all_water, all_steam):
    """
    Writes the date, time, electricity and water usage to a CSV file.
    """
    row = [now_date, now_time, all_electricity, all_water, all_steam]
    with open('data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(row)


main()
