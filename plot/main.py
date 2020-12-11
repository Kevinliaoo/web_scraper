import argparse
import logging
import pandas as pd 

from matplotlib import pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = '../datasets'
ECONOMIC_DATA_FILE = DATA_DIR + '/Economic_data.csv'
COMPARING_COLS = ['GDP ', 'GDP PC ', 'Country']

def _compare_countries(country1, country2): 

	df = pd.read_csv(ECONOMIC_DATA_FILE)
	selected_countries_mask = (df.Country == country1) | (df.Country == country2)
	selected_countries = df[selected_countries_mask]
	_bar_plot(selected_countries[COMPARING_COLS], COMPARING_COLS[0])
	_bar_plot(selected_countries[COMPARING_COLS], COMPARING_COLS[1])
	_plot_economic_activity(country1, country2)

def _bar_plot(df, category):
	"""
	Bar plots comparing two countries data

	:param df: Dataframe of shape (2, ?)
	:param category: Category of the datafeame to be compared
	"""
	country_1 = df.Country.values[0].capitalize()
	country_2 = df.Country.values[1].capitalize()
	plt.title("{} vs {} {}".format(country_1, country_2, category))
	plt.bar(
		x = [country_1, country_2], 
		height = [df[category].values[0], df[category].values[1]]
	)
	plt.xlabel("Country")
	plt.ylabel(category)
	#plt.yticks(range(int(max(df[category].values))))
	for i in range(len(df['Country'].values)):
		plt.text(
			i, 0, 
			s = "${:.2f}".format(df[category].values[i])
		)
	plt.show()

def _plot_economic_activity(country1, country2): 
	"""
	:param country1: Country 1 name
	:param country2: Country 2 name
	"""
	export_goods, import_goods = _get_economic_activity_data(country1, country2)
	export_industries = export_goods.keys()
	export_values = export_goods.values()
	import_industries = import_goods.keys()
	import_values = import_goods.values()

	def plot_(type_, trade_industries, trade_values): 
		"""
		Makes a bar plot of export or import industries 
		"""
		plt.title(f"{type_.capitalize()} industries of {country1.capitalize()} vs {country2.capitalize()}")
		plt.bar(
			x = trade_industries, 
			height = [int(x) for (x, _) in trade_values], 
			label = country1.capitalize(), 
			color = "r"
		)
		plt.bar(
			x = trade_industries, 
			height = [int(x) for (_, x) in trade_values], 
			label = country2.capitalize(), 
			color = "b"
		)
		plt.legend()
		plt.xticks(rotation=45)
		plt.show()

	plot_("export", export_industries, export_values)
	plot_('import', import_industries, import_values)


def _get_economic_activity_data(country1, country2): 

	def create_dict(country1_vals, country2_vals):
		"""
		Builds a dictionary containing all industries activitues of both countries. 
		Industry: 0

		:param country1_vals: List containig industries of country_1
		:param country2_vals: List containig industries of country_2 
		"""
		dict_ = dict() 
		for i, j in zip(country1_vals, country2_vals): 
			dict_[i] = 0 
			dict_[j] = 0 
		return dict_

	def fill_dict(dict_, country1_df, country2_df):
		"""
		:param dict_: Dictionary to be filled
		"""
		for key in dict_.keys():
			value_1 = extract_value_from_list(country1_df[country1_df.Industry.values == key]['Ammount'].values)
			value_2 = extract_value_from_list(country2_df[country2_df.Industry.values == key]['Ammount'].values)
			
			dict_[key] = [value_1, value_2]

		return dict_

	def extract_value_from_list(list_):
		"""
		Extracts the first value of a list or returns 0 if no value is in the list 

		:param list_: List
		""" 
		if len(list_) == 0: 
			return 0 
		else: 
			return list_[0]

	country1_df = pd.read_csv(f"{DATA_DIR}/{country1}_industry.csv")
	country2_df = pd.read_csv(f"{DATA_DIR}/{country2}_industry.csv")
	country1_exports = country1_df[country1_df.Trade == "Export"]
	country2_exports = country2_df[country2_df.Trade == "Export"]
	country1_imports = country1_df[country1_df.Trade == "Import"]
	country2_imports = country2_df[country2_df.Trade == "Import"]

	export_goods = create_dict(country1_exports.Industry.values, country2_exports.Industry.values)
	import_goods = create_dict(country1_imports.Industry.values, country2_imports.Industry.values)

	export_goods = fill_dict(export_goods, country1_exports, country2_exports)
	import_goods = fill_dict(import_goods, country1_imports, country2_imports)

	return (export_goods, import_goods)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'country1', help = 'First country', type = str
	)
	parser.add_argument(
		'country2', help = "Second country", type = str
	)
	
	arguments = parser.parse_args() 
	
	_compare_countries(arguments.country1, arguments.country2)
