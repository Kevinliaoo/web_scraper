import argparse
import logging
import json 
import os 
import re
import csv
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

csv_headers_econ_act = ['Industry', 'Ammount', 'Trade']
csv_headers_trading_dest = ['Destination', 'Ammount', 'Trade']

DATASETS_DIR = '../datasets'
ECON_DATA_NAME = "Economic_data.csv"
ECON_DATA_FILE = DATASETS_DIR + "/" + ECON_DATA_NAME

def _change_json_to_csv(country): 
	"""
	Convert data stored in JSON file to CSV

	:param country: Country name
	"""

	# Read json 
	cwd = os.getcwd()
	os.chdir(DATASETS_DIR)

	econ_activity = _read_json('{}_econ_act.json'.format(country))
	trade_countries = _read_json('{}_trade_dest.json'.format(country))

	_write_csv(csv_headers_econ_act[0], csv_headers_econ_act[1], csv_headers_econ_act[2], f'{country}_industry.csv', 'w+')
	
	for key, val in econ_activity.items(): 
		ammount_list, content_list = _separate_fields(val)

		for industry, ammount in zip(content_list, ammount_list):
			_write_csv(industry, ammount, key, f'{country}_industry.csv', 'a')

	_write_csv(csv_headers_trading_dest[0], csv_headers_trading_dest[1], csv_headers_trading_dest[2], f'{country}_trade.csv', 'w+')

	for key, val in trade_countries.items(): 
		ammount_list, content_list = _separate_fields(val)

		for country_, ammount in zip(content_list, ammount_list):
			_write_csv(country_, ammount, key, f'{country}_trade.csv', 'a')

	os.chdir(cwd)

def _write_csv(c1, c2, c3, filename, mode): 
	"""
	Inserts a line in a CSV file

	:param c1: First column content
	:param c2: Second column content
	:param c3: Third column content 
	:param filename: CSV file name
	:param mode: Open file mode
	"""
	# Check if file is a CSV file
	is_csv = re.compile(r'^.+\.csv$')
	if is_csv.match(filename) == None: 
		logger.info("Failed to write in CSV")
		return 

	with open(filename, mode) as f: 
		writer = csv.writer(f)
		writer.writerow([c1, c2, c3])

def _separate_fields(content):
	"""
	Extract essential information from a line of text 

	:param content: Text
	"""

	def _get_content(x, re_): 
		"""
		Inner function 
		Evaluates a regular expression and returns the essential part of the string 

		:param x: String 
		:param re_: Regular expression to evaluate 
		"""
		try: 
			c = re.findall(re_, x)[0].strip()
		except: 
			c = ""
		finally: 
			return c 

	ammount = r'\(\$.+?[MBT]{1,1}\),?'
	value = r'[A-Z]{1,1}.+'
	money = r'\d.+?[MBT]'

	ammount_list = re.findall(ammount, content)
	ammount_list = list(map(_get_content, ammount_list, [money for _ in range(len(ammount_list))]))
	ammount_list.pop()
	ammount_list = list(map(_string_to_int, ammount_list))
	content_list = re.split(ammount, content)
	content_list = list(map(_get_content, content_list, [value for _ in range(len(content_list))]))
	content_list.pop()

	return [ammount_list, content_list]

def _string_to_int(x): 
	"""
	Convert String to numerical value

	:param x: String value of number ending with M, B or T
	"""
	last_letter = x[-1]
	num = float(x[:-1])
	if last_letter == 'M': 
		ceros = 1e6
	elif last_letter == 'B': 
		ceros = 1e9
	elif last_letter == 'T': 
		ceros = 1e12
	elif last_letter == 'k': 
		ceros = 1e3

	try: 	
		return num * ceros
	except: 
		return x

def _read_json(filename):
	"""
	Return json file content 

	:param filename: File name
	""" 
	logger.info('Reading {} json file'.format(filename))
	with open(filename, 'r') as f: 
		data = json.load(f)

	return data

def _fix_csv_data(country): 
	"""
	Fix data in Economic_data.csv file

	:param country: Country name
	"""
	df = pd.read_csv(ECON_DATA_FILE)
	mask = df['Country'] == country
	country_df = df[mask]
	country_df = country_df.apply(_money_to_float)
	df[mask] = country_df

	cwd = os.getcwd() 
	os.chdir(DATASETS_DIR)

	df.to_csv(ECON_DATA_NAME, index=False)

	os.chdir(cwd)

def _money_to_float(money):
	"""
	Convert money format value to float 

	:param money: Content
	"""
	value = money.values[0] 
	if type(value) == str: 
		first = value[0]
		if first == '$': 
			# Convert money to float
			value = value.replace("$", "").replace(",", ".")
			return _string_to_int(value)
	return money

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'country', help = 'The country to fix data', type = str
	)
	
	arguments = parser.parse_args() 
	
	_change_json_to_csv(arguments.country)
	_fix_csv_data(arguments.country)