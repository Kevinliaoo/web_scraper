import requests 
import bs4 
import re

from common import config 

class Country: 

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
			data[data_list[NAME_INDEX].text] = data_list[INFO_INDEX].text

		return data

	def _scrape_export_import(self, index, export_re, import_re): 
		query = config()['economic_data']['queries']['economic_activity']
		result = self._select(query)[index].text

		export_statement = re.findall(r'{}'.format(export_re), result)[0]
		import_statement = re.findall(r'{}'.format(import_re), result)[0]

		export_start_index = result.find(export_statement)
		import_start_index = result.find(import_statement)

		export_goods = result[export_start_index+len(export_statement):import_start_index]
		import_goods = result[import_start_index+len(import_statement):-1]

		return {"Export": export_goods, "Import": import_goods}

	@property 
	def economic_activity(self): 
		"""
		Extract the main export and import industries of the country 
		"""
		index_ = int(config()['economic_data']['queries']['trade_p'])
		export_re = config()['economic_data']['queries']['export_re']
		import_re = config()['economic_data']['queries']['import_re']

		return self._scrape_export_import(index_, export_re, import_re)

	@property 
	def trade_destination(self): 
		"""
		Extract the export and import trading partners
		"""
		index_ = int(config()['economic_data']['queries']['destination_p'])
		export_re = config()['economic_data']['queries']['exp_dest_re']
		import_re = config()['economic_data']['queries']['imp_from_re']

		return self._scrape_export_import(index_, export_re, import_re)