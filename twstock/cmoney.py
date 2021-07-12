# -*- coding: utf-8 -*-
import requests, os, re, datetime, json
import ujson
from attrdict import AttrDict
###########################################################
# Private Function
###########################################################
def json_save(filename, data):
    '''
    :param filename: json filename
    :param data: the dictionary that store date
    :return: None
    '''
    with open(filename, 'w') as fjson:
        json.dump(data, fjson, ensure_ascii=False, sort_keys=True, indent=4)

def json_load(filename):
    '''
    :param filename: the json filename
    :return: the dictionary that store date
    '''
    if not os.path.exists(filename):
        return None
    with open(filename) as f:
        d = ujson.decode(f.read())
    return _make_attrdict(d)

def _make_attrdict(d):
    return {k:AttrDict(v) for k, v in d.items()}

def get_stock_ck():

    # Browse the webpage once to get the CK value
    url = 'http://www.cmoney.tw/notice/chart/stockchart.aspx?action=r&id=1101&date=20171010'

    # Real get
    session = requests.Session()
    res = session.get(url)

    # Get the content
    content = res.text

    # Parse ck from content
    for line in content.split('\n'):
        m = re.match('\s*?var\s*ck\s*=\s*"(.*?)";', line)
        if m:
            ck = m.group(1)

    return ck, session
        
def get_finance(sid):

    today = datetime.datetime.today().date()
    year, month, day = today.year, today.month, today.day
    today_date = '%d%0.2d%0.2d' % (year, month, day)
    
    json_file = os.path.join('.cache', '%s.json' % sid)

    if not os.path.exists('.cache'):
        os.mkdir('.cache')

    if os.path.exists(json_file):
        d = json_load(json_file)
        if list(d.keys())[-1] == today_date:
            return _make_attrdict(d)
    
    d = {}

    ck, session = get_stock_ck()
    h = {
        'Cookie': 'AspSession='+session.cookies['AspSession']+'; __asc=f192f05015e1a2dd01ff253ba0a; __auc=f192f05015e1a2dd01ff253ba0a; _gat_real=1; _gat_UA-30929682-4=1; _ga=GA1.2.1793962014.1465548991; _gid=GA1.2.2115739754.1503677764; _gat_UA-30929682-1=1',
        'Host': 'www.cmoney.tw',
        'Referer': 'https://www.cmoney.tw/notice/chart/stockchart.aspx?action=d&id=TWA00&scaleSize=1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    data = {
        'action': 'd',
        'count': '1000',
        'id': sid,
        'ck': ck,
        '_': '1533974045257'
    }
    res = session.get('https://www.cmoney.tw/notice/chart/stock-chart-service.ashx', headers=h, params=data)
    
    for element in res.json()['DataLine']:
        date, open_price, high_price, low_price, close_price, capacity, diff, rate, tmp2, money = element
        date_string = datetime.datetime.fromtimestamp(date/1000.0).strftime('%Y%m%d')
        if date_string not in d:
            d[date_string] = {
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'capacity': capacity,
                'diff': diff,
                'rate': rate,
                'money': money * 1000
            }

    json_save(json_file, d)
    return _make_attrdict(d)

if __name__ == '__main__':
    print(get_finance('5285'))
