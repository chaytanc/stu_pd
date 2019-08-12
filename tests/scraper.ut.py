#! /usr/bin/python3
# vim: set sw=4 noet ts=4 fileencoding=utf-8:

import unittest
import sys
import os
sys.path.append('./../')
from scraper_new import Scraper
from driver import Driver


class TestAngelListScraper(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		pass

	def setUp(self):
		driver = Driver.get_driver()
		base_url = "https://angel.co/companies?stage=Seed"
		self.scraper = AngelListScraper(base_url, driver)

	def test_limited_load_url_100(self):
		page_loaded = self.scraper.limited_load_url()
		assert page_loaded 
		
		page_loaded = self.scraper.limited_load_url(n_attempts_limit=0)
		self.assertFalse(page_loaded)
		#XXX
		skipTest()

	def test_check_dir_exists_200(self):
		# setup
		self.new_dir = "./new_dir"

		# test
		self.scraper.check_dir_exists(self.new_dir)
		assert os.path.exists(self.new_dir)

		# teardown self.new_dir if made
		if os.path.exists(self.new_dir):
			os.rmdir(self.new_dir)
		#XXX
		skipTest()

	def test_construct_dir_tree_300(self):
		# setup dirs for testing
		dir_lst = ["x", "x/y"]

		# test
		self.scraper.construct_dir_tree(dir_lst)
		assert(self.scraper.x)
		assert(self.scraper.y)

		# teardown dir_lst if constructed
		for d in dir_lst:
			if os.path.exists(d):
				os.rmdir(d)
		#XXX
		skipTest()

	def test_get_ranged_filter_url_appendage_400(self):
		ranged_filter_dict = {raised : [10000, 400000]}
		self.scraper.get_ranged_filter_url_appendage(ranged_filter_dict)
		assert 

	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		pass

if __name__ == '__main__':
	unittest.main()
	
