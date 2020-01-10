import time, requests, argparse
from bs4 import BeautifulSoup
import pandas as pd

'''
Example command: python quote_getter.py TSLA
It will create an Excel file with data of next 6 weeks
'''

def get_next_six_timestamp(base = 1578614400):      # 1/10/2020, 7:00:00 AM
    interval = 604800                               # time interval between two quote dates
    current_time = int(time.time())
    while base < current_time:
        base += interval
    return [str(base + i * interval) for i in range(0, 6)]

def _unpack(row, kind):
    elts = row.xpath(kind)
    return [val.text_content() for val in elts]
    
def quote_puts_parser(ticker, dates):
    gen_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    writer = pd.ExcelWriter('tmp/' + ticker + gen_time + '.xlsx', engine='xlsxwriter')
    for i, date in enumerate(dates):
        url = "https://finance.yahoo.com/quote/%s/options?date="%(ticker) + str(date)
        print(url)
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find_all('table')[1]
        df = pd.read_html(str(table))[0]
        df.to_excel(writer, sheet_name = 'Sheet' + time.strftime("%Y%m%d", time.gmtime(int(date))))
    writer.save()
    print('Finished!')
    
if __name__=="__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('ticker',help = '')
    args = argparser.parse_args()
    ticker = args.ticker
    print ("Fetching data for %s"%(ticker))
    quote_puts_parser(ticker,get_next_six_timestamp())