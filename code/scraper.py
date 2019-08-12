# vim: set sw=4 noet ts=4 fileencoding=utf-8:
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
# Colors terminal text
import colorama

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

url = "https://angel.co/companies?" 
#driver = Driver.get_driver()

#XXX have moved many things from __init__ into separate functions and may need
# to access stored values differently
# Also, general_scraper is no longer a class so calling functions like log_time
# may need adjustment

#XXX program constantly checks for drivers present and loaded urls and
# that company count is greater than none etc... it is defensive and
# costly in terms of complexity so I wonder if there is a better way

class AngelListScraper():
	def __init__(self, base_url, driver,
		skip_market_filter=False, 
		skip_location_filter=False,
		skip_raised_filter=False,
		skip_stage_filter=False,
		skip_signal_filter=False,
		skip_featured_filter=False):
		

		self.setup_data_display()
		self.dr = driver
		self.url = base_url

		# Skipping filters based on args when instantiating class
		self.skip_market_filter = skip_market_filter
		self.skip_location_filter = skip_location_filter
		self.skip_raised_filter = skip_raised_filter
		self.skip_stage_filter = skip_stage_filter
		self.skip_signal_filter = skip_signal_filter
		self.skip_featured_filter = skip_featured_filter

		#XXX ??
		self.market_filters = ['']
		self.location_filters = ['']
		self.signal_filters = ['']
		self.featured_filters = ['']

		#XXX changed "folder" to "dir" from the end of directories;
		# that will mess up variable names in the future
		self.dir_list = ["output", "code", 
			"output/url_list_dir", "output/results_dir", 
			"output/company_page_dir", "output/index_page_dir", 
			"output/market_label_size_file_dir", "output/debug_dir"]


		#XXX need other class for isolating settings
		self.parser = 'lxml' 
		self.visit_inner = True  # inner pages are comapny detail pages
		self.inner_page_redownload = False  # if inn
		self.mute_display = False

	
		#XXX Moved theses setups to main.py. Need to change
		self.locations = ['1688-United+States', '1624-California', 
			'1664-New+York+City', '153509-Asia', '1642-Europe',
			'1695-London,+GB', '1681-Silicon+Valley']

	
	
		# raised money
		#XXX Shouldn't these come from crawling, not from manually set values?
		self.raised_pair_list = [(0, 1),
			(1, 400000),
			(400000, 10000000),
			(1000000, 1500000),
			(1500000, 2000000),
			(2000000, 2500000),
			(2500000, 3500000),
			(3500000, 5500000),
			(5500000, 8500000),
			(8500000, 12000000),
			(12000000, 20000000),
			(20000000, 30000000),
			(30000000, 50000000),
			(50000000, 100000000),
			(100000000, 1000000000),
			(1000000000, 1000000000000000)]
	
	
		self.stage_list = [
			'Series+A',
			'Series+B',
			'Acquired',
			'Series+C',
			'Series+D',
			'Seed',
			'IPO']


		self.url_df = None
		self.search_page_url_list_file = os.path.join(self.url_list_folder,
			'url_list_{}.csv'.format(datetime.date.today()))

	def setup_data_display(self):
		# Data displaying settings
		pd.set_option('display.max_colwidth', -1)
		pd.set_option('display.colheader_justify', 'left')
		colorama.init()
	

	def load_url(self, target_url, driver):
		try:
			driver.get(target_url)
			page_loaded = True
			log_time(msg='page loaded successfully: {}'.format(target_url))
	
		except TimeoutException:
			timeout_msg = 'loading page timeout' + target_url + \
				'attempt {}'.format(n_attempts)
			log_time(kind='error', msg=timeout_msg)
			set_pause(1)
	
		#XXX dont catch all other exceptions
		except:
			other_exception_msg = 'loading page unknown error' + \
				target_url + 'attempt {}'.format(n_attempts)
			log_time(kind='error', msg=other_exception_msg)
			set_pause(1)

		return page_loaded

	def limited_load_url(self, n_attempts_limit=3, target_url, driver):
		n_attempts = 0
		page_loaded = False
		while not page_loaded:
			n_attempts += 1
			if n_attempts >= n_attempts_limit:
				# Driver was never loaded so don't quit it?
				#self.dr.quit()
				load_limit_msg = \
					'loading page failed after {} attempts, ' \
					'now giving up on: '.format(n_attempts_limit) + \
					self.url
				log_time(kind='error', msg=load_limit_msg)
				break
		
			else:
				page_loaded = self.load_url(target_url, driver)
				break
		return page_loaded

	# d must be a directory which either exists or will exist
	def check_dir_exists(self, d):
		if not os.path.exists(d):
			os.mkdir(d)

	#XXX could alternatively pass in dir_list as arg or as arg in __init__()
	def construct_dir_tree(self, dir_list):
		for each in dir_list:
			dir_string_name = os.path.basename(each) 

			# Ex: if dir_list = ["code"] then the variable code contains
			# "code" and makes the dir when check_dir_exists runs
			setattr(self, dir_string_name, each)

			# Make a dir with the name dir_string_name if it did not exist
			self.check_dir_exists(getattr(self, dir_string_name))


	def setup_market_labels(self, market_label_file):
		if market_label_file is None:
			market_labels = []
		#XXX 
		#path_of_market_label_file = os.path.join(
			#code_dir, os.path.basename(market_label_file))
		else:
			with open(os.path.abspath(market_label_file), 'r') as f:
				m = f.readlines()
			market_labels = [x.strip() for x in m]
		return market_labels
	
	#XXX returned market_filters instead of self
	def setup_market_filters(self, market_label_file)
		market_labels = self.setup_market_labels(market_label_file)
		if market_labels and not self.skip_market_filter:
			# Fills market_filters with each label and replaces spaces with +
			# which is used to append the filter to a base url later 
			#XXX what is the .replace('+++', '+') thing
			market_filters = ['&markets[]={}'.format
				(x.replace(' ', '+')).replace('+++', '+')
				for x in market_labels]
			market_filters.insert(0, '')
		return market_filters


	#XXX returned instead of self for loc filters
	def setup_location_filters(self):
		if locations and not self.skip_location_filter:
			location_filters = ['&locations[]={}'.format(
				x.replace(' ', '+')) 
				for x in locations]
			location_filters.insert(0, '')
		return location_filters

	def setup_signal_filters(self, signal_pair_list):
		signal_pair_list.reverse()
		if self.skip_signal_filter or not signal_pair_list:
			#XXX ??
			# signal_pair_list = [(8, 9), (9, 10)]
			signal_pair_list = [(7, 8)]
		signal_filters = [
			'&signal[min]={signal_min}&signal[max]={signal_max}'.format
				(signal_min=x[0], signal_max=x[1]) for x in signal_pair_list]
		signal_filters = zip(self.signal_filters, signal_pair_list)
		return signal_filters
	
	#XXX needs work
	def setup_featured_filters(self, featured_filter_list=None):
		if not self.skip_featured_filter:
			featured_filters = ['', '&featured=Featured']
		return featured_filters

	# Raised money filter
	def setup_raised_filter(self, raised_pair_list):
		if not raised_pair_list or self.skip_raised_filter:
			raised_filters = ['']
		else:
			raised_filters = [
				'&raised[min]={raised_min}&raised[max]={raised_max}'.format
					(raised_min=x[0], raised_max=x[1]) for x in 
					raised_pair_list]
			raised_filters.insert(0, '')
		return raised_filters

	# Stage as in seed, series a, b, c, etc..
	def setup_stage_filter(self, stage_list): 
		if self.skip_stage_filter or not stage_list:
			stage_filters = ['']
		else:
			stage_filters = ['&stage={}'.format(x) for x in stage_list]
			# self.stage_filters.append('')
			stage_filters.insert(0, '')
		return stage_filters

	# changed func name from generate_url_list_of_search_pages
	#XXX return url_df
	def generate_search_page_urls(self, use_existing_url_list=False,
		raised_filters, stage_filters,
		market_filters, featured_filters, 
		location_filters, signal_filters):

		# tmp filters don't seem necessary; just use the self ones I think
		tmp_raised_filters = self.raised_filters
		tmp_stage_filters = self.stage_filters

		if not use_existing_url_list:
			url_list = self.append_url_list(tmp_raised_filters, target_url,
				market_filters, featured_filters
				location_filters, signal_filters)
			self.check_company_count()
			self.url_df = pd.DataFrame(url_list).drop_duplicates()

			writing_urls_msg = 'Writing url list file: {}'.format
				(self.search_page_url_list_file)
			log_time(msg=writing_urls_msg)

			self.url_df.to_csv(self.search_page_url_list_file)

		else:
			reading_urls_msg = 'Reading url list file: {}'.format
				(self.search_page_url_list_file)
			log_time(msg=reading_urls_msg)

			self.url_df = pd.read_csv(self.search_page_url_list_file)

		url_list_length_msg = 'Length of url_list: {}'.format(len(self.url_df))
		log_time(msg=url_list_length_msg)
			
	#XXX better name
	def append_url_list(self, tmp_filters_list, 
		market_filters, featured_filters, 
		location_filters, signal_filters):

		# Will contain a list of dictionaries, each of which will contain
		# one url, filename?, company count on the given page, featured filter,
		# and signal filter
		url_list = []

		# Gets every combination of filter urls
		for mf in market_filters: # OR
			for ff in featured_filters: # XXX
				for lf in location_filters: # OR
					for sf in signal_filters: # AND
						target_url = self.url + mf + ff + lf + sf[0]
						company_count = self.get_company_count_on_search_page(
								target_url=target_url)

						self.make_company_dict(
							target_url, company_count, ff, sf)

						# so as not to query the server too much
						self.url_generator_pause()
						
						divisor = self.get_divisor(company_count)

						#XXX conceptually correct but need to understand
						# what is happening with the different filter lists used
						# and how the companies are actually being separated
						for each in range(divisor):
							self.divide_url_companies(tmp_filters_list, 
								target_url, url_list, ff, sf)

		return url_list

	@staticmethod
	def url_generator_pause():
		if random.random() < .6:
			set_pause(2)
		elif random.random() < .95:
			set_pause(1)

	# SHOULD take a search which returns more than 400 companies and create
	# multiple urls with =< 400 companies so that they can all be scraped
	# adds 'and' filters (those that decrease comp. count) if there are too 
	# many companies on a page.
	def divide_url_companies(self, tmp_filter_list, 
		target_url, url_list, ff, sf):

		over_400_msg = "Url has too many companies. Making multiple urls"
		log_time(msg=over_400_msg)

		for filtr in tmp_filter_list:
			div_url = target_url + filtr
			new_company_count = self.get_company_count_on_search_page(
				target_url=div_url)
	
			self.url_generator_pause()
	
			self.make_company_dict(url_list, div_url, 
			new_company_count, ff, sf)
		return div_url
	
	def make_company_dict(self, url_list, target_url, company_count, ff, sf):
		if company_count > 0:
			url_list.append(dict(url = target_url,
				fname = self.url_to_base_fname(div_url),
				company_count = company_count,
				featured = ff,
				signal = sf[1][1]))
		
		else:
			empty_list_msg = (
				'empty list, not adding' + \
				'to the url_list: {}'.format(target_url))
			log_time(msg=empty_list_msg)

	#XXX not applicable bc the "dividing" company method may include duplicates
	def get_divisor(self, company_count):
		# Round up number of times to divide company count per page
		divisor = math.ceil(company_count / 400)
		return divisor

	def url_to_base_fname(self, url):
		# self.url is base url
		fname = 'results_' + url.replace
			(self.url, '').replace('&', '_') + '.csv'
		return fname


	def get_company_count_on_search_page(self, driver_in=None, target_url=None):

		new_search_msg = '*** New search, target_url: {}'.format(target_url)
		log_time('highlight', msg=new_search_msg)
		#XXX put in log function
		#sys.stdout.flush()

		#XXX ?? get from general_scraper
		driver = self.new_driver(driver_in)

		try self.limited_load_url(target_url, driver):
			page = driver.page_source
			if driver_in is None:
				quit_driver(driver)
	
			company_count = self.parse_comp_count(page)

		#XXX catch specific 'unloaded page' error
		except someerror:	
			company_count = 0

		return company_count

	def parse_comp_count(self, page):
		soup = BeautifulSoup(page, self.parser)
		parser_count = re.compile(r'([\d,]+)')

		try:
			company_count = soup.select(
				'div.top div.count')[0].get_text().replace(',', '')
			company_count = int(parser_count.search(company_count).group(1))

		# Couldn't get comp count from page. Maybe didn't load url for ex.
		except:
			failed_case_fname = os.path.join(self.debug_dir,
				'failed_{}.html'.format(str(datetime.datetime.now())))

			comp_count_fail_msg = 'failed to get company count page, ' + \
				'saving page as {}'.format(failed_case_fname)
			log_time('error', msg=comp_count_fail_msg)

			with open(failed_case_fname, 'w') as failed_f:
				failed_f.write(page.encode('utf-8'))

			company_count = 0

		comp_found_msg = '*** found {} companies'.format(company_count)
		log_time('highlight', msg=comp_found_msg)

		return company_count

	def new_driver(self, driver_in=None):
		if driver_in is None:
			driver = dr.get_driver()
		else:
			driver = driver_in
		return driver


	#XXX could prob pass in url_df
	def parse_all_search_pages(self, use_file=None):
		# use self.url_df if not using a file
		if use_file is None:  
			# shuffle to help resuming at random entry point
			self.url_df = self.randomize_urls(url_df)

			for idx, row in self.url_df.iterrows():
				self.parse_one_search_page(url_dict=row)
		else:
			#XXX different way to do this? use log and raise exception?
			assert 0

	#XXX could document in Jupyter notebook with iloc picture/example
	# Used to not get blocked
	def randomize_urls(self, url_df):
		df = url_df.iloc[np.random.permutation(len(url_df))]
		return df

	def parse_one_search_page(self, url_dict=None):
		assert url_dict is not None

		parse_msg = 'parsing single page: ' + url_dict
		log_time('highlight', msg=parse_msg)

		result_fname_template = os.path.join(
			self.results_folder, url_dict['fname']).replace('.csv',
			'_sort=<sort_key>_click={''}.csv')

		url = url_dict['url']
		company_count = url_dict['company_count']
		signal_score = url_dict['signal']
		featured = url_dict['featured']

		click_sort_list = self.get_click_list(company_count)

		for click_sort in click_sort_list:
			result_fname = result_fname_template.replace(
				'<sort_key>', click_sort)
			#XXX driver changed
			driver = init_driver()
			limited_load_url(driver=driver, url=url)

			N_click_max = company_count / 20 + 2
			#XXX Seems like maybe this should be a plus equals?
			N_click = 1
			N_rows = 1

			results = self.get_click_sorted_results(company_count, 
				click_sort, driver, url)

			#XXX necessary?
			if results:
				N_rows_new = self.get_number_rows(results)

			entries = []

			while N_click < N_click_max:
				output_fname = result_fname.format(N_click)
				start_row = N_rows
				N_rows = N_rows_new

				self.write_entries_to_data_frame(output_fname, start_row, 
					N_rows, results)

				self.output_pause()

				self.click_more_button(more_button, N_click)

				self.retry_loading_page(driver, N_click)

				last_page_flag = self.get_more_button_final(driver)

			quit_driver(driver)


	def get_click_list(self, company_count):
		if company_count > 400:
			# using several clicks to get more companies
			click_sort_list = ['signal', 'joined', 'raised']  
		else:
			click_sort_list = ['signal']

		return click_sort_list

	# does not actually click on more button, just sets variable if 
	# it is available to click
	def get_more_button(self):
		more_button = None
		try:
			# ec is selenium's 'expected conditions'
			more_button = driver.wait.until(ec.element_to_be_clickable(
				(By.CLASS_NAME, 'more')))

		except TimeoutException:
			last_page_msg = 'exhausted page length,' +\
				'with N_click == {}'.format(N_click)
			log_time('error', msg=last_page_msg)
		return more_button

	def get_last_page_flag(self, more_button, last_page_msg):
		timeout = self.get_more_button_timeout(more_button, last_page_msg)
		if more_button is None or timeout:
			last_page_flag = True
		else:
			last_page_flag = False
		return last_page_flag

	def get_css_selector(self, click_sort):
		#XXX doesn't use signal because that is the default? Wouldn't
		# hurt to click it anyway though...? unless it creates repeated data
		#if click_sort != 'signal':
		css_selector_str = 'div.column.{}.sortable'.format(
			click_sort)
		click_button_msg = 'clicking sort button: {}'.format(
			css_selector_str)
		log_time('info', msg=click_button_msg)
		return css_selector_str

	def sort_companies_by_filter(self, css_selector_str):
		try:
			sort_button = driver.wait.until(
				ec.element_to_be_clickable(
					(By.CSS_SELECTOR, css_selector_str)))
			sort_button.click()
			#XXX why wait here again? Why not random pause for reasonable time
			#driver.wait.until(ec.element_to_be_clickable(
			#	(By.CSS_SELECTOR, css_selector_str)))
		except:
			fail_click_msg = 'failed to click' +\
				' click_sort={} at {}'.format(click_sort, url)
			log_time('error', msg=fail_click_msg)

	#XXX what is happening here?
	# results is an html element describing the whole container for company 
	# title, signal, website, whatever...
	# I believe this saves the data-_tn and companies/row elements 
	# within results as results
	def get_results(self, page, soup):
		try:
			results = soup(class_='results')[0]('div', attrs={
				'data-_tn': 'companies/row'})
		except:
			self.log_failed_results(page)

		return results

	def get_number_rows(self, results):
		N_rows_new = len(results)
		return N_rows_new

	def log_failed_results(self, page):
		failed_case_fname = os.path.join(self.debug_dir,
			'failed_{}.html'.format(str(datetime.datetime.now())))
		parse_fail_msg = 'failed to get results from page,'+\
			'saving page as {}'.format(failed_case_fname)
		log_time('error', msg=parse_fail_msg)

		with open(failed_case_fname, 
			'w', encoding='utf-8') as failed_f:
			failed_f.write(page.encode('utf-8'))
		continue

	def make_entries(self, entry, a, results, title, inner_url):
		entry['title'] = title
		#XXX how do we know these are from the correct page?
		entry['featured'] = featured
		entry['score'] = signal_score
		# startup-link ex: amazon.com
		entry['al_link'] = inner_url
		entry['signal'] = a.select('div.column.signal')[0]('img')[0]['alt']
		entry = self.make_date_entry(a, entry)
		entry = self.make_entry(a, 'location', entry)
		entry = self.make_entry(a, 'market', entry)
		entry = self.make_href_entry(a, 'website', entry)
		entry = self.make_entry(a, 'company_size', entry) 
		entry = self.make_entry(a, 'stage', entry)
		entry = self.make_nice_entry(a, 'raised', entry)

		return entry

	def get_title(self, a):
		title = a.select('a.startup-link')[0]['title']
		title = title.encode('ascii', errors='replace')
		return title

	def get_inner_url(self, a):
		inner_url = a.select('a.startup-link')[0]['href']
		return inner_url

	def make_date_entry(self, a, entry):
		date_obj = a.select('div.column.joined > div.value')
		if date_obj:
			date_str = date_obj[0].get_text().encode(
				'ascii', errors='replace')
			date_str = date_str.decode(
				'utf-8').strip().replace('?', '')
			entry['joined_date'] = datetime.datetime.strptime(
				date_str, '%b %y')
		else:
			entry['joined_date'] = None

		return entry

	def make_entry(self, a, tag, entry):
		some_filter = a.select('div.column.' + str(tag) + ' div.tag'
		if some_filter:
			entry[str(tag)] = some_filter[0].get_text().strip()
		return entry

	# website
	def make_href_entry(self, a, tag, entry):
		try:
			entry[str(tag)] = a.select(
				'div.column.' + str(tag) + ' a')[0]['href']
		except:
			pass
		return entry

	# Definition 'nice': doesn't contain string [^\d.] in the entry 
	def make_nice_entry(self, a, tag, entry):
		area_of_interest = a.select(
			'div.column.' + str(tag) + ' div.value')[0].get_text().strip()
		# this is a raw expression of the string [^\d.] .... why it was
		# there I have no idea
		nice_text = re.sub(r'[^\d.]', '', area_of_interest)
		if nice_text:
			entry['raised'] = float(nice_text)

		return entry

	def log_entries(self, N_click, i, N_rows, title, entry):

		click_number_msg = datetime.datetime.now() +
			'N_click = {}, row = {}/{}, {}'.format(
				N_click, i, N_rows - 1, title)

		entry_msg = 'Made entries of html aspects' +\
			'of a page: {}'.format(str(entry) + \n + click_number_msg)

		log_time(msg=entry_msg)

	#XXX Should selfs in this be selfs? Are they handled differently now?
	def interpret_inner_page(self, inner_url, entries, entry):

		inner_page_filename = self.get_inner_page_filename(
			self.company_page_folder, inner_url)

		if self.visit_inner:
			#XXX Why?
			inner_page = None

			# Checks to see if the inner page was already downloaded.
			#XXX in future just control this based on what you know will be
			# downloaded or not
			if (not self.inner_page_redownload) and
				os.path.exists(inner_page_filename):
				inner_page = self.get_existing_inner_page(inner_page_filename)

			else:
				inner_page = self.get_new_inner_page(inner_url)
				self.write_out_page(inner_page_filename, inner_page)

			if inner_page is not None:
				entry = self.make_prod_desc_entry(inner_page, entry)

		self.make_inner_page_entry(inner_page_filename, entry)

		entries.append(entry)
		return entries


	def get_inner_page_filename(self, company_folder, inner_url):
		#XXX why do this? I saw this in results folder 
		# and everything had ]]]. Also self.company_page_folder is messed up
		inner_page_filename = os.path.join(
			company_folder, inner_url.replace('/', ']]]') + '.html')

	def get_existing_inner_page(self, inner_page_filename):
		overwrite_msg = '{} exists, wont ' +\
			're-download'.format(inner_page_filename)
		log_time('overwrite', msg=overwrite_msg)

		with open(inner_page_filename, 'r') as fi:
			inner_page = fi.read()

		return inner_page

	#XXX may be replaceable with a more general func for loading pages
	# also init_driver() is wrong and so is load_url() (probably)
	#XXX must be in a loop b/c of the continue?
	def get_new_inner_page(self, inner_url):
		inner_driver = init_driver()
		if load_limited_url(driver=inner_driver, url=inner_url):
			inner_page = inner_driver.page_source
			inner_driver.quit()
		else:
			quit_driver(inner_driver)
			continue

		return inner_page

	def write_out_page(self, filename, page):
		with open(filename, 
			'w', encoding='utf-8') as p:

			if sys.version_info[0] == 3:
				if isinstance(page, bytes):
					p.write(page.decode(
						'utf-8', 'replace'))
				else:
					p.write(page)
			else:
				if isinstance(page, unicode):
					p.write(page.encode(
						'utf-8'))
				else:
					p.write(page)
		#XXX why, move preferably so it doesn't mess up function
		self.write_inner_pause()

	def write_inner_pause(self):
		if random.random() < 0.1:
			set_pause(3)
		elif random.random() < .6:
			set_pause(2)
		elif random.random() < .95:
			set_pause(1)

	def make_prod_desc_entry(self, inner_page, entry):
		inner_soup = BeautifulSoup(
			inner_page, self.parser)
		try:
			product_desc = inner_soup.select(
				'div.product_desc div.content')[
				0].get_text().strip()
			entry['product_desc'] = product_desc
		except:
			prod_desc_msg = 'cannnot get product_desc'
			log_time('error', msg=prod_desc_msg)

		return entry

	def make_inner_page_entry(self, inner_page_filename, entries, entry):
		with open(inner_page_filename.replace(
			'.html', '.txt'), 'w') as f_record:
			f_record.write(str(entry))

	def make_data_frame_output(self, entries, output_fname):
		df_entries = pd.dataframe(entries)

		write_output_msg = 'writing {}'.format(output_fname)
		log_time('write', msg=write_output_msg)

		df_entries.to_csv(
			output_fname, index=false, encoding='utf-8')

	def last_page_break(self, last_page_flag):
		if last_page_flag:
			last_pg_msg = 'last page reached'
			log_time('error', msg=last_pg_msg)
			set_pause(1)
			break

	def output_pause(self):
		if random.random() < 0.01:
			set_pause(5)
		elif random.random() < 0.05:
			set_pause(4)
		elif random.random() < 0.1:
			set_pause(3)
		elif random.random() < .9:
			set_pause(2)
		else:
			set_pause(1)

	def click_more_button(self, more_button, N_click):
		try:
			more_button.click()
			N_click += 1
		except:
			not_clickable_msg = 'more button not clickable,' +\
				'N_click = {}'.format(N_click)
			log_time('error',msg=not_clickable_msg)
			set_pause(1)
			break

	def retry_loading_page(self, driver, N_click):
		#XXX Should this be set here? is it set previously and 
		# would that be more accurate?
		page_loaded = False
		N_tries = 0
		while not page_loaded and N_tries < 10:
			N_tries += 1
			page = driver.page_source
			page_filename = self.get_page_filename(N_click)

			self.write_out_page(page_filename, page)

			soup = BeautifulSoup(page, self.parser)
			
			results = self.get_results(page, soup)
			N_rows_new = self.get_number_rows(results)

			if N_rows_new > N_rows:
				page_loaded = True

			time.sleep(0.5)

	#XXX self.index_page_folder prob messed up
	def get_page_filename(self, N_click):
		page_filename = os.path.join(self.index_page_folder,
			url.replace('/', ']]]') + '_click_{}.html'.format(
			N_click))

		return page_filename

	#XXX slightly different than get_more_button so got its own func
	# Could incorporate as condition of getting last_page_flag
	# but that might slow things down due to the timeout
	def get_more_button_final(self, driver):
		try:
			more_button = driver.wait.until(
				ec.element_to_be_clickable((By.CLASS_NAME, 'more')))

		except TimeoutException:
			last_page_flag = True

			last_page_msg = 'exhausted page length,' +\
			'with N_click == {}'.format(N_click)
			log_time('error', msg=last_page_msg)

		return last_page_flag

	# Gets results which are sorted based on a certain filter.
	# Ex: if the click_sort was signal it would get results with highest
	# signal to lowest
	def get_click_sorted_results(self, company_count, click_sort, driver, url):
		if company_count > 0:
			more_button = self.get_more_button()
			last_page_flag = self.get_last_page_flag(more_button)

			css_selector_str = self.get_css_selector(click_sort)
			self.sort_companies_by_filter(css_selector_str)

			# Gets page html after it has been sorted by different filters
			page = driver.page_source
			soup = BeautifulSoup(page, self.parser)

			results = self.get_results(page, soup)
			N_rows_new = self.get_number_rows(results)
			quit_driver(driver)
			set_pause(1)
			return results

		# This continues (goes to next loop iter) and thus will not use
		# results in this iter. Therefore only the if statement needs
		# the return
		else:
			self.no_companies_close(url, driver)


	def no_companies_close(self, url, driver):
		empty_search_msg = 'empty search result with ' +\
			'target_url=={}'.format(url)
		log_time('error', msg=empty_search_msg)
		quit_driver(driver)
		set_pause(1)
		continue

	def write_entries_to_data_frame(self, output_fname, start_row, N_rows, results):
		entries = []
		#XXX this seems like it would error because entries doesn't exist. Should
		# it have a continue?
		if os.path.exists(output_fname):
			existing_output_file_msg = output_fname + \ 
				' exists, skipping'
			log_time('overwrite', msg=existing_output_file_msg)

		else:
			for i in range(start_row, N_rows):
				entry = dict()
				# a refers maybe to action tag in html?
				a = results[i]
				inner_url = self.get_inner_url(a) 
				title = self.get_title(a)

				entry = self.make_entries(entry, a, results,
					title, inner_url)
				self.log_entries(N_click, i, N_rows, title, entry)

				#XXX maybe make entries outside of the inner entry func
				# given that inner_page may not always be the last entry

				# gets final inner entry and appends each in entry to entries
				entries = self.interpret_inner_page(inner_url, entries, entry)

			# Writes entries to csv
			self.make_data_frame_output(entries, output_fname)
			self.last_page_break(last_page_flag)


	#XXX messed up probably
	def start(dir_lst, market_label_file, locations, signal_pair_list
			raised_pair_list, stage_list):

		self.construct_dir_tree(dir_list)

		market_filters = self.setup_market_filters(market_label_file)
		location_filters = self.setup_location_filters(locations)
		signal_filters = self.setup_signal_filters(signal_pair_list)
		featured_filters = self.setup_featured_filter()
		raised_filters = self.setup_raised_filter(raised_pair_list)
		stage_filters = self.setup_stage_filter(stage_list)

		self.generate_search_page_urls(use_existing_url_list=False,
			raised_filters, stage_filters,
			market_filters, featured_filters, 
			location_filters, signal_filters)



	def teardown(self):
		#XXX Logical loop?
		self.dr.teardown_driver(self.dr)



	




















