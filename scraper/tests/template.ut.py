#! /usr/bin/python

# vim: set sw=4 noet ts=4 fileencoding=utf-8:

import unittest
import sys
sys.path.append('./../')
from XXXfile import XXXclass


class TestXXXclass(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		pass

	def setUp(self):
		pass

	def test_XXX_100(self):
		pass
		#assert 

	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		pass

if __name__ == '__main__':
	unittest.main()
	
