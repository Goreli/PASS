'''
Created on 14 May 2018

@author: David
'''
import requests
from copy import deepcopy


class ListPages:
    def __init__(self, url, plpfunc):
        self.next_url = url
        self._parse_list_page = plpfunc
        self.html = None
        ''' HTML code resulted from the most recent GET request.'''
        self.curr_url = None
        ''' URL used by the most recent successful GET request.'''
        self._urls = []
        ''' The list of the detail page URL's parsed out of the html code.'''
        self.exception = None
        ''' Exception, if any. To check if there was an error and re-throw it if required.'''

    def __iter__(self):
        return self

    def __next__(self):
        if(not self.next_url):
            raise StopIteration()

        try:
            self.html = requests.get(self.next_url).text
        except Exception as e:
            self.exception = e
            raise StopIteration()
        else:
            self.curr_url = self.next_url
            self._urls, self.next_url = self._parse_list_page(self.html)

        return self

    @property
    def urls(self):
        return deepcopy(self._urls)
