from urllib2 import urlopen
from bs4 import BeautifulSoup as soup
import re, datetime, csv, time, random

class divend_info:
	def __init__(self, full_list_filename, ah_list_filename, divend_filename):
		self.full_dict = self.load_full_list(full_list_filename)
		self.ah_dict = self.load_ah_list(ah_list_filename)
		self.divend_data = self.load_divend_data(divend_filename)
		self.usd = None
		self.hkd = None
		
	def load_full_list(self, filename):
		full_dict = {}
		with open(filename) as csvfile:
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

	def get_last_price(self, code):
		if len(code) == 5:
			code = 'hk' + code
			the_url = 'http://hq.sinajs.cn/format=text&list=' + code
			client = urlopen(the_url)
			print 'try to get', the_url
			text = client.read()
			client.close()
			parts = text.split(',')
			name = parts[1]
			price_str = parts[6]
			return float(price_str), name
			
		else:
			if code[0] == '0' or code[0] == '2' or code[0] == '3':
				code = 'sz' + code
			elif code[0] == '6' or code[0] == '9':
				code = 'sh' + code
			else:
				print 'Unkonw code:', code
				return None
			
			the_url = 'http://hq.sinajs.cn/format=text&list=s_' + code
			client = urlopen(the_url)
			print 'try to get', the_url
			text = client.read()
			client.close()
			
			code_name, price_str, delta, delta_percent, volume, turnover = text.split(',')
			if price_str == '0.00':
				the_url = 'http://hq.sinajs.cn/format=text&list=' + code
				client = urlopen(the_url)
				print 'try to get', the_url
				text = client.read()
				client.close()
				price_str = text.split(',')[2]
				
			scode, name = code_name.split('=')
			if scode[-8:] != code:
				print 'Some thing error, request', code, ', but return', scode
			price = float(price_str)
			
			return price, name

	def format_row(self, code, price, name):
		items = ['="' + code + '"', str(price),]
		key = self.ah_dict[code]['code_a'] if len(code) == 5 else code
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
		for year in range(2017, 1990, -1):
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
		lines = text.split('\n')
		self.usd = float(lines[0].split(',')[2])
		self.hkd = float(lines[1].split(',')[2])

	def get_data_from_sina_then_write(self, code):
		price, name = self.get_last_price(code)
		text = self.format_row(code, price, name)
		with open('output.csv', 'a') as ofile:
			ofile.write(text)
			ofile.write('\n')
		
	def main(self):
		self.get_usd_hkd()
		with open('output.csv', 'w') as ofile:
			heads = ['CODE', 'PRICE', 'TOTAL', 'MARKET']
			for year in range(2017, 1990, -1):
				heads.append(str(year))
				heads.append(str(year)+'p')
			ofile.write(','.join(heads))
			ofile.write('\n')
		total = len(self.full_dict) + len(self.ah_dict)
		done = 0
		for key in self.full_dict:
			self.get_data_from_sina_then_write(key)
			done += 1
			print 'Get info of %s done. [%d/%d]' % (key, done, total)
		for key in self.ah_dict:
			self.get_data_from_sina_then_write(key)
			done += 1
			print 'Get info of %s done. [%d/%d]' % (key, done, total)


if __name__ == '__main__':
	worker = divend_info('full_list.csv', 'ah.csv', 'divend.csv');
	'''code = '600028'
	price, name = worker.get_last_price(code)
	text = worker.format_row(code, price, name)
	print text'''
	worker.main()
	