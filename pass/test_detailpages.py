'''
Created on 17 May 2018

@author: David
'''
import unittest
from detailpages import DetailPages


class DetailPagesTest(unittest.TestCase):
    def getCounts(self, urls):
        detailpages = DetailPages(
            urls, lambda html: {'html': html, 'len': 'len(html)'})
        page_count = 0
        for detailpage in detailpages:
            page_count += 1
        exception_count = 0
        if(detailpages.exceptions):
            exception_count = len(detailpages.exceptions)
        return page_count, exception_count

    def testGetThreeOfThree(self):
        urls = ['https://www.google.com/',
                'https://www.youtube.com/', 'https://www.facebook.com/']
        pagecount, exceptioncount = self.getCounts(urls)
        self.assertEqual((pagecount, exceptioncount), (3, 0))

    def testGetTwoOfThree1(self):
        urls = ['https://www.google.comMMM/',
                'https://www.youtube.com/', 'https://www.facebook.com/']
        pagecount, exceptioncount = self.getCounts(urls)
        self.assertEqual((pagecount, exceptioncount), (2, 1))

    def testGetTwoOfThree2(self):
        urls = ['https://www.google.com/',
                'https://www.youtube.comMMM/', 'https://www.facebook.com/']
        pagecount, exceptioncount = self.getCounts(urls)
        self.assertEqual((pagecount, exceptioncount), (2, 1))

    def testGetTwoOfThree3(self):
        urls = ['https://www.google.com/',
                'https://www.youtube.com/', 'https://www.facebook.comMMM/']
        pagecount, exceptioncount = self.getCounts(urls)
        self.assertEqual((pagecount, exceptioncount), (2, 1))

    def testGetOneOfThree1(self):
        urls = ['https://www.google.comMMM/',
                'https://www.youtube.comMMM/', 'https://www.facebook.com/']
        pagecount, exceptioncount = self.getCounts(urls)
        self.assertEqual((pagecount, exceptioncount), (1, 2))

    def testGetOneOfThree2(self):
        urls = ['https://www.google.comMMM/',
                'https://www.youtube.com/', 'https://www.facebook.comMMM/']
        pagecount, exceptioncount = self.getCounts(urls)
        self.assertEqual((pagecount, exceptioncount), (1, 2))

    def testGetOneOfThree3(self):
        urls = ['https://www.google.com/',
                'https://www.youtube.comMMM/', 'https://www.facebook.comMMM/']
        pagecount, exceptioncount = self.getCounts(urls)
        self.assertEqual((pagecount, exceptioncount), (1, 2))

    def testGetZeroOfThree(self):
        urls = ['https://www.google.comMMM/',
                'https://www.youtube.comMMM/', 'https://www.facebook.comMMM/']
        pagecount, exceptioncount = self.getCounts(urls)
        self.assertEqual((pagecount, exceptioncount), (0, 3))


# if __name__ == "__main__":
#     ''' "Errare (Errasse) humanum est, sed in errare (errore) perseverare diabolicum."
#     (To err is human, but to persist in it is diabolic")
#     https://www.python-course.eu/python3_tests.php
#     '''
#     unittest.main()
