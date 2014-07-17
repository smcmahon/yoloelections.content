import re

from Acquisition import aq_inner
from Products.Five import BrowserView

#mpat = re.compile(r'''\<meta name="(.+?)" content="(.+?)"\>''')
mpat = re.compile(r'''\<meta name="(.+?)" content="(.+?)".*?\>''', re.DOTALL)


class ExtractMetadata(BrowserView):
    """ extract data from meta tags in body """

    def __init__(self, context, request):
        self.mdict = dict(mpat.findall(aq_inner(context).getText()))

    def extract(self, id=None):
        """ actually get the metadata """
        if id:
            return self.mdict.get('id')
        else:
            return self.mdict
