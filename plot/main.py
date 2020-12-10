import argparse
import logging
import pandas as pd 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = '../datasets'
ECONOMIC_DATA_FILE = DATA_DIR + '/Economic_data.csv'
COMPARING_COLS = ['GDP ', 'GDP PC ']

def _compare_countries(country1, country2): 

	df = pd.read_csv(ECONOMIC_DATA_FILE)
	selected_countries_mask = (df.Country == country1) | (df.Country == country2)
	selected_countries = df[selected_countries_mask]
	print(selected_countries[COMPARING_COLS])

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