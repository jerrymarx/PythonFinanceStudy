try:
	from urllib.request import urlopen
except:
	from urllib2 import urlopen
from bs4 import BeautifulSoup as soup
import re, datetime, csv, time, random

def delay():
	time.sleep(random.randint(10,20))

def get_page_soup(the_url):
	print('try to get data from:', the_url)
	client = urlopen(the_url, timeout=90)
	page_html = client.read()
	client.close()
	page_soup = soup(page_html, 'html.parser')
	return page_soup
	
def convert_date(date_str):
	return datetime.datetime.strptime(date_str, '%Y-%m-%d')

def get_divend_data(code):
	the_url = 'http://money.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/' + code + '.phtml'
	page_soup = get_page_soup(the_url)
	data_body = page_soup.find_all('tbody')[0]
	data = list()
	orig = list()
	for row in data_body.find_all('tr'):
		cols = row.find_all('td')
		if len(cols) == 1:
			continue
		public_date_str = cols[0].text.strip()
		register_date_str = cols[6].text.strip()
		divend_str = cols[3].text.strip()
		data.append({'public':convert_date(public_date_str), 
					 'register':convert_date(register_date_str) if register_date_str != '--' else convert_date(public_date_str),
					 'divend':float(divend_str)})
		orig.append(cols)
	return data, orig

def get_total_stock_data(code):
	the_url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_StockStructureHistory/stockid/' + code + '/stocktype/TotalStock.phtml'
	page_soup = get_page_soup(the_url)
	tables = page_soup.find_all('table', id=re.compile('historyTable*'))

	data = list()
	orig = list()
	for t in tables:
		for row in t.find_all('tr'):
			cols = row.find_all('td')
			if len(cols) != 0:
				date_str = cols[0].div.text.strip()
				count_str = cols[1].div.text.strip()[:-2]
				data.append({'date':convert_date(date_str), 'count':float(re.sub(r'[^0-9.]', '', count_str))})
				orig.append(cols)
	return data, orig

def get_total_stocks(date, stocks_data):
	count = 0.0
	for item in stocks_data:
		if date < item['date']:
			break
		else:
			count = item['count']
	return count
	
def get_divend(code):
	divend_data, divend_orig = get_divend_data(code)
	delay()
	stocks_data, stocks_orig = get_total_stock_data(code)
	
	current_year = 0
	for i in range(len(divend_data)-1, -1, -1):
		record = divend_data[i]
		reg_date = record['register']
		
		year_in_record = reg_date.year
		if current_year == year_in_record:
			record['year'] = year_in_record
		else:
			record['year'] = year_in_record - 1
		current_year = year_in_record
		
		record['total'] = get_total_stocks(reg_date, stocks_data)
	return divend_data, stocks_data

def load_AB_list(filename):
	full_dict = {}
	with open(filename, encoding='UTF-8') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			key = row[0]
			data = {'code_a':row[1], 'name_a':row[2], 'code_b':row[3], 'name_b':row[4]}
			full_dict[key] = data
	return full_dict
	
def load_divend_done_list(filename):
	done_set = set()
	try:
		with open('no_record.txt') as afile:
			for line in afile.readlines():
				key = line.strip()
				if key not in done_set:
					done_set.add(key)
	except:
		pass
		
	try:
		with open('divend.csv') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				key = row[0]
				if key not in done_set:
					done_set.add(key)
					#print('already had', key)
	except:
		pass
	return done_set
	
if __name__ == '__main__':
	no_record_file = 'no_record.txt'
	divend_csv = 'divend.csv'
	full_dict = load_AB_list('full_list.csv')
	done_set = load_divend_done_list(divend_csv)
	total = len(full_dict)
	done = len(done_set)
	for code in full_dict:
		if code in done_set:
			continue
		try:
			divend_data, stocks_data = get_divend(code)
		except:
			# raise
			print('Get data from the url failed')
			continue
		done += 1
		if len(divend_data) > 0:
			with open(divend_csv, 'a') as outfile:
				for record in divend_data:
					text = '%s,%s,%s,%s,%s\n' % (code, record['total'], record['divend'], record['year'], record['register'].date().isoformat())
					outfile.write(text)
		else:
			with open(no_record_file, 'a') as outfile:
				output.write(code + '\n')
		print('Progress ... [%d/%d] done' % (done, total))
		done_set.add(code)
		delay()