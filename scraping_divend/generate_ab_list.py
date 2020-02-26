# Name: generate_ab_list.py
# Current version: 0.2
# Copyright 2020 TsinghuaChat
# License: BSD license
# Dev and debugged with Python 3.6.5
#
# This tool is used dto generate the full_list.csv, the format in this csv are
# Code, A Code, A Name, B Code, B Name
# A field maybe empty if it is not avaiable
#
# The data source is from Shang Hai Stock Exchange official website and Shen Zhen stock Exchange official website.
#
# From http://www.sse.com.cn/assortment/stock/list/share/, download stock list for Main Board A, Main Board B and Sci-Tech Innovation Board
# http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1
# http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=2
# http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=8 
# The files ext is .xls, but they are plain text files, open it, replace all '\t  ' with ',' and save as sha.csv, shb.csv and shk.csv

# From http://www.szse.cn/market/companys/company/index.html, down load stock list for Main Board A and Main Board B, notice the random in URL may change.
# http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1&random=0.6543691230337494
# http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab2&random=0.238366504422175
# The files are .xlsx, open them with Excel and save as sza.csv and szb.csv

import csv

def read_sz_csv(filename):
	with open(filename, 'r', encoding='UTF-8') as csvfile:
		reader = csv.reader(csvfile)
		header = next(reader) #skip the header line
		for row in reader:
			code_a = row[5].strip()
			name_a = row[6].strip()
			code_b = row[10].strip()
			name_b = row[11].strip()
			yield code_a, name_a, code_b, name_b

def read_sh_csv(filename):
	with open(filename, 'r') as csvfile:
		reader = csv.reader(csvfile)
		header = next(reader)
		for row in reader:
			company_code = row[0].strip()
			code = row[2].strip()
			name = row[3].strip()
			yield company_code, code, name


def load_sz_a(full):
	for code_a, name_a, code_b, name_b in read_sz_csv('sza.csv'):
		info = {'code_a':code_a, 'name_a':name_a, 'code_b':code_b, 'name_b':name_b }
		full[code_a] = info
		if len(code_b) > 0:
			full[code_b] = info 

def load_sz_b(full):
	for code_a, name_a, code_b, name_b in read_sz_csv('szb.csv'):
		if code_a in full or code_b in full:
			continue
		full[code_b] = {'code_a':code_a, 'name_a':name_a, 'code_b':code_b, 'name_b':name_b }
		
def load_sh_a(full):
	for company_code, code, name in read_sh_csv('sha.csv'):
		full[code] = {'code_a':code, 'name_a':name, 'code_b':'', 'name_b':''}
		
def load_sh_k(full):
	for company_code, code, name in read_sh_csv('shk.csv'):
		full[code] = {'code_a':code, 'name_a':name, 'code_b':'', 'name_b':''}
		
def load_sh_b(full):
	for company_code, code, name in read_sh_csv('shb.csv'):
		if company_code in full:
			info = full[company_code]
			info['code_b'] = code
			info['name_b'] = name
			full[company_code] = info
		else:
			info = {'code_a':'', 'name_a':'', 'code_b':code, 'name_b':name}

if __name__ == '__main__':
	full_dict = dict()
	load_sz_a(full_dict)
	load_sz_b(full_dict)
	load_sh_a(full_dict)
	load_sh_b(full_dict)
	load_sh_k(full_dict)
	
	with open('full_list.csv', 'w', encoding='UTF-8') as csvfile:
		for k, v in sorted(full_dict.items()):
			text = '%s,%s,%s,%s,%s\n' % (k, v['code_a'], v['name_a'], v['code_b'], v['name_b'])
			csvfile.write(text)

			