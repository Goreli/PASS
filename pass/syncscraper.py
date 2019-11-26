''' pass - Police Auctions Synchronous Scraper
Created on 14 May 2018

@author: David
'''
import datetime
import json
import logging
from collections import OrderedDict

from listpages import ListPages
from detailpages import DetailPages


def buildmetadoc(detailpage, category):
    parsed_utc_dt = datetime.datetime.utcnow().isoformat()
    ''' Get the UTC time when the information was parsed. '''
    parsed_utc_dt = parsed_utc_dt.split('.')[0]
    ''' Remove the microseconds part. '''

    metadoc = OrderedDict()
    metadoc['category'] = category
    metadoc['url'] = detailpage.curr_url
    metadoc['parsed_utc_dt'] = parsed_utc_dt
    metadoc['document'] = detailpage.doc
    return metadoc


def log_exception(logger, location, ex):
    logger.error(f'Problem with "{location}" in module {__name__}.')
    logger.error('Caught the following exception:')
    logger.error(ex)


def scrape_pages(detailpages, category, logger, storage, profiler):
    detail_page_count = 0
    for detailpage in detailpages:
        if (profiler):
            profiler.update(detailpage.doc)
        metadoc = buildmetadoc(detailpage, category)
        if (logger and logger.getEffectiveLevel() < logging.INFO):
            pretty_json = json.dumps(metadoc, indent=2)
            logger.debug(pretty_json)
        storage.insert_one(metadoc)
        ''' Apparently Mongodb does something to the metadoc object
        so that it becomes unusable as far as json.dumps is concerned.
        json.dumps just spits the dummy with:
            TypeError: ObjectId('') is not JSON serializable
        So make sure storage.store is the last call using metadoc
        or consider using a deep copy of metadoc.
        '''
        detail_page_count += 1

    if(logger and detailpages.exceptions):
        log_exception(logger, 'next detailpage', json.dumps(
            detailpages.exceptions, indent=2))

    return detail_page_count


def scrape_site(site, category, logger, storage, profiler):
    first_url = site.get_starting_url(category)
    listpages = ListPages(first_url, site.parse_list_page)

    list_page_count = 0
    for listpage in listpages:
        urls = listpage.urls
        logger.info(
            f"{len(urls):>4} detail page URL(s) found on the list page {listpage.curr_url}")
        urls = storage.filter_urls(urls)
        logger.info(
            f"{len(urls):>4} URL(s) remaining to be scraped after filtering the existing ones out...")

        detailpages = DetailPages(urls, site.parse_detail_page)
        detail_page_count = scrape_pages(
            detailpages, category, logger, storage, profiler)
        logger.info(
            f"{detail_page_count:>4} detail page document(s) have been submitted into the storage.")
        list_page_count += 1

    if(listpages.exception):
        log_exception(logger, 'next listpage', listpages.exception)

    return list_page_count
