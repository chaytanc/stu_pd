#!/usr/bin/python3
# vim: set sw=4 noet ts=4 fileencoding=utf-8:

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from scraper_new import Scraper
from driver import Driver

class Main():
	
	def __init__(self):
		# Locations have a number associated in the url which may be found
		# by inputting location in website and then getting number from parsed
		# url. XXX Maybe it would be better to apply filters by using website
		# interface rather than manipulating url? not worth it...
		self.filter_dict = {
			'type' : '',
			'locations': [''],
			'markets' : '',
			'tech' : '',
			'investors' : '',
			'team' : '',
			'stage' : ''}

		# Raised is between 10K - 100M 
		# Signal is between 1-10
		self.ranged_filter_dict = {
			'raised' : [10000, 15000],
			'signal' : []}

		self.root_url = 'https://angel.co/companies?'
		self.parser = 'lxml' 
		self.driver = Driver.get_driver()

#		self.visit_inner = True  # inner pages are comapny detail pages
#		self.inner_page_redownload = False  # if inn
#		self.mute_display = False
		
		# Dirs here will be created if they don't already exist
		self.dir_lst = ['output', 'output/debug_dir']

	def main(self):
		scraper = Scraper(self.dir_lst)
		scraper.parse_main_page(self.root_url, self.filter_dict, 
			self.ranged_filter_dict, self.parser)
#		graphviz = GraphvizOutput()
#		graphviz.output_file = 'functions.png'
#	
#		with PyCallGraph(output=graphviz):
#			scraper.parse_main_page(self.root_url, self.filter_dict,
#				self.parser)


if __name__ == '__main__':
	main = Main()
	main.main()
		
