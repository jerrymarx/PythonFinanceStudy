# original source from http://quote.eastmoney.com/hk/ahlist.html, copy the content and save it as 'ah.txt'
infile = open('ah.txt', 'rb')
lines = [line.strip().decode('utf-8') for line in infile.readlines()]
infile.close()
outputs = list()
i = 0
black_list = ['00300', '00350']
while i < len(lines):
	number, name, code_h = lines[i].split('\t')
	code_a = lines[i+3]
	if code_h not in black_list:
		outputs.append('%s,%s,%s' % (code_h, code_a, name))
	i = i + 7
with open('ah.csv', 'w') as outfile:
	outfile.write('\n'.join(outputs))
