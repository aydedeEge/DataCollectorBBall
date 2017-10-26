import os
import time
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from load_config import read_config, set_env_vars
from pymysqlconnect import PyMySQLConn

class WebPage:

    tag_attribute_dict = {
        "id": "getElementById",
        "class": "getElementsByClassName",
    }

    def __init__(self):
        self.driver = webdriver.Chrome('{path}/chromedriver'.format(path=os.getcwd()))

    def load_page(self, url):
        self.url = url
        self.driver.get(self.url)
    
    def get_page(self):
        return self.driver.page_source

    # Must call load_page at least once before
    def dom_change_event_class(self, tag_attribute, tag_attribute_value, new_value):
        tag_attr_command = "getElementsByClassName"

        a = 0
        while a < 11:
            try:
                # Need to change the first line of execute_script; [0] hard coded
                self.driver.execute_script('''
                    var el = document.{tag_attr_command}("{tag_attribute_value}")[0];
                    el.value = "{new_value}";
                    var event = document.createEvent("HTMLEvents");
                    event.initEvent("change", true, false);
                    el.dispatchEvent(event);
                '''.format(tag_attr_command=tag_attr_command, tag_attribute_value=tag_attribute_value, new_value=new_value))
                break
                
            except Exception as e:
                time.sleep(1)
                a+=1
                print('Page not loaded, attempt number: {a}'.format(a=a))
                if a < 10:
                    continue