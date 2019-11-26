'''
Created on 4 May 2018

Captures the following information:
    Auction Id:
        It's a number but we'll capture it as a string.
        It's gone up to 7 digits by now.
    Bid History (multiple records):
        User Id, amount, ccy
    Auction end date/time:
        Datetime
    Product description string:
        String
    Gemstone Description (multiple records):
        Gemstone: Diamond
        Quantity: 12
        Color: J - Near Colorless
        Clarity: I3
        CTW: 0.050 CTW
        Cut: Round Cut    
    Material Information:
        Plating Material: Yellow Gold
        Plating Material Karat: 14 k
        Primary Material: Brass
        Primary Material Weight: 9.20 g
        Primary Material Karat: 0.00 k
        Secondary Material: Yellow Gold
        Secondary Material Weight: 0.00 g
        Secondary Material Karat: 14.00 k
    Jewelry Information:
        Mount Type: Sets
        Gender: Womens
        Overall Weight: 9.20 g

DATETIME to be represented using the ISO8601 standard with the time zone always set to UTC.
>>> print(datetime.datetime.utcnow().isoformat())
2018-05-05T05:58:52.429598
The fraction part is optional in ISO, so we will drop it as it's not required for the application.

All database column values are to be supplied by this module using the string data type. 
The conversion to the ultimate database level type to be facilitated by the database adapter.

@author: David
'''


from bs4 import BeautifulSoup
import re
import datetime
import pytz
from collections import OrderedDict
import copy


class PASite():
    _site_url = 'https://www.policeauctions.com'
    # _prod_page_url_template = '/category/{}?sort=date&order=asc'
    _prod_page_url_template = '/category/{}?sort=date&order=desc'
    _categories = ['bracelet', 'brooch', 'earrings',
                   'necklace', 'ring', 'sets', 'watches']

    @classmethod
    def get_site_url(cls):
        return cls._site_url

    @classmethod
    def get_starting_url(cls, category):
        return cls._site_url + cls._prod_page_url_template.format(category)

    @classmethod
    def get_categories(cls):
        return copy.deepcopy(cls._categories)

    @classmethod
    def parse_list_page(cls, summary_page_html):
        ''' Parses the list page html and returns the
        the (detail_url_list, next_page_url) pair where
        - detail_url_list contains a list of detail page url's.
            If no detail page url's found then the list returned
            will have zero length;
        - next_page_url contains a url of the next summary page.
            If there is no such url then the None value is returned.
        '''
        soup = BeautifulSoup(summary_page_html, 'lxml')
        # Put together a list of urls pointing to detail pages.
        detail_url_list = []
        for product_element in soup.find_all('div', class_='product-image-cell'):
            detail_url = cls._site_url + product_element.a.get('href')
            detail_url_list.append(detail_url)
        # Get the url for the next summary page.
        next_page_url = None
        next_button_anchor = soup.find('a', rel='next')
        if next_button_anchor:
            next_page_url = next_button_anchor.get('href')

        return detail_url_list, next_page_url

    @staticmethod
    def parse_detail_page(detail_page_html):
        soup = BeautifulSoup(detail_page_html, 'lxml')

#         auction_rec = _build_auction_table_record(soup)
#         auction = []
#         auction.append(auction_rec)
#
#         tables = OrderedDict()
#         tables['auction'] = auction

        tables = OrderedDict()
        tables['auction'] = _build_auction_table_record(soup)

        div_container = soup.find('div', class_='panel-body')
        for ultag in div_container.find_all('ul'):
            table_nm = _identify_other_table_name(ultag)
            if not table_nm:
                break
            if not (table_nm in tables):
                tables[table_nm] = []

            litags = ultag.find_all('li')
            other_rec = _build_other_table_record(litags)
            tables[table_nm].append(other_rec)

        return tables


def _identify_other_table_name(ultag):
    ''' Go back to find the preceding "strong" tag.
    If the second word is Description or Information
    then use the first word (lower case). Otherwise
    use the entire content of the tag (lower case
    with _ replacing white space).
    If the tag is not found then return None.
    '''
    table_nm = None
    prevsib = ultag.previous_sibling
    while prevsib:
        if prevsib.name and prevsib.name == 'strong':
            wordlist = prevsib.text.split()
            if wordlist[1] in set(('Description', 'Information')):
                table_nm = wordlist[0].lower()
            else:
                table_nm = prevsib.text.lower().replace(' ', '_').replace('\t', '_')
            break
        prevsib = prevsib.previous_sibling

    return table_nm


def _build_other_table_record(litags):
    tbl_rec = OrderedDict()
    for litag in litags:
        coldata = litag.text.split(':')
        colkey = coldata[0].lower().replace(' ', '_').replace('\t', '_')
        colval = coldata[1].strip()
        tbl_rec[colkey] = colval
        # Split the column value into two columns if this is
        # a numeric value along with its measurement unit.
        if colkey.endswith('karat') or colkey.endswith('weight') or colkey == 'ctw':
            colval = colval.split()
            num = colval[0]
            unit = colval[1]
            tbl_rec[colkey] = num
            tbl_rec[colkey + '_unit'] = unit

    return tbl_rec


def _build_auction_table_record(soup):
    # Get Auction Id
    auction_id_span = soup.find('span', class_='pull-right',
                                string=re.compile(r'Auction\sID:\s\d+'))
    # <span class="pull-right">Auction ID: 2229706</span>
    auction_id = auction_id_span.string.split()[-1]

    # Get Auction End date/time
    end_dt_strong = soup.find(
        'strong', string=re.compile(r'This\sAuction\sEnds:\s'))
    end_origtz = end_dt_strong.string.split(' ', 4)[-1]
    end_utc_dt = _parse_auction_end_date(end_origtz)

    # Get the product description
    product_dsc = soup.find('meta', property='og:description')['content']

    auction_rec = OrderedDict()
    auction_rec['auction_id'] = auction_id
    auction_rec['product_dsc'] = product_dsc
    auction_rec['end_utc_dt'] = end_utc_dt
    auction_rec['end_origtz'] = end_origtz

    return auction_rec


def _parse_auction_end_date(origtz_end):
    # 'May 4th 2018 10:21:20 PM PDT'
    end_dt_split = origtz_end.split()
    day = re.compile(r'\d+').match(end_dt_split[1])[0]
    day_dd = f'{int(day):02}'
    month_Mmm = end_dt_split[0]
    origtz_end_dt = f"{day_dd} {month_Mmm} {' '.join(end_dt_split[2:])}"
    # '04 May 2018 10:21:20 PM PDT'
    origtz_end_dt = origtz_end_dt.replace('PDT', '-0700')
    origtz_end_dt = origtz_end_dt.replace('PST', '-0800')
    origtz_end_dt = datetime.datetime.strptime(
        origtz_end_dt, '%d %b %Y %I:%M:%S %p %z')
    # Convert to the UTC timezone.
    utc_dt = origtz_end_dt.astimezone(pytz.utc)

    # Get a string representation of the date in the ISO format
    # and remove the microseconds at the end.
#     utc_end_dt = utc_end_dt.isoformat().split('+')[0].split('-')[0]
    truncated_utc_dt = datetime.datetime(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second)
    truncated_utc_dt = truncated_utc_dt.isoformat()
    return truncated_utc_dt
