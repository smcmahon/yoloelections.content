# -*- coding: utf-8 -*-

from interfaces import ICandidateFiling
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


@provider(IContextSourceBinder)
def officeVocabulary(context):
    while context is not None:
        terms = [SimpleTerm('New Office', 0, 'New Office')]
        offices = getattr(context, 'offices', None)
        if offices is not None:
            offices = [s.strip() for s in offices.split('\n')]
            offices.sort()
            for office in offices:
                terms.append(SimpleTerm(value=office, token=len(terms), title=office))
            break
        context = getattr(context, 'aq_parent', None)
    return SimpleVocabulary(terms)


@provider(IContextSourceBinder)
def partiesVocabulary(context):
    while context is not None:
        terms = []
        parties = getattr(context, 'parties', None)
        if parties is not None:
            parties = [s.strip() for s in parties.split('\n')]
            parties.sort()
            for party in parties:
                terms.append(SimpleTerm(value=party, token=len(terms), title=party))
            break
        context = getattr(context, 'aq_parent', None)
    return SimpleVocabulary(terms)


def compareFilings(a, b):
    ao = a.office.lower()
    bo = b.office.lower()
    if ao > bo:
        return 1
    elif ao < bo:
        return -1
    else:
        return cmp(a.title, b.title)


class FilingsView(BrowserView):
    """ support for filings template """

    def getFilings(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []
        for rez in catalog(object_provides=ICandidateFiling.__identifier__, review_state="published"):
            results.append(rez.getObject())
        results.sort(compareFilings)
        categories = []
        last_cat = None
        last_office = None
        for rez in results:
            if rez.office_category != last_cat:
                last_cat = rez.office_category
                offices = []
                categories.append((last_cat, offices))
                last_office = None
            if rez.office_name != last_office:
                last_office = rez.office_name
                candidates = []
                offices.append((last_office, candidates))
            candidates.append(rez)
        return categories
