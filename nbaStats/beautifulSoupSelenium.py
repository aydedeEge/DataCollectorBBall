import os
from bs4 import BeautifulSoup
from selenium import webdriver

URL = "https://stats.nba.com/player/201939/boxscores-traditional/?Season=2016-17&SeasonType=Regular%20Season"

driver = webdriver.Chrome(f'{os.getcwd()}/chromedriver')
driver.get(URL)

html = driver.page_source

soup = BeautifulSoup(html)

steph_currey_game_1 = soup.tbody.find("tr", {"index": 0})

print(steph_currey_game_1)