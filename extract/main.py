import argparse
import logging 
import requests
import bs4
import os 
import csv
import re
import json 

import pandas as pd 
import numpy as np

from common import config 
from country_object import Country

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

csv_headers = None

def getCountriesCode(): 
	"""
	Gets the ISO 3166-1 alpha-3 three-letters country code of each country

	:returns: Dictionary containing {Country: Code}
	"""
	url = config()['countries_data']['url']

	response = requests.get(url)
	response.encoding = 'utf-8'
	response.raise_for_status()

	html = bs4.BeautifulSoup(response.text, 'html.parser')
	
	list_ = dict() 
	for index, value in config()['countries_data']['queries'].items(): 
		for i in html.select(value)[0].findChildren('li'):
			# Replace the space with a '_' in countries name with more than one word to form single-word names
			if len(i.findChild('a').text.lower().split(' ')) > 1: 
				country = '_'.join(i.findChild('a').text.lower().split(' ')) 
				list_[country] = i.findChild('span').text.lower()
			else: 
				list_[i.findChild('a').text.lower()] = i.findChild('span').text.lower()

	return list_

def _scrape_country_economic_activity(name, code): 
	
	logging.info("Scraping economic activity information about {}".format(name.capitalize()))
	host = config()['economic_data']['url']
	host += '/{}'.format(code)
	country = Country(name, code, host)

	datasets_path = '../datasets'
	_save_json(country.economic_activity, datasets_path, "{}_econ_act.json".format(name))
	_save_json(country.trade_destination, datasets_path, "{}_trade_dest.json".format(name))

def _save_json(dict_, path, filename): 
	"""
	Saves a dictionary to a json file

	:param dict_: Dictionary to be saved
	:param path: Directory path to save the data
	:param filename: File name
	"""
	cwd = os.getcwd() 
	os.chdir(path) 

	with open(filename, 'w') as f: 
		json.dump(dict_, f, indent=4)

	os.chdir(cwd)

def _scrape_country_info(name, code): 
	"""
	Get basic economic information about a country and store data in datasets/Economic_data.csv
	"""
	logging.info('Scraping information about {}'.format(name.capitalize()))

	host = config()['economic_data']['url']
	host += '/{}'.format(code)

	country = Country(name, code, host)
	_save_country_info(country, country.economic_data)

def _save_country_info(country, economic_data): 
	"""
	Save all country economic information in a row of Economic_data.csv

	:param country: Country 
	:param economic_data: 
	"""
	global csv_headers

	FILENAME = "Economic_data.csv"
	FILEDIR = '../datasets'
	res = _check_file(FILEDIR, FILENAME)
	
	if res == -1: 
		_create_dir('../', 'datasets')
		_create_dataset(FILEDIR, FILENAME)
	elif res == 0: 
		# Create the file 
		_create_dataset(FILEDIR, FILENAME)

	# Build row
	row = [] 
	econ_data_index = 0
	for index, col in enumerate(csv_headers[:-1]): 
		if col in list(economic_data.keys()): 
			row.append(list(economic_data.values())[econ_data_index])
			econ_data_index += 1
		else: 
			row.append(np.nan)
	row.append(country.country_name)
	logging.info('Saving infromation to {}'.format(FILENAME))
	with open('{}/{}'.format(FILEDIR, FILENAME), 'a') as f: 
		writer = csv.writer(f)
		writer.writerow(row)

def _check_file(path, filename):
	"""
	Chechs if a file exists in a directory 

	:param path: Path to the directory 
	:param filename: Filename 

	:returns: 
		-1: The directory does not exist 
		 0: The directory does exist but not the file
		 1: The file exists 
	""" 
	logging.info('Checking if {} exists in {}'.format(filename, path))

	response = 0 
	cwd = os.getcwd() 

	try: 
		os.chdir(path)
		if filename in os.listdir(): 
			response = 1
		else: 
			response = 0
	except: 
		response = -1
	finally: 
		os.chdir(cwd)
		return response

def _create_dir(path, dirname): 
	"""
	Creates a directory in a given path 

	:param path: Path 
	:param dirname: Directory name
	"""
	logging.info('Creating directory {} in {}'.format(dirname, path))

	cwd = os.getcwd()
	os.chdir(path)
	os.mkdir(dirname)
	os.chdir(cwd)

def _create_dataset(path, filename):
	"""
	Creates Economic_data.csv with the csv_headers
	This function must be run only one time for each excecution 

	:param path: Path to directory where to create the file
	:param filename: Filename
	"""
	logging.info('Creating file {} in {}'.format(filename, path))

	global csv_headers

	cwd = os.getcwd()
	os.chdir(path)
	
	with open(filename, mode='w+') as f: 
		writer = csv.writer(f)
		writer.writerow(csv_headers)

	os.chdir(cwd)

def _read_dataset(file): 
	logging.info('Reading dataset {}'.format(file))
	df = pd.read_csv(file)
	print(df)

def _set_csv_header(country='Argentina', code='arg'): 
	"""
	Configure CSV headers for Economic_data.csv
	I use Argentina to set the headers since Argentina has no information missing 
	"""
	global csv_headers

	# Get directly from file if the file already exist
	res = _check_file('../datasets', 'Economic_data.csv');
	if res == 1:
		with open('../datasets/Economic_data.csv', 'r') as f: 
			csv_reader = csv.reader(f)
			csv_headers = next(csv_reader)
		return 

	logging.info("Configuring CSV headers")

	host = config()['economic_data']['url']
	host += '/{}'.format(code)

	country = Country(country, code, host)
	csv_headers = list(country.economic_data.keys())
	csv_headers = list(map(Country._clean_parentesis, csv_headers))
	csv_headers.append("Country")

if __name__ == '__main__':
	
	_set_csv_header()

	parser = argparse.ArgumentParser() 
	countries_name_list = list(getCountriesCode().keys())
	parser.add_argument(
		'country', help = 'The country to investigate', type = str, choices = countries_name_list
	)
	
	arguments = parser.parse_args() 
	# Check if country is already screaped
	is_checked = False
	try: 
		df = pd.read_csv('../datasets/Economic_data.csv')['Country'].values.tolist()
		if arguments.country in df: 
			logger.info('Information about {} is already available!'.format(arguments.country.capitalize()))
			is_checked = True
		else: is_checked = False
	except: 
		is_checked = False

	if is_checked == False: 
		_scrape_country_info(arguments.country, getCountriesCode()[arguments.country])
		_scrape_country_economic_activity(arguments.country, getCountriesCode()[arguments.country])