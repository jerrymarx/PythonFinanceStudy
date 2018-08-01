# Name: generate_ab_list.py
# Current version: 0.1
# Dev and debugged with Python 2.7
#
# This tool is used to generate full_list.csv, the format in csv is 
# Stock Code, Stock A Code (if has), Stock A Name (if has), Stock B Code (if has), Stock B Name (if has), Total volume A, Total volume B
#
# The data source is from ShangHai Stock Exchange official website and ShenZhen Stock Exchange official website.
# http://www.sse.com.cn/assortment/stock/list/share/, the downloaded files are .xls, open it with notepad++,
# replace all '\t  ' as ',' and rename as sha.csv and shb.csv
# http://www.szse.cn/market/stock/list/index.html, the downloaed files are .xlsx, open them with Excel and save 
# as sza.csv and szb.csv
#
# Put this file and sha.csv, shb.csv, sza.csv, szb.csv in same folder, run 'python generate_ab_list.py', will
# generate a output file as full_list.csv


import csv

full_dict = {}

def read_sz_csv(filename):
	with open(filename, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		header = True
		for row in reader:
			if header:
				header = False
				continue
			code_a = row[5].strip()
			name_a = row[6].decode('UTF-8').strip()
			code_b = row[10].strip()
			name_b = row[11].decode('UTF-8').strip()
			total_a_str = row[8].strip().replace(',','')
			total_b_str = row[13].strip().replace(',','')
			total_a = float(total_a_str)/10000 if total_a_str != '' else 0.0
			total_b = float(total_b_str)/10000 if total_b_str != '' else 0.0
			yield code_a, name_a, code_b, name_b, total_a, total_b

def read_sh_csv(filename):
	with open(filename, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		header = True
		for row in reader:
			if header:
				header = False
				continue
			code_a = row[0].strip()
			name_a = row[1].strip()
			code_b = row[2].strip()
			name_b = row[3].strip()
			text = row[5].strip().replace(',','')
			total = float(text) if text != '' else 0.0
			yield code_a, name_a, code_b, name_b, total
			
for code_a, name_a, code_b, name_b, total_a, total_b in read_sz_csv('sza.csv'):
	#print 'Code A:', code_a, 'Name_A:', name_a, 'Code_B:', code_b, 'Name_B:', name_b
	if len(code_b) == 0:
		full_dict[code_a] = {'code_a':code_a, 'name_a':name_a, 'code_b':'', 'name_b':'', 'total_a':total_a, 'total_b':total_b}
	else:
		d = {'code_a':code_a, 'name_a':name_a, 'code_b':code_b, 'name_b':name_b, 'total_a':total_a, 'total_b':total_b}
		full_dict[code_a] = d
		full_dict[code_b] = d
		 
for code_a, name_a, code_b, name_b, total_a, total_b in read_sz_csv('szb.csv'):
	if code_a in full_dict:
		continue
	if code_b in full_dict:
		continue
	full_dict[code_b] = {'code_a':'', 'name_a':'', 'code_b':code_b, 'name_b':name_b, 'total_a':total_a, 'total_b':total_b}
	
for dummy_c, dummy_n, code_a, name_a, total in read_sh_csv('sha.csv'):
	full_dict[code_a] = {'code_a':code_a, 'name_a':name_a.decode('UTF-8'), 'code_b':'', 'name_b':'', 'total_a':total, 'total_b':0.0}
	
for code_a, name_a, code_b, name_b, total in read_sh_csv('shb.csv'):
	if code_a in full_dict:
		item = full_dict[code_a]
		item['code_b'] = code_b
		item['name_b'] = name_b.decode('UTF-8')
		item['total_b'] = total
		full_dict[code_b] = item
	else:
		full_dict[code_b] = {'code_a':'', 'name_a':'', 'code_b':code_b, 'name_b':name_b.decode('UTF-8'), 'total_a':0.0, 'total_b':total}

import codecs
csvfile = codecs.open('full_list.csv', 'w', 'UTF-8')
for k, v in sorted(full_dict.items()):
	text = '%s,%s,%s,%s,%s,%s,%s\n' % (k, v['code_a'], v['name_a'], v['code_b'], v['name_b'], str(v['total_a']), str(v['total_b']))
	csvfile.write(text)
	
csvfile.close()
