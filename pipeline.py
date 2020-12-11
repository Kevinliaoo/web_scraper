import logging 
import subprocess
import os 
import extract

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(): 
	
	_ask_countries()

def _ask_countries(): 
	remaining = 2
	selected_countries = []

	while remaining != 0: 
		input_ = str(input("Introduce a country ({} remaining): \n>".format(remaining))).strip().lower()
		
		if _run_extract(input_): 
			remaining -= 1
			selected_countries.append(input_)
	
	for country in selected_countries: 
		_run_transform(country)

	subprocess.run(['python', 'main.py', selected_countries[0], selected_countries[1]], cwd='./plot')

def _run_extract(country):
	"""
	Runs main.py on extract to extract a country's economic data

	:param country: Country name
	"""
	response = subprocess.run(['python', 'main.py', country], cwd='./extract')
	
	if response.returncode == 2: 
		print("Error! Invalid country") 
		return False

	return True

def _run_transform(country): 
	"""
	Runs main.py on transform to transform countries data

	:param country: Country name
	"""
	response = subprocess.run(['python', 'main.py', country], cwd='./transform')

if __name__ == '__main__':
	
	main()