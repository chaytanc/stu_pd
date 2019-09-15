# vim: set sw=4 noet ts=4 fileencoding=utf-8:
# For not getting detected as a bot
import random
import time
import datetime
# Displays large datasets?
import pandas as pd
# Colors terminal text
import colorama
import sys
import os

COLOR_KIND = {
	'error' : colorama.Fore.RED,
	'e' : colorama.Fore.RED,
	'info' : colorama.Fore.YELLOW,
	'i' : colorama.Fore.YELLOW,
	'overwrite' : colorama.Fore.MAGENTA,
	'o' : colorama.Fore.MAGENTA,
	'highlight' : colorama.Fore.GREEN,
	'h' : colorama.Fore.GREEN
}

# Creates color coded logs when called in the form log_time('kind')
def log_time(kind='general', color_str=None, msg=''):
	if color_str is None:
		try:
			color_str = COLOR_KIND[kind]
		except KeyError:
			color_str = colorama.Fore.WHITE

	print(
		color_str + \
		str(datetime.datetime.now()) + \
		'\n' + \
		msg
		)
	colorama.Fore.RESET
	#sys.std.flush()

#XXX make program fail? Can't work w/out comp count...
#XXX write which function it was used in
#XXX kill program?, ask for different search criteria?
#XXX clear each time this runs? setting?
# debug_dir is dir it will write to, page is what it will write
# Page must be in string format
# Pretty General
def write_debug_error(debug_dir, page, msg=''):
	log_time('error', msg=msg)

	failed_case_fname = os.path.join(debug_dir,
		'failed_{}.html'.format(str(datetime.datetime.now())))

	fail_msg = 'failed to get crucial info, ' + \
		'saving error as {}'.format(failed_case_fname)

	log_time('error', msg=fail_msg)

	with open(failed_case_fname, 'w') as failed_f:
		#failed_f.write(page.decode('utf-8'))
		failed_f.write(page)

# General
def calc_pause(base_seconds=3., variable_seconds=5.):
	return base_seconds + random.random() * variable_seconds
	
PAUSE_TYPE = {
		1 : [ 'very_short', 0.5 ],
		2 : [ 'short', 3.0 ],
		3 : [ 'long', 10.0 ],
		4 : [ 'very_long', 100.0 ],
		5 : [ 'ultra_long', 1000.0 ]
	}

# Creates a function to pause for a varying set lengths
def set_pause(kind=1, seconds=None, logger=None):
	if seconds:
		kind_str = 'specific'
	else:
		kind_str, base_sec = PAUSE_TYPE[kind]
		seconds = calc_pause(base_sec, base_sec)

	if logger:
		logger('info', None, '{} pause: {}s...'.format(kind_str, seconds))

	time.sleep(seconds)

# d must be a directory which either exists or will exist
def check_dir_exists(d):
	if not os.path.exists(d):
		os.mkdir(d)

def construct_dir_tree(self, dir_list):
	for each in dir_list:
		dir_string_name = os.path.basename(each) 

		# Ex: if dir_list = ["code"] then the variable code contains
		# "code" and makes the dir when check_dir_exists runs
		setattr(self, dir_string_name, each)

		# Make a dir with the name dir_string_name if it did not exist
		check_dir_exists(getattr(self, dir_string_name))

	
# n_attempts is amount of times url was loaded
def load_url(driver, target_url, n_attempts, logger):
	try:
		driver.get(target_url)
		page_loaded = True
		if logger:
			logger(msg='page loaded successfully: {}'.format(target_url))

	except TimeoutException:
		page_loaded = False
		timeout_msg = 'loading page timeout' + target_url + \
			'attempt {}'.format(n_attempts)
		if logger:
			logger(kind='error', msg=timeout_msg)
		set_pause(1)

	except Exception as e:
		page_loaded = False
		other_exception_msg = 'Error loading page: {}'.format(e) + \
			'\n' + target_url + ' attempt {}'.format(n_attempts)
		if logger:
			logger(kind='error', msg=other_exception_msg)
		set_pause(1)

	return page_loaded

# limits loading attempt number; not too many queries
def limited_attempt_load_url(target_url, driver, 
	n_attempts_limit=3, logger=None):

	n_attempts = 0
	page_loaded = False
	while not page_loaded:
		n_attempts += 1
		if n_attempts >= n_attempts_limit:
			# Driver is running but page failed 
			driver.quit()
			if logger:
				load_limit_msg = \
					'loading page failed after {} attempts, ' \
					'now giving up on: '.format(n_attempts_limit) + \
					self.url
				logger(kind='error', msg=load_limit_msg)
			break
	
		else:
			page_loaded = load_url(driver, target_url, n_attempts, logger)

	return page_loaded



