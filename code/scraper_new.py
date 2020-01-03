#!/usr/bin/python3
# vim: set sw=4 noet ts=4 fileencoding=utf-8:

#XXX !!!!!!!!!!!To Do!!!!!!!!!!!!!!!!!!
#XXX could pass in functions to make more abstract...?
#XXX when funcs are mapped label them as either specific or abstract and try to
#XXX contain specifcs
#XXX use getter functions in more consistent manner

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

# For debugging interactively
import code


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
		
		>>> str1 = '&locations[]=1673-Portland&locations[]=1692-San+Francisco'
		>>> str2 = '&markets[]=Hospitality'
		>>> sorted(s.get_filter_url_appendage(
		... {'locations' : ['1673-Portland', '1692-San Francisco'],
		...		'markets' : ['Hospitality']})
		...	) == sorted(str1 + str2)
		True
		'''

		big_appendage = ''

		for filter_type, selected_filter in filter_dict.items():
			for string in selected_filter:
				new_string = string.replace(" ", "+")
				url_appendage = '&' + str(filter_type) + '[]=' + new_string
				big_appendage = big_appendage + str(url_appendage)

		return big_appendage

	# Used for signal and total money raised
	# General
	def get_ranged_filter_url_appendage(self, ranged_filter_dict):
		''' Args:
		ranged_filter_dict -- dict containing {'filter_type' : [min, max]}

		Test must be sorted because dict values are appended in unordered way
		
		>>> sorted(s.get_ranged_filter_url_appendage(
		... {'raised' : [4000,25000], 'signal' : [0,4]})
		...	) == sorted(
		... '&raised[min]=4000&raised[max]=25000&signal[min]=0&signal[max]=4')
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
		#more_button = self.get_button_by_class(driver, 'more')
		#self.indefinitely_click_button(more_button, driver)
		self.indefinitely_click_button_by_class('more', driver)
		company_count = self.get_comp_count(page, soup, mega_url)
		#try:
		if company_count > 400:
			optimize_input = self.get_optimization_user_input()
			# runs based on user input to above question
			df = self.optimize(
				optimize_input, company_count, soup, page, driver)
			self.write_output(df)
			log_time('highlight', 'Parsed main search page! \n')
		else:
			results = self.get_results(driver)
			log_time('highlight', 'Parsed main search page!')

		#except Exception as e:
			#log_time('error', str(e))
		Driver.teardown_driver(driver)

	#XXX probably have a func that does this
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
			not_clickable_msg = 'button does not exist or is not clickable'
			log_time('info', msg=not_clickable_msg)

		return button

	#XXX trying to wait for it to be clickable before looping thru 
	def indefinitely_click_button_by_class(self, button_class, driver):
		''' Clicks button until it is no longer available to click
		Args:
		button -- clickable button from a website
		'''

		button = driver.wait.until(ec.element_to_be_clickable((
			By.CLASS_NAME, button_class)))
		while button: 
			try:
				# For some god forsaken reason ec.element_to_be_clickable
				# expects a tuple as the arg... hence the stupid paren
				button = driver.wait.until(ec.element_to_be_clickable((
					By.CLASS_NAME, button_class)))
				button.click()
				set_pause(1)
			except Exception as e:
				not_clickable_msg = '\n button no longer clickable OR \n' + \
					str(e)
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
			write_debug_error(self.debug_dir, page)
			company_count = 0

		comp_found_msg = '****found {} companies**** '.format(company_count)
		log_time('highlight', msg=comp_found_msg)

		return company_count

	# Specific
	#XXX maybe pass in as a setting later
	def get_click_list(self):
		''' A list of base words for attributes of divs on Angellist. 
			This list determines what sort buttons will be clicked on for
			optimization. '''

		click_sort_list = ['location', 'website', 
			'market', 'company_size', 'stage', 'raised']  
		return click_sort_list

	# Specific
	def get_click_sort_list(self, click_list):
		'''
		Example:
		>>> click_list = ['joined', 'market', 'raised']
		>>> click_sort_list = s.get_click_sort_list(click_list)
		>>> click_sort_list == ['joined.sortable', 'market', 'raised.sortable']
		True
		'''

		new_click_list = click_list
		for i, string in enumerate(click_list):
			if string == 'joined' or string == 'raised' or string == 'signal':
				new_string = string + '.sortable'
				click_list[i] = string.replace(string, new_string)
		return click_list 

	#XXX may want to revert to not clicking automatically
	#XXX need to shorten
	# Gets results which are sorted based on a certain filter.
	# Ex: if the click_sort was signal it would get results with highest
	# signal to lowest
	# Specific
	#XXX NOT WORKING; clicking sort buttons may not yield different results
#	def get_click_sorted_results(self, 
#		company_count, click_sort_list, 
#		soup, page, driver):
#
#		df = pd.DataFrame()
#		results = self.get_results(driver)
#		set_pause(1)
#		if company_count > 0:
#			for click_sort in click_sort_list:
#				print('\n\n\n\nCLICK SORT\n\n\n\n' + str(click_sort) + '\n')
#				#XXX scattered get... func
#				sort_css = self.get_sort_column_css(click_sort)
#				# Gets sort buttons initially available
#				sort_clickable = self.click_available_button(driver, sort_css)
#				df = self.append_dataframe(results, df)
#				# This tries to click the slider to the right so that all sort
#				# columns can be seen. Just go look at the site to understand.
#				# Gets sort buttons not initially available
#				attempt = 0
#				while not sort_clickable and attempt == range(0,5):
#					slide_css = 'column slider'
#					slide_clickable = self.click_available_button(
#						driver, slide_css)
#					if slide_clickable:
#						sort_clickable = self.click_available_button(
#							driver, sort_css)
##############################working here######################################
#						# gets results and companies and adds to pd dataframe
#						#df = self.get_dataframe(driver)
#						df = self.append_dataframe(results, df)
#			
#						######################################
#
#
#					else:
#						log_time(msg='Slider not clickable')
#
#					attempt += 1
#
#				if not sort_clickable:
#					msg = 'Could not sort companies or slide sort' +\
#						'buttons!'
#					write_debug_error(self.debug_dir, msg=msg)
#					log_time('error', msg=msg)
#
#			#results = self.get_results(driver)
#			set_pause(1)
#
#		else: 
#			msg = '\n' + '0 companies found' + '\n'
#			write_debug_error(self.debug_dir, page, msg)
#			Driver.teardown_driver(driver)
#		return df

	def get_dataframe(self, company_count, page, driver):
		df = pd.DataFrame()
		results = self.get_results(driver)
		set_pause(1)
		if company_count > 0:
			df = self.append_dataframe(results, df, driver)
		else: 
			msg = '\n' + '0 companies found' + '\n'
			write_debug_error(self.debug_dir, page, msg)
			Driver.teardown_driver(driver)
		return df

	def append_dataframe(self, results, df, driver):
		#XXX added driver to params
		entries = self.get_entries(results, driver)
		entry_msg = '\n Entries: \n' + str(entries)
		log_time(kind='h', msg=entry_msg)
		len_msg = ('\n' + str(len(entries)) + '\n')
		log_time(msg=len_msg, kind='i')
		df = df.append(entries)
		df_msg = ('\n' + 'df: ' + str(len(df)) + '\n')
		log_time(msg=df_msg, kind='i')
		return df

	# Specific
	def get_sort_column_css(self, click_sort):
		''' Click sort passed in must already have .sortable if applicable.
		Example:
		>>> click_sort = 'raised.sortable'
		>>> out = s.get_sort_column_css(click_sort)
		>>> out == 'div.column.raised.sortable'
		True
		'''

		css_selector_str = 'div.column.{}'.format(click_sort)
		return css_selector_str


	# General
	def click_available_button(self, driver, css_str):
		''' Clicks button when available, can be used for sort_button. '''

		clickable = False
		try:
			#XXX js version of clicking
			element = driver.find_element_by_css_selector(css_str)
			driver.execute_script("arguments[0].click();", element)
#			button = driver.wait.until(
#				ec.element_to_be_clickable(
#					(By.CSS_SELECTOR, css_str)))
#			button.click()
			set_pause(1)
			clickable = True

		except TimeoutException as e:
			fail_click_msg = '\n Failed to click {} due ' +\
				'to TimeoutException; '.format(css_str) + str(e) 
			log_time('error', msg=fail_click_msg)
			write_debug_error(self.debug_dir, msg=fail_click_msg)

		return clickable
	
	# Specific
#XXX need to reformat output data so that there is only one key like 
# 'title' which will contain a tuple (comp1_data, comp2_data) etc...
# Rather than a dict with a key and value for each company
# e.g [{'title' : 'Amazon'}, {'title' : }...]
	def get_results(self, driver):
		''' Gets every aspect on main search page and stores in results. Aspects
		include date joined and website link etc...
		'''

		#XXX IMPORTANT TO GET PAGE AGAIN BEFORE PARSING. IDK WHY
		try:
			page = driver.page_source
			soup = BeautifulSoup(page, 'lxml')
			# [0] doesn't seem necessary as theres is only
			# one results class but its defensive
			results = soup(class_='results')[0]('div', attrs={
				'data-_tn' : 'companies/row'})
		except Exception as e:
			log_time('e', str(e))
			write_debug_error(self.debug_dir, e)
			results = None
		return results

	# In the future one dict which was structured {'header' : [entry1...],
	# 'next header' : [entry1...]} such that entry elements always match
	# would save some redundancy
	#XXX added driver to params
	def get_entries(self, results, driver):
		''' Gets info about companies in a list of dictionaries. Must pass in
		results as gotten by self.get_results.
		Args:
			results -- a specific section of the angellist website containing
			company data.
		'''
		length = len(results)
		entries = []
		# This loop creates individual dictionaries with keys that represent
		# aspects of that company. It then appends the individual dict to the
		# the list of dicts and returns the list as entries
		for each in range(1, length):
			comp_entry = dict()
			try:
				# a represents one company in results set
				a = results[each]

				title = a.select('a.startup-link')[0]['title']
				comp_entry['title'] = title

				pitch = a.select('div.pitch')[0].string
				comp_entry['pitch'] = pitch

				# Parens used for different html tags, brackets for settings
				# within tags like classes and ids
				signal_img = a.select(
					'div.column.signal')[0]('img')[0]['src']
				signal = self.get_signal_value(signal_img)
				comp_entry['signal'] = signal

				# As comp_entry is passed through these functions they append
				# to it and return it
				comp_entry = self.joined_entries(a, comp_entry)
				
				click_list = self.get_click_list()
				# Gets things like market and location. See func below
				comp_entry = self.click_list_entries(click_list, a, comp_entry)

				#XXX kinda works but I need to separate from get_entries
				# because this will take forever clicking on each of 702
				# pages. It needs to be optional.
				# Also needs to return to the prior page so that it can get
				# the next company description by hitting the back button.
				#################working###############
				#inner_soup = self.get_inner_soup(a, driver)
				#desc = self.get_description(inner_soup)
				#print(desc)
				#self.visit_inner_soup(a, driver)

				entries.append(comp_entry)

			except IndexError as e:
				msg = 'get_entries Error! ' + str(e)
				log_time(kind=e, msg=msg)
				continue

		#XXX encode?
		#entries = self.encode_entries(entries)
		#code.interact(local=locals())

		return entries

	# Specific
	def click_list_entries(self, click_list, result, comp_entry):
		''' This func uses a list of search criteria to find the html text
		corresponding to each criterion. Some do not have the same html tags.
		'''
		# Location, Market, Website, Employees, Stage, Raised
		# Stage and raised don't have a tag but do have div.value
		for each in click_list:
			try:
				selection = result.select(
				# was each))[0].text.strip() before
					'div.column.' + str(each))[0]('a')[0].text.strip()
			except IndexError as e:
				selection = result.select(
					'div.column.' + str(each) + ' > div.value')[0].text.strip()
				
			selection = Scraper.replace_commas(selection)
			comp_entry[str(each)] = selection
		return comp_entry

	@staticmethod
	def replace_commas(selection):
		''' 
		This method removes commas from text for future use in csv files.
		It returns strings.
		Example:
		>>> selection = '12,000,000'
		>>> new_selection = s.replace_commas(selection)
		>>> new_selection == '12000000'
		True
		'''
		comma = ','	
		if comma in selection:
			selection = selection.replace(comma, '')
			#' '.join(selection.split())
		return selection

	def joined_entries(self, result, comp_entry):
		# This syntax indicates nested css SELECTORS (not classes)
		# Also can't just do value b/c ambiguous
		joined = result.select('div.column.joined > div.value')
		if joined:
			joined = joined[0].get_text().encode(
				'ascii', errors='replace')
			#XXX why? in original he decodes into utf-8
			joined = joined.decode('utf-8').strip().replace('?', '')
			# Changes i.e. Aug '17 to regular computer date format
			# like 2017-08-01 00:00:00
			joined = str(datetime.datetime.strptime(joined, '%b %y'))
		comp_entry['joined'] = joined
		return comp_entry

	#XXX need to use self.parser
	def get_inner_soup(self, result, driver):
		inner_url = result.select('a.startup-link')[0]['href']
		################working, 11/4/19################3
		print(inner_url)
		#xpth_str = '//a[@href=' + str(inner_url) + ']'
		#driver.find_element_by_xpath(xpth_str).click()
		driver.find_element_by_css_selector('a.startup-link').click()
		page = driver.page_source
		inner_soup = BeautifulSoup(page, 'lxml')

		#driver.load_url(driver=driver
		return inner_soup

	def get_description(self, inner_soup):
		desc = inner_soup(class_='component_bc35d')[0].text
		return desc

	#XXX test this
	def encode_entries(self, entries):
		''' Should take the value of each key in the dict of entries
		and encode it with ascii '''

		#XXX is this always one d?
		for key, value in entries.items(): 
			entries[key] = value.encode('ascii', errors='replace')
		return entries

	# Need to get signal img_src from html and pass it in to get signal value
	def get_signal_value(self, img_src):
		'''
		Example:
		>>> src1 = 'https://angel.co/assets/icons/signal0-' 
		>>> src2 = 'ff10531d1ea9f81f96c2a24d2b1a98df606e1d4912ee'
		>>> src3 = '8156f30b7b3e5c6e5d45.png'
		>>> img_src = (src1 + src2 + src3)
		>>> signal = s.get_signal_value(img_src)
		>>> signal == 0
		True
		'''

		# Python excludes last number, includes first
		for number in range(0,11):
			thing = 'signal' + str(number)
			if thing in str(img_src):
				signal = number
		return signal

	def get_optimization_user_input(self):
		''' Asks whether or not to try to parse more company data. '''

		print('The search yielded more than 400 companies. Angellist limits' +\
			' companies displayed to 400. Do you wish to optimize the data' +\
			' collected? This results in a greater number of unique' +\
			' data collected. (y/n)')
		response = input()
		if response == 'y' or 'Y' or 'yes' or 'Yes':
			optimize = True	
		else:
			optimize = False
		return optimize

	#XXX probably not necessary, replacing with direct call to get_click_sorted
	def optimize(self, optimize, company_count, soup, page, driver):
		''' Uses sorting companies by click on signal/joined etc... sort buttons
		to get more of the companies not shown by the first 400
		'''
		if optimize:
			click_list = self.get_click_list()
			click_sort_list = self.get_click_sort_list(click_list)
			#XXX changed to get_dataframe
			#df = self.get_click_sorted_results(
				#company_count, click_sort_list, soup, page, driver)
			df = self.get_dataframe(company_count, page, driver)
			#XXX being weird.
			#df = df.drop_duplicates()
			df_msg = ('\n' + 'df: ' + str(len(df)) + '\n')
			log_time(msg=df_msg, kind='i')
		return df

	def write_output(self, df):
		''' This function takes the pandas dataframe and writes it
		to a csv file in the dir ../output.'''
		df.to_csv('../output/out.csv')
		return df

#def setUp(test):
	#test.globs['y'] = 1

if __name__ == '__main__':
	#import minimock

	import doctest
	# This construction is necessary b/c Scraper expects a dir_list
	mock_dir_lst = ['mock']
	# makes the var s available for testing and runs tests
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


