import pytest
sys.path.append('../code')
from scraper_new import Scraper as s
from driver import Driver
import urllib
import bs4

def setup():
    self.driver = Driver.get_driver()
    
    self.s = s(dir_lst)

def get_results():
    url = https://angel.co/companies?
    mock_html_path = './mock/html.txt'
    mock_results = urllib.urlretrieve(url, mock_html_path)

def test_get_results():
    assert(s.get_results(self.driver) == mock_results)
