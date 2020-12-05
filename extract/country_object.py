import requests 
import bs4 

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