from urllib.request import urlopen
from threading import Timer
import re, urllib, time, datetime, calendar, random, csv, os
from hk_history_sina_getter import load_hk_stock_full_list

crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
cookie_regex = r'set-cookie: (.*?); '

def refine_code(code):
	if code[0] == '0':
		return code[-4:] + '.HK'
	else:
		return code + '.HK'

def get_crumble_and_cookie(code):
	the_url = 'https://finance.yahoo.com/quote/' + refine_code(code) + '/history'
	crumble_str, cookie_str = None, None
	for i in range(10):
		client = None
		try:
			print('Try get cookie and scrumb', the_url)
			client = urlopen(the_url, timeout=10)
			t = Timer(10, close_connection, [client, ])
			t.start()
			
			info_str = str(client.info())
			match = re.search(cookie_regex, info_str)
			cookie_str = match.group(1)
			
			content_str = str(client.read())
			match = re.search(crumble_regex, content_str)
			crumble_str = match.group(1)

			print('Scrumb:', scrumb, 'Cookie:', cookie)
			t.cancel()
			client.close()
			break
		except:
			if client:
				client.close()
	return crumble_str, cookie_str

def close_connection(client):
	client.close()

def get_history_csv_from_yahoo(code, scrumb, cookie):
	now_gm_timestamp = calendar.timegm(datetime.datetime.now().timetuple())
	the_url = 'https://query1.finance.yahoo.com/v7/finance/download/' + refine_code(code) + '?period1=0&period2=' + str(now_gm_timestamp) + '&interval=1d&events=history&crumb=' + scrumb
	print('Try to get csv from', the_url, end=' ', flush=True)
	req = urllib.request.Request(the_url, headers={'Cookie': cookie})
	content = None
	for i in range(5):
		client = None
		try:
			print('>', end='', flush=True)
			client = urlopen(req, timeout=10)
			t = Timer(10, close_connection, [client, ])
			t.start()
			print('.', end='', flush=True)
			content = client.read();
			t.cancel()
			client.close()
			break
		except:
			if client:
				client.close()
	print('Done' if content else 'Failed')
	return content
	
def history_data_filename(code):
	return os.path.join('yahoo', code + '.HK.csv')

def save_to_file(code, content):
	with open(history_data_filename(code), 'wb') as outfile:
		outfile.write(content)
	
if __name__ == '__main__':
	hk_stock = load_hk_stock_full_list('list.hk.csv')
	total = len(hk_stock)
	done = 0
	scrumb, cookie = None, None
	for code in hk_stock:
		if os.path.exists(history_data_filename(code)):
			done += 1
			print('History data for', code, hk_stock[code], 'already exist. [%d/%d] Done.' % (done, total))
		else:
			if scrumb == None:
				scrumb, cookie = get_crumble_and_cookie(code)
			data = get_history_csv_from_yahoo(code, scrumb, cookie)
			if data is None:
				print('Failed to get history data for', code, hk_stock[code])
				continue
			save_to_file(code, data)
			done += 1
			print('Got history data for', code, hk_stock[code], '[%d/%d] Done.' % (done, total))
