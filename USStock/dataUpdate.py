# Python 2.7.11
from bs4 import BeautifulSoup as soup
import csv, urllib, datetime, time, random

nasdaqurl = 'https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download'
nyseurl = 'https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download'

def sort_list(file):
    with open(file, 'r+') as f:
        headers = f.readline()
        firstData = f.readline()
        f.seek(0)
        firstData = firstData[:-1] + ' ' * (len(headers) + 1)
        f.write(firstData)

    reader = csv.reader(open(file))
    sortedlist = sorted(reader, key=lambda row: row[0], reverse=False)

    sorted_file = f.name[:-4] + '_sorted.csv'
    sorted_file_path = open(sorted_file, "wb")
    writer = csv.writer(sorted_file_path)
    # writer.writerow(['Symbol','Name','LastSale','MarketCap','IPOyear','Sector','industry','Summary Quote'])
    for stock in sortedlist:
        writer.writerow(stock)
    sorted_file_path.close()
    print f.name[:-4] + ' sorted list is updated'

def update_list(category):
    if category == 'NASDAQ':
        print('Beginning file download with NASDAQ...')
        urllib.urlretrieve(nasdaqurl, 'NASDAQ.csv')
        sort_list('NASDAQ.csv')
    elif category == 'NYSE':
        print('Beginning file download with NYSE...')
        urllib.urlretrieve(nyseurl, 'NYSE.csv')
        sort_list('NYSE.csv')


def get_page_soup(the_url):
    print 'try to get data from:', the_url
    client = urllib.urlopen(the_url)
    page_html = client.read()
    client.close()

    page_soup = soup(page_html, 'html.parser')
    return page_soup

def update_div_history(file):
    outfile = open(file[:-10] + 'dividend_' + datetime.datetime.now().strftime("%Y%m%d") + '.csv', "wb")
    with open(file, 'r+') as f:
        count = 0
        for line in f:
            count = count + 1
            value = line.split(',')
            code = value[0]
            the_url = 'https://dividendhistory.org/payout/' + code + '/'
            page_soup = get_page_soup(the_url)
            dividend_table = page_soup.find('table', {'id' : "dividend_table"})
            try:
                data_body = dividend_table.find_all('tbody')[0]
                data = list()
                orig = list()
                for row in data_body.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) == 1:
                        continue
                    pay_date_str = cols[1].text.strip()
                    register_date_str = cols[0].text.strip()
                    divend_str = cols[2].text.strip()
                    # data.append({'payout': convert_date(pay_date_str),
                    #              'register': convert_date(
                    #                  register_date_str) if register_date_str != '--' else convert_date(
                    #                  public_date_str),
                    #              'divend': float(divend_str)})
                    # orig.append(cols)
                    print('Payout Date:' + pay_date_str + '\tRegister Date:' + register_date_str + '\tDivend per 10 shares:' + divend_str)
                    outfile.write(code + ',' + pay_date_str + ',' + register_date_str + ',' + divend_str + '\n')
            except:
                print('No dividend info for ' + code)
                pass
            time.sleep(random.randint(1, 5))
            #if count > 5:
            #    break
    outfile.close()

    # data = list()
    # orig = list()
    # for row in data_body.find_all('tr'):
    #     cols = row.find_all('td')
    #     if len(cols) == 1:
    #         continue
    #     pay_date_str = cols[1].text.strip()
    #     register_date_str = cols[0].text.strip()
    #     divend_str = cols[3].text.strip()
    #     data.append({'payout': convert_date(pay_date_str),
    #                  'register': convert_date(register_date_str) if register_date_str != '--' else convert_date(
    #                      public_date_str),
    #                  'divend': float(divend_str)})
    #     orig.append(cols)
    # print 'Public Date:', public_date.text.strip(), '\tRigester Date:', register_date.text.strip(), '\tDivend per 10 shares:', divend.text.strip()
    # return data, orig

if __name__ == '__main__':
    update_list('NASDAQ')
    update_list('NYSE')
    update_div_history('NASDAQ_sorted.csv')
    update_div_history('NYSE_sorted.csv')