import requests 
import bs4 
import re

from common import config 

class Country: 

	export_re = config()['economic_data']['queries']['export_re']
	import_re = config()['economic_data']['queries']['import_re']
	dest_re = config()['economic_data']['queries']['exp_dest_re']
	from_re = config()['economic_data']['queries']['imp_from_re']

	def __init__(self, country_name, abbreviation, url): 

		self.country_name = country_name
		self.abbreviation = abbreviation
		
		self._url = url
		self._html = None

		self._visit()

	def _visit(self): 
		"""
		Get the HTML content and store in self._html
		"""
		response = requests.get(self._url)
		response.encoding = 'utf-8'

		response.raise_for_status()

		self._html = bs4.BeautifulSoup(response.text, 'html.parser')

	def _select(self, query): 
		"""
		Get information about a section of the HTML page given the CSS selector

		:param query: CSS selector 
		"""

		return self._html.select(query)

	@property
	def economic_data(self): 
		"""
		Scrapes basi economic data of the country
		"""
		query = config()['economic_data']['queries']['basic_data']
		result = self._select(query)
		data = dict()
		NAME_INDEX = int(config()['economic_data']['queries']['basic_data_name_index'])
		INFO_INDEX = int(config()['economic_data']['queries']['basic_data_info_index'])

		for econ_data in result: 
			data_list = list(econ_data.find_all())
			data[Country._clean_parentesis(data_list[NAME_INDEX].text)[:-1]] = data_list[INFO_INDEX].text

		return data

	def _scrape_export_import(self, index, reg_1, reg_2): 
		"""
		:param index: Index number of the p tag inside the div tag 
		:reg_1: Regular expression 1 used to extract data inside the paragraph
		:reg_2: Regular expression 2 used to extract data inside the paragraph
		"""
		query = config()['economic_data']['queries']['economic_activity']
		result = self._select(query)[index].text

		# export_statement = re.match(r'{}'.format(export_re), result)
		industries_and_values = list(re.findall(r'{}'.format(reg_1), result)[0])
		destinations_and_values = list(re.findall(r'{}'.format(reg_2), result)[0])

		return {"Industries": industries_and_values, "Destinations": destinations_and_values}

	def _adapter(self, dict_1, dict_2, extract): 
		"""
		Estoy haciendo este adaptador porque la página web cambio, y tengo que hacer 
		cambios en la manera que estoy transmitiendo la información

		:param extract: 'activity' o 'trade'
		"""
		if extract == 'activity': 
			return {'Export': dict_1['Industries'], 'Import': dict_2['Industries']}
		elif extract == 'trade': 
			return {'Export': dict_1['Destinations'], 'Import': dict_2['Destinations']}

	def _extract_activity_or_destination(self, extract): 

		index_1 = int(config()['economic_data']['queries']['trade_p'])
		index_2 = int(config()['economic_data']['queries']['destination_p'])

		exports_ = self._scrape_export_import(index_1, Country.export_re, Country.dest_re)
		imports_ = self._scrape_export_import(index_2, Country.import_re, Country.from_re)
		
		return self._adapter(exports_, imports_, extract)

	@property 
	def economic_activity(self): 

		return self._extract_activity_or_destination('activity')

	@property 
	def trade_destination(self): 
		"""
		Extract the export and import trading partners
		"""

		return self._extract_activity_or_destination('trade')

	@staticmethod
	def _clean_parentesis(string_): 
		"""
		Extract all thext before ()
		"""
		str_ = ""
		for i in string_: 
			if i != '(': 
				str_ += i 
			else: break
		return str_