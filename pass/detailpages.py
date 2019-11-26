'''
Created on 17 May 2018

@author: David
'''
import requests


class DetailPages:
    def __init__(self, urls, pdpfunc):
        self.urls = urls
        self._parse_detail_page = pdpfunc

        self.html = None
        ''' HTML code resulted from the most recent GET request.'''
        self.urlinx = None
        self.next_url = None
        self.curr_url = None
        self.exceptions = None
        self.doc = None

    def __iter__(self):
        self.urlinx = 0
        return self

    def __next__(self):
        try:
            self.next_url = self.urls[self.urlinx]
        except:
            raise StopIteration()

        try:
            self.html = requests.get(self.next_url).text
        except Exception as e:
            if (not self.exceptions):
                self.exceptions = []
            self.exceptions.append({'url': self.next_url, 'exception': e})
            self.urlinx += 1
            self.__next__()
        else:
            self.doc = self._parse_detail_page(self.html)
            self.curr_url = self.next_url
            self.urlinx += 1

        return self
