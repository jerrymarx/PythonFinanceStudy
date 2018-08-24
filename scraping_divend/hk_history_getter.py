from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
from threading import Timer
from datetime import datetime
import re, urllib, time, random, csv, os

def get_HK_stock_history_range(code):
	the_url = 'http://stock.finance.sina.com.cn/hkstock/api/jsonp.php//HistoryTradeService.getHistoryRange?symbol=' + code
	print('Get history range for', code, 'from', the_url, end='', flush=True)
	for i in range(10):
		client = None
		try:
			print('.', end='', flush=True)
			client = urlopen(the_url, timeout=10)
			t = Timer(10, close_response, [client, ])
			t.start()
			text = client.read().decode('gbk')
			t.cancel()
			client.close()
			break
		except:
			if client:
				client.close()
	else:
		print('Failed')
		return None, 0, 0, 0

	rp = re.compile('\(\(\{max:\"(.*)-(.*)\",min:\"(.*)-(.*)\".*')
	matches = re.findall(rp, text)
	print('Done')
	return matches[0]
	
def x_history_range(max_year, max_season, min_year, min_season):
	max_y = int(max_year)
	max_s = int(max_season)
	min_y = int(min_year)
	min_s = int(min_season)
	while(max_y != min_y or max_s != min_s):
		y, s = min_y, min_s
		min_s += 1
		if min_s == 5:
			min_y += 1
			min_s = 1
		yield y, s
	yield max_y, max_s

def close_response(client):
	client.close()
	
def get_HK_stock_history(code, year, season):
	the_url = 'http://stock.finance.sina.com.cn/hkstock/history/' + code + '.html'
	values = {'year': str(year), 'season':str(season)}
	data = urllib.parse.urlencode(values).encode('utf-8')
	req = urllib.request.Request(the_url, data)
	print('Try to get history data of', code, ',', year, 'year', season, 'season', end=' ', flush=True)
	for i in range(5):
		print('>', end='', flush=True)
		client = None
		try:
			client = urlopen(req, timeout=10)
			print('.', end='', flush=True)
			t = Timer(10, close_response, [client, ])
			t.start()
			content = client.read()
			t.cancel()
			print('.', end='', flush=True)
			page_soup = soup(content, 'html.parser')
			print('.', end='', flush=True)
			client.close()
			break
		except:
			if client:
				client.close()
			continue
	else:
		print('Failed')
		return None
	print('Done')
	
	wrap_div = page_soup.find_all('div', id='sub01_c2')[0]
	lines = list()
	first_line = True
	for tr in wrap_div.find_all('tr'):
		if first_line:
			first_line = False
			continue
		tds = tr.find_all('td')
		if len(tds) == 1:
			continue
		trade_date 	= tds[0].text.strip()
		close 		= tds[1].text.strip()
		change 		= tds[2].text.strip()
		pct_change 	= tds[3].text.strip()
		vol 		= tds[4].text.strip()
		amount		= tds[5].text.strip()
		open		= tds[6].text.strip()
		high		= tds[7].text.strip()
		low			= tds[8].text.strip()
		temp = [trade_date, open, high, low, close, change, pct_change, vol, amount, ]
		lines.append(','.join(temp))
	lines.reverse()
	return lines
	
def get_HK_stock_whole_history(code):
	max_year, max_season, min_year, min_season = get_HK_stock_history_range(code)
	if max_year is None:
		return None
	history = list()
	for year, season in x_history_range(max_year, max_season, min_year, min_season):
		# print('year:', year, 'season:', season)
		lines = get_HK_stock_history(code, year, season)
		if lines is None:
			break
		# print('Get', len(lines), 'lines data')
		history.extend(lines)
		time.sleep(random.randint(1,5))
	return history

def history_data_filename(code):
	return os.path.join('data', code + '.HK.csv')
	
def save_to_file(code, history):
	with open(history_data_filename(code), 'w') as csvfile:
		csvfile.write('trade_date,open,high,low,close,change,pct_change,vol,amount\n')
		for line in history:
			csvfile.write(line)
			csvfile.write('\n')

def get_latest_date_from_file(code):
	last_line = None
	with open(history_data_filename(code)) as csvfile:
		reader = csv.reader(csvfile)
		lines = list(reader)
		for i in range(-1,-1 - max(5, len(lines)),-1):
			if len(lines[i]) != 0:
				last_line = lines[i]
				break
	return datetime.strptime(last_line[0], '%Y%m%d').date()
			
def load_hk_stock_full_list(filename):
	dict = {}
	with open(filename, encoding='utf-8') as csvfile:
		reader = csv.reader(csvfile)
		for i in range(3):
			next(reader)
		for row in reader:
			key = row[0]
			name = row[1]
			type = row[2]
			if type in ['股本', '交易所買賣產品', '房地產投資信託基金', ]:
				dict[key] = name
	return dict
			
if __name__ == '__main__':
#	max_year, max_season, min_year, min_season = get_HK_stock_history_range('01088')
#	print(max_year, max_season, min_year, min_season)
#	for line in get_HK_stock_history('00386', 2000, 3):
#		print(line)

#	code = '00386'
#	history = get_HK_stock_whole_history(code)
#	save_to_file(code, history)

#	hk_stock = load_hk_stock_full_list('list.hk.csv')
#	total = len(hk_stock)
#	done = 0
#	for code in hk_stock:
#		if os.path.exists(history_data_filename(code)):
#			done += 1
#			print('History data for', code, hk_stock[code], 'already exist. [%d/%d] Done.' % (done, total))
#		else:
#			data = get_HK_stock_whole_history(code)
#			if data is None:
#				continue
#			save_to_file(code, data)
#			done += 1
#			print('Got history data for', code, hk_stock[code], '[%d/%d] Done.' % (done, total))

	print(get_latest_date_from_file('00038'))
