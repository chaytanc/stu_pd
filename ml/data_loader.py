#!/usr/bin/env python3
# vim: set sw=4 noet ts=4 fileencoding=utf-8:

import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
#import torch.nn as nn
#import torch.optim as optim

# This class redefines Dataset functions so that we can use dataloader
class Company_Name_Dataset(Dataset):
	def __init__(self):
		#XXX get pd dataset and select 'title' of company only
		#XXX pass in output location to read
		df = pd.read_csv('../my_scraper/output/out.csv')
		title_col = df['title'].values
		raised_col = df['raised'].values
		#XXX need to test that raised and title col are same length
		print(raised_col)
		print('\n' + 'RAISED')

		title_col = self.preprocess_words(title_col)
		raised_col = self.preprocess_numbers(raised_col)
		#XXX Technically not necessary because arrays are passed by reference
		title_col = self.same_dim(title_col)
		raised_col = self.same_dim(raised_col)

		# This took values from title column and turned to a torch tensor
		titles = torch.tensor(title_col, requires_grad=True)
		raised = torch.tensor(raised_col, requires_grad=True)
		print(titles)
		print('\n' + 'TITLES')
		print(raised)
		print('\n' + 'RAISED')

	# Overriding __len__ and __getitem__ is necessary for custom Dataset
	# Length of your dataset
	def __len__(self, titles):
		data_len = len(titles)
		return data_len 

	# Which items you will use from your dataset
	def __getitem__(self, idx):
		sample = self.titles[idx]
		return sample

	def preprocess_words(self, col):
		''' Converts a list of strings into a list of arrays.
		>>> col = ['Quen']
		>>> ti = t.preprocess_words(col)
		>>> ti[0]
		[81.0, 117.0, 101.0, 110.0]
		'''
		# Empty list which will fill with lists of each title in integer form
		num_col = []
		for title in col:
			# Make an empty list for each company name in col, this will fill w/
			# ascii values of the characters
			num_title = []
			for char in title:
				# Converts chars to ascii ints then ints to floats
				i = ord(char)
				f = float(i)
				num_title.append(f)
			num_col.append(num_title)
		#XXX use logger?
		#print(str(len(num_col)) + " LENGTH")
		return num_col

	def same_dim(self, array):
		''' This func takes an array of strings which have been turned into
		arrays of ascii numbers to represent their characters
		(using preprocess_words) and pads the inner arrays representing a word
		with -1 so that they are all the length of the longest array '''

		longest_element = max(array, key=len)
		max_len = len(longest_element)
		for each_array in array:
			len_diff = max_len - len(each_array)
			for char in range(len_diff):
				each_array.append(float(-1))
		return array

	# Duck-typing does not work in this method because tensors and math ARE
	# dependent on datatype.
	def preprocess_numbers(self, num_col):
		''' This processes a column/array of numbers of the datatype string
		and converts them to floats, as well as converting any non number
		characters to ascii. 
		
		#>>> col = ['$1400', '150', '$600a2']
		#>>> t.preprocess_numbers(col)
		'''
			
		processed_col = []
		for obj in num_col:
			float_array = []
			digit_count = 0
			# Check if each character is a digit
			for char in obj:
			#XXX These conversions should be a separate function for testing.
			#XXX may need to provide for any non ascii chars for all preprocess
				# If it is a digit, add it to a decimal place of an element 
				# in the array representing the dollar amount by multiplying 
				# existing # by ten and then adding it. Do this as a float.
				if char.isdigit():
					# The first digit that is found saves the location of the
					# array that it is appended to
					if digit_count == 0:
						array_loc = len(float_array)
						float_array.append(float(char))
					else:
						float_array[array_loc] *= 10
						float_array[array_loc] += float(char)
					digit_count += 1
				# If not a digit, convert to ascii
				# Add ascii to new raised array
				else:
					char = float(ord(char))
					float_array.append(char)

			# Append each converted raised amount to a list of all raised
			processed_col.append(float_array)
		return processed_col

	#XXX
	def char_digits_to_float(self):
		'''
		Input(previous_char, digit, float_array, digit_count, num_loc)
		if previous_char.isdigit() digit_count > 0:
			float_array[num_loc] *= 10
			float_array[num_loc] += float(digit)
		else:
			float_array.append(float(digit))
		'''

#	def convert_alphanum_to_float(char, float_array):
#		'''
#		Params:
#			char: a char that will be checked and converted to a float. If
#				it is a digit it will sum with other char digits in a base ten
#				fashion.
#			float_array: This can be empty. It will store the floats.
#
#		This function checks if a character is a digit and converts it to a
#		float accordingly. If it is a digit, the func will consider the 
#		following digits to construct a base ten number from the chars.
#		The values of original number (which is passed as chars here) should
#		not have a decimal form on the end.
#		'''
#		# If it is a digit, add it to a decimal place of an element 
#		# in the array representing the dollar amount by multiplying 
#		# existing # by ten and then adding it. Do this as a float.
#		count = 0
#		if char.isdigit():
#			# The first digit that is found saves the location of the
#			# array that it is appended to
#			if count = 0:
#				array_loc = len(float_array)
#				float_array.append(float(char))
#			#XXX this part could be its own function
#			else:
#				float_array[array_loc] = float_array[array_loc] * 10
#				float_array[array_loc] += float(char)
#			count += 1
#
#		# If not a digit, convert to ascii
#		# Add ascii to new raised array
#		else:
#			char = float(ord(char))
#			float_array.append(char)
#		return float_array



if __name__ == '__main__':
	import doctest
	doctest.testmod(extraglobs={'t': Company_Name_Dataset()})

# example of how to use this dataset, prob not the actual implementation
# of accessing this dataset
	#dataset = Company_Name_Dataset
	#training_data = DataLoader(dataset=dataset, batch_size=20, 


