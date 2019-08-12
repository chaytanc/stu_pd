#!/usr/bin/python3
# vim: set sw=4 noet ts=4 fileencoding=utf-8:

#XXX !!!!!!!!!!!To Do!!!!!!!!!!!!!!!!!!
#XXX could pass in functions to make more abstract...?
#XXX when funcs are mapped label them as either specific or abstract and try to
#XXX contain specifcs

# For not getting detected as a bot
import random
import time
# Interpreting and formatting html
from bs4 import BeautifulSoup
# For creating directories and files
import os
import sys
# Json and regular expression interpreting
import re
# Displays large datasets?
import pandas as pd
# Dataset interpretation and operations
import numpy as np

# Accessing website for crawling
from selenium import webdriver
# Finds html elements in pages 
from selenium.webdriver.common.by import By
# pauses webdriver
from selenium.webdriver.support.ui import WebDriverWait
# Applies attributes and behaviors to common html things? i.e. click for buttons
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

# Driver class
from driver import Driver
# General Scraper for inheritance
from general_scraper import * 
# Webscraping browser
from driver import Driver


# input filters to use
    # main.py
    # def start(filters, settings):
# start driver (once and then input
    # driver.py

class Scraper():

	def __init__(self, dir_lst):
		# Makes output/debug, output/results
		construct_dir_tree(self, dir_lst)
		#XXX I don't know if self or passing around is better... 
		#self.driver = driver

# apply filters

	# General
	def get_filter_url_appendage(self, filter_dict):

		''' Args:
		filter_dict -- dict containing {'filter_type' : ['selected_filter']}

		Test must be sorted because dict values are appended in unordered way
		
		>>> sorted(s.get_filter_url_appendage(
		... {'locations' : ['1673-Portland', '1692-San Francisco'],
		...		'markets' : ['Hospitality']})
		...	) == sorted('&locations[]=1673-Portland&locations[]=1692-San+Francisco&markets[]=Hospitality')
		True
		'''

		big_appendage = ''

		for filter_type, selected_filter in filter_dict.items():
			for string in selected_filter:
				new_string = string.replace(" ", "+")
				url_appendage = '&' + str(filter_type) + '[]=' + new_string
				big_appendage = big_appendage + str(url_appendage)

		return big_appendage

	# e.g. &raised[min]=2334658&raised[max]=100000000 
	# Used for signal and total money raised
	# General
	def get_ranged_filter_url_appendage(self, ranged_filter_dict):
		''' Args:
		ranged_filter_dict -- dict containing {'filter_type' : [min, max]}

		Test must be sorted because dict values are appended in unordered way
		
		>>> sorted(s.get_ranged_filter_url_appendage(
		... {'raised' : [4000,25000], 'signal' : [0,4]})
		...	) == sorted('&raised[min]=4000&raised[max]=25000&signal[min]=0&signal[max]=4')
		True
		'''
		big_ranged_appendage = ''
		for filter_type, selected_filter in ranged_filter_dict.items():
			try:
				min_range = selected_filter[0]
				max_range = selected_filter[1]
				ranged_appendage = '&' + str(filter_type) + '[min]=' + \
					str(min_range) + '&' + str(filter_type) + '[max]=' + \
					str(max_range)
				big_ranged_appendage += ranged_appendage
			except IndexError:
				pass

		return big_ranged_appendage

	# Best be a string
	def get_concatenated_list_items(self, lst):
		#XXX should have one item, test later?
		concatenated_lst = []
		# iterates by multiples of 2
		for each in range(0, len(lst), 2):
			next_item = each + 1
			concatenated = lst[each] + lst[next_item]
			concatenated_lst.append(concatenated)

		return concatenated_lst

	# Combines root url as well as big appendage for each different filter 
	def get_mega_url(self, root_url, filter_dict, ranged_filter_dict): 
		appendage = self.get_filter_url_appendage(filter_dict)
		ranged_appendage = self.get_ranged_filter_url_appendage(
			ranged_filter_dict)
		mega_url = str(root_url) + appendage + ranged_appendage
		return mega_url

	def parse_main_page(self, root_url, filter_dict, 
		ranged_filter_dict, parser):

		driver = Driver.get_driver()
		mega_url = self.get_mega_url(root_url, filter_dict, ranged_filter_dict)
		limited_attempt_load_url(mega_url, driver, logger=log_time)
		page = driver.page_source
		soup = BeautifulSoup(page, parser)
		more_button = self.get_button_by_class(driver, 'more')
		self.indefinitely_click_button(more_button)
		company_count = self.get_comp_count(page, soup, mega_url)
		#try:
		if company_count > 400:
			optimize = self.get_optimization_user_input()
			# runs based on user input to above question
			self.optimize(optimize, company_count, soup, page, driver)
			log_time('highlight', 'Parsed main search page! \n')
		else:
			results = self.get_results(soup, page)
			log_time('highlight', 'Parsed main search page!')

		#except Exception as e:
			#log_time('error', str(e))
		Driver.teardown_driver(driver)

	def get_button_by_class(self, driver, cls):
		'''Args:
		driver -- selenium driver
		cls -- Class describing the button to search for within html soup

		Output: button if it is clickable
		'''

		button = None
		try:
			set_pause(1)
			# ec is selenium's 'expected conditions'
			button = driver.wait.until(ec.element_to_be_clickable(
				(By.CLASS_NAME, str(cls))))
		except TimeoutException:
			last_page_msg = 'exhausted page length'
			log_time('info', msg=last_page_msg)

		return button

	def indefinitely_click_button(self, button):
		''' Clicks button until it is no longer available to click
		Args:
		button -- clickable button from a website
		'''

		while button: 
			try:
				button.click()
				set_pause(1)
			except:
				not_clickable_msg = 'button no longer clickable'
				log_time('info', msg=not_clickable_msg)
				set_pause(1)
				break

	# Page from main page
	# Specific
	def get_comp_count(self, page, soup, target_url=None):
		''' Get the company count from the main search page. More abstract, 
		it gets a number within div.top div.count.
		Args:
		page -- page loaded by the driver
		soup -- beautiful soup soup from the page input
		target_url -- used for updating logger output
		'''

		parser_count = re.compile(r'([\d,]+)')
		try:
			new_search_msg = '*** New search, target_url***: {}'.format(
				target_url)
			log_time('highlight', msg=new_search_msg)
			company_count = soup.select(
				'div.top div.count')[0].get_text().replace(',', '')
			company_count = int(parser_count.search(company_count).group(1))

		except:
			write_debug_error(self.debug_error, page)
			company_count = 0

		comp_found_msg = '****found {} companies**** '.format(company_count)
		log_time('highlight', msg=comp_found_msg)

		return company_count

	# Specific
	def get_click_list(self):
		''' A list of buttons to click on to sort company results '''
		click_sort_list = ['signal', 'joined', 'raised']  
		return click_sort_list

	# Gets results which are sorted based on a certain filter.
	# Ex: if the click_sort was signal it would get results with highest
	# signal to lowest
	# Specific
	def get_click_sorted_results(self, 
		company_count, click_sort, 
		soup, page, driver):

		if company_count > 0:
			# Clicking on different ways to sort the company list
			sort_button = self.get_css_selector(click_sort)
			self.click_available_button(driver, sort_button)

			click_button_msg = 'clicking sort button: {}'.format(
				css_selector_str)
			log_time('info', msg=click_button_msg)

			results = self.get_results(soup, page)
			set_pause(1)
			log_time('h', 'Got results: {} \n'.format(results))

		else: 
			msg = '\n' + '0 companies found' + '\n'
			write_debug_error(self.debug_dir, page, msg)
			Driver.teardown_driver(driver)
		return results

	# Specific
	def get_css_selector(self, click_sort):
		''' Gets a css string from a column div. Gets sort button in this case.
		>>> s.get_css_selector('joined')
		'div.column.joined.sortable'
		'''
		css_selector_str = 'div.column.{}.sortable'.format(click_sort)

		return css_selector_str

	# General
	def click_available_button(self, driver, css_selector_str):
		''' Clicks button when available, can be used for sort_button. '''

		try:
			button = driver.wait.until(
				ec.element_to_be_clickable(
					(By.CSS_SELECTOR, css_selector_str)))
			button.click()
			set_pause(1)
		except:
			fail_click_msg = 'failed to click'
			log_time('error', msg=fail_click_msg)
	
	#XXX print out results at this step with code.interact
	#XXX broken
	# Specific
	#################################testing#################################
	def get_results(self, soup, page):
		''' Gets every aspect on main search page and stores in results. Aspects
		include date joined and website link etc...

		>>> soup = bs4.
		>>> s.get_results(
		'''
		try:
			results = soup.findall(class_='results')[0]('div', attrs={
				'data-_tn' : 'companies/row'})
		except Exception as e:
			log_time('e', str(e))
			write_debug_error(self.debug_dir, e)
			results = None

		return results

	def get_optimization_user_input(self):
		''' Asks whether or not to try to parse more company data. '''

		print('The search yielded more than 400 companies. Angellist limits' +\
			' companies displayed to 400. Do you wish to optimize the data' +\
			' collected? This results in a greater number of unique' +\
			' data collected. (y/n)')
		response = input()
		if response == 'y' or 'Y' or 'yes' or 'Yes':
			optimize = 'True'	
		else:
			optimize = 'False'
		return optimize

	def optimize(self, optimize, company_count, soup, page, driver):
		''' Uses sorting companies by click on signal/joined etc... sort buttons
		to get more of the companies not shown by the first 400
		'''
		if optimize:
			click_sort_list = self.get_click_list()
			for click_sort in click_sort_list:
				results = self.get_click_sorted_results(
					company_count, click_sort, soup, page, driver)

if __name__ == '__main__':
	import doctest
	mock_dir_lst = ['mock']
	mock_html = './mock/html.txt'
	urllib.urlretrieve('https://angel.co/companies?', mock_html)
	doctest.testmod(extraglobs={'s': Scraper(mock_dir_lst)})

	# get url for filters and maximize individual companies:
		# get company count
		# if more than 400 when using few filters, add another filter or
			# click one of the different ways of sorting
			# maybe add permutations fo keywords or just of the alphabet
			# (though thats a lot of permutations)
			# just adjust raised money filter by narrowing it 
			# and getting urls until
			# less than 400 are there click more button til it ends
		# else just parse main

# get results section of page, parse
# get prod desc from inner page
# write results to csv
# don't get blocked
	# randomize url list
    # add pauses so as not to innundate server with requests
    # maybe get vpn or something so as not to get blocked
    # switch user-agents if using a vpn
    # incorporate random mouse movements


