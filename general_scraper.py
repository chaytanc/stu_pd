# vim: set sw=4 noet ts=4 fileencoding=utf-8:
# For not getting detected as a bot
import random
import time
import datetime
# Displays large datasets?
import pandas as pd
# Colors terminal text
import colorama

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

