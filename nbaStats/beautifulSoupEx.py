#Need to pip install PyQt5 if you want to run
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage

from bs4 import BeautifulSoup
from urllib.request import urlopen
from time import sleep

URL = "https://stats.nba.com/player/201939/boxscores-traditional/?Season=2016-17&SeasonType=Regular%20Season"

class Client(QWebEnginePage):

    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebEnginePage.__init__(self)
        self.html = ''
        self.loadFinished.connect(self._on_load_finished)
        self.load(QUrl(url))
        self.app.exec_()

    def _on_load_finished(self):
        self.html = self.toHtml(self.Callable)
        print('Load Finished')
        
    def Callable(self, html_str):
        self.html = html_str
        self.app.quit()

client_response = Client(URL).html
soup = BeautifulSoup(client_response, "html.parser")

steph_currey_game_1 = soup.tbody.find("tr", {"index": 0})

print(steph_currey_game_1)

# height = soup.find("div", {"class": "player-stats__height"}).span.string

# game_stats = soup.find("div", {"class": "nba-stat-table__overflow"})
# print(game_stats)
