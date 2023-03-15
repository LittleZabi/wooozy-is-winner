from printy import printy
import requests
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher

def _filter(__str__):
    __str__ = re.sub(' +', ' ', __str__)
    __str__ = __str__.replace('\n', '')
    __str__ = __str__.replace('\r', '')
    __str__ = __str__.strip()
    return __str__

def log(__str__, __type__='success'):
    colors = ['[c]', '[o>]', '[r>]', '[c>]']
    print(end='\n')
    c = colors[0]
    if __type__ == 'highlight':
        c = colors[3]
    if __type__ == 'alert':
        c = colors[1]
    if __type__ == 'error':
        c = colors[2]
    printy(f"{c}{__str__}", end='')


def __request__(url):
    log('Sending Request to website...', 'success')
    # html = open('./horses.html', 'r', encoding='utf-8')
    # return html
    page = requests.get(url)
    return (page.text).encode('utf-8')

def compareTimes(time1, time2):
    if time1 == time2:
        return True
    try:
        half_day = timedelta(hours=12)
        datetime1 = datetime.strptime(time1, '%H:%M')
        datetime2 = datetime.strptime(time2, '%H:%M')
        if datetime1 == datetime2:
            return True
        datetime1_halfday = datetime1 + half_day
        if datetime1_halfday == datetime2:
            return True
        else:
            return False
    except Exception as e:
        log(f"compareTimes -> failed: {e}", 'error')

def stringMatchingPercent(str1, str2):
    str1 = str1.replace(' ', '')
    str2 = str2.replace(' ', '')
    similarity_ratio = SequenceMatcher(None, str1, str2).ratio()
    percent_similarity = round(similarity_ratio * 100, 2)
    return percent_similarity