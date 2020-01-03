import pytest
sys.path.append('../code')
from scraper_new import Scraper as s
from driver import Driver

def mock_driver():
    driver = Driver.get_driver()
    return driver

def get_results():
    url = https://angel.co/companies?
    mock_html_path = './mock/html.txt'
    urllib.urlretrieve(url, mock_html_path)
    driver = mock_driver()
    s.get_results(driver)


def test_answer():

