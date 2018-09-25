try:
	from urllib.request import urlopen
except:
	from urllib2 import urlopen
from bs4 import BeautifulSoup as soup
import re, datetime, csv, time, random

class divend_info:
	def __init__(self, full_list_filename, ah_list_filename, divend_filename):
		self.full_dict = self.load_full_list(full_list_filename)
		self.ah_dict = self.load_ah_list(ah_list_filename)
		self.divend_data = self.load_divend_data(divend_filename)
		self.price_dict = {}
		self.usd = None
		self.hkd = None
		
	def load_full_list(self, filename):
		full_dict = {}
		with open(filename, encoding='UTF-8') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				key = row[0]
				code_a = row[1]
				code_b = row[3]
				total_a = row[5]
				total_b = row[6]
				full_dict[key] = {'code_a':code_a, 'code_b':code_b, 'total_a':float(total_a), 'total_b':float(total_b)}
		return full_dict

	def load_ah_list(self, filename):
		ah_dict = {}
		with open(filename) as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				code_h = row[0]
				code_a = row[1]
				name_h = row[2]
				ah_dict[code_h] = {'code_a':code_a, 'name_h':name_h}
		return ah_dict
		
	def load_divend_data(self, filename):
		divend_data = {}
		with open(filename) as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				code = row[0]
				volume = float(row[1])
				rate = float(row[2])
				year = int(row[3])
				
				if code not in divend_data:
					divend_data[code] = {}
				record = divend_data[code]
				if year not in record:
					record[year] = 0.0
				record[year] += volume * rate / 10
		return divend_data

	def get_code_str_for_sina_hq(self, code, prefix=''):
		if len(code) == 5:
			return 'hk' + code
		if code[0] == '0' or code[0] == '2' or code[0] == '3':
			return prefix + 'sz' + code
		elif code[0] == '6' or code[0] == '9':
			return prefix + 'sh' + code
		else:
			print('Unknow code:', code)
			return None
		
	def get_latest_price_from_sina(self):
		total = len(self.full_dict) + len(self.ah_dict)
		group_size = 50
		done = 0
		
		key_list = list(self.full_dict.keys())
		for i in range(0, len(self.full_dict), group_size):
			temp_list = key_list[i:i+group_size]
			code_list = [self.get_code_str_for_sina_hq(code, 's_') for code in temp_list]
			
			the_url = 'http://hq.sinajs.cn/format=text&list=' + ','.join(code_list)
			client = urlopen(the_url)
			print('try to get', the_url)
			text = client.read()
			client.close()
			
			lines = text.decode('gbk').split('\n')
			for line in lines:
				if line.strip() == '':
					continue
				parts = line.split(',')
				code, name = parts[0].split('=')
				price_str = parts[1]
				
				if price_str == '0.00':
					the_url = 'http://hq.sinajs.cn/format=text&list=' + code[-8:]
					client = urlopen(the_url)
					print('try to get', the_url)
					text = client.read()
					client.close()
					price_str = text.decode('gbk').split(',')[2]
					name = name + ' S'
				
				self.price_dict[code[-6:]] = [name, float(price_str),]
				done += 1
			print('Get info of [%d/%d] done.' % (done, total))
				
		key_list = list(self.ah_dict.keys())
		for i in range(0, len(self.ah_dict), group_size):
			temp_list = key_list[i:i+group_size]
			code_list = [self.get_code_str_for_sina_hq(code) for code in temp_list]
			
			the_url = 'http://hq.sinajs.cn/format=text&list=' + ','.join(code_list)
			client = urlopen(the_url)
			print('try to get', the_url)
			text = client.read()
			client.close()
			
			lines = text.decode('gbk').split('\n')
			for line in lines:
				if line.strip() == '':
					continue
				parts = line.split(',')
				code = parts[0].split('=')[0][-5:]
				name = parts[1]
				price_str = parts[6]
				self.price_dict[code] = [name, float(price_str),]
				done += 1
			print('Get info of [%d/%d] done.' % (done, total))
		
	def get_last_price(self, code):
		if code in self.price_dict:
			info = self.price_dict[code]
			return info[1], info[0]
		else:
			print('Cannot find price and name for code:', code)
			return None, None

	def format_row(self, code, price, name):
		items = ['="' + code + '"', name, str(price),]
		key = code
		if len(code) == 5:
			key = self.ah_dict[code]['code_a']
		elif self.full_dict[code]['code_a'] != '':
			key = self.full_dict[code]['code_a']
		common_info = self.full_dict[key]
		total = common_info['total_a'] + common_info['total_b']
		total_value = total * price
		if code[0] == '9':
			total_value *= self.usd
		elif code[0] == '2' or len(code) == 5:
			total_value *= self.hkd
		items.append('%.4f' % total)
		items.append('%.4f' % total_value)
		
		divend_info = self.divend_data[key] if key in self.divend_data else {}
		for year in range(2018, 1990, -1):
			divend = ('%.4f' % divend_info[year]) if year in divend_info else ''
			percent = (('%.2f%%' % (divend_info[year]*100/total_value)) if year in divend_info else '') if total_value > 1 else ''
			items.append(divend)
			items.append(percent)
		return ','.join(items)

	def get_usd_hkd(self):
		the_url = 'http://hq.sinajs.cn/format=text&list=USDCNY,HKDCNY'
		client = urlopen(the_url)
		text = client.read()
		client.close()
		lines = text.decode('gbk').split('\n')
		self.usd = float(lines[0].split(',')[2])
		self.hkd = float(lines[1].split(',')[2])

	def get_data_from_sina_then_write(self, code, outfile):
		price, name = self.get_last_price(code)
		text = self.format_row(code, price, name)
		with open(outfile, 'a', encoding='utf-8-sig') as ofile:
			ofile.write(text)
			ofile.write('\n')
		
	def main(self):
		self.get_usd_hkd()
		outfile = 'output_' + datetime.datetime.now().strftime("%Y%m%d") + '.csv'
		with open(outfile, 'w',encoding='utf-8-sig') as ofile:
			heads = ['CODE', 'NAME', 'PRICE', 'TOTAL', 'MARKET']
			for year in range(2018, 1990, -1):
				heads.append(str(year))
				heads.append(str(year)+'p')
			ofile.write(','.join(heads))
			ofile.write('\n')
		self.get_latest_price_from_sina()
		done = 0
		print('Handle the data', end='', flush=True)
		for key in self.full_dict:
			self.get_data_from_sina_then_write(key, outfile)
			done += 1
			if done % 100 == 0:
				print('.', end='', flush=True)
				
		for key in self.ah_dict:
			self.get_data_from_sina_then_write(key, outfile)
			done += 1
			if done % 100 == 0:
				print('.', end='', flush=True)

		print(' Done')

if __name__ == '__main__':
	worker = divend_info('full_list.csv', 'ah.csv', 'divend.csv');
	'''code = '600028'
	price, name = worker.get_last_price(code)
	text = worker.format_row(code, price, name)
	print text'''
	worker.main()
	