import pandas as pd
import os
'''
data = pd.read_csv('00386.hk.csv')
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)
return date



hk = pd.read_csv('CNYHKD.csv', delimiter='\t')
del hk['Unnamed: 0']
hk['Date'] = pd.to_datetime(hk['Date'])
hk.set_index('Date', inplace=True)
hk.sort_index(inplace=True)
'''

class YahooHistoryDataDownloader:
	CRUMBLE_REGEX = r'CrumbStore":{"crumb":"(.*?)"}'
	COOKIE_REGEX = 
	

def get_code(code):
	if code.find('.') != -1:
		return code
	if len(code) == 6:
		if code[0] == '6' or code[0] == '9':
			return code + '.SS'
		elif code[0] == '0' or code[0] == '2' or  code[0] == '3':
			return code + '.SZ'
	if len(code) == 5:
		if code[0] == '0':
			return code[-4] + '.HK'
		else:
			return code + '.HK'
			
def load_history_data(code):
	if not os.path.exists(get_history_data_file_path(code)):
		download_history_data(code)
	else:
		pass
		
def download_history_data(code):
	