''' pass - Police Auctions Synchronous Scraper
Created on 14 May 2018

@author: David
'''
import logging
import sys
import os
import datetime
from dateutil import tz

from pasite import PASite
from profiler import Profiler
from mongodbadapter import MongodbAdapter
from syncscraper import scrape_site


def create_logger():
    logger_name = os.path.basename(sys.argv[0]).split('.')[0]
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logfilehandler = logging.RotatingFileHandler(
        f'.\\{logger_name}.log', maxBytes=1000000, backupCount=2)
    logger.addHandler(logfilehandler)
    return logger


def log_timestamped_msg(logger, msg):
    dtstamp = datetime.datetime.now().__str__().split('.')[0]
    logger.info(f'{dtstamp} - {msg}')
    logger.info('')


def log_utciso_msg(logger, msg):
    review_utc_dt = datetime.datetime.utcnow().replace(tzinfo=tz.tzutc())
    review_loc_dt = review_utc_dt.astimezone(tz.tzlocal())

    review_utc_dt_str = review_utc_dt.isoformat().split('.')[0]
    review_loc_dt_str = review_loc_dt.isoformat().split('.')[0]

    logger.info(msg)
    logger.info(f'    UTC   - {review_utc_dt_str}')
    logger.info(f'    Local - {review_loc_dt_str}')

    return review_utc_dt_str


if __name__ == '__main__':
    logger = create_logger()
    site = PASite()
    log_timestamped_msg(
        logger, f'started scraping data from {site.get_site_url()}')

    categories = site.get_categories()
    ''' Start looping over the categories here... 
    We will use the categories once the storage has been implemented.
    For now we will use a single category "sets".
    '''
    categories = ['sets']

    for category in categories:
        logger.info(f'Started processing category "{category}"')
        profiler = Profiler()
        strgcurr = MongodbAdapter(
            'mongodb://localhost:27017', 'JewelryAuctionsCurrent', f'PA_{category}', logger)
        list_page_count = scrape_site(
            site, category, logger, strgcurr, profiler)
        logger.info(f'Profiling results for category "{category}":')
        profiler.print(logger=logger)
        logger.info(
            f'{list_page_count:>4} list page(s) have been processed for category "{category}".')

    log_timestamped_msg(logger, 'ended scraping the data.')
    logger.info(
        'Started moving completed auction records from the current to completed storage.')

    review_utc_dt_str = log_utciso_msg(
        logger, 'Date/time value used to review the auction completion status:')
    for category in categories:
        logger.info(f'Started processing category "{category}"')
        strgcurr = MongodbAdapter(
            'mongodb://localhost:27017', 'JewelryAuctionsCurrent', f'PA_{category}', logger)
        strgcomp = MongodbAdapter(
            'mongodb://localhost:27017', 'JewelryAuctionsCompleted', f'PA_{category}', logger)
        filter = {'document.auction.end_utc_dt': {'$lt': review_utc_dt_str}}
        batch_size = 100
        strgcurr.move_documents(strgcomp, filter, batch_size)

    log_timestamped_msg(logger, 'ended moving completed auction records.')
