# -*- coding: utf-8 -*-

from copy import deepcopy
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
                # Guard against accidental duplicates which are not allowed
                # by SimpleVocabulary
                old_terms = deepcopy(terms)
                terms.append(SimpleTerm(value=office, token=len(terms), title=office))
                try:
                    dummy = SimpleVocabulary(terms)
                except ValueError:
                    terms = old_terms
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
                # Guard against accidental duplicates which are not allowed
                # by SimpleVocabulary
                old_terms = deepcopy(terms)
                terms.append(SimpleTerm(value=party, token=len(terms), title=party))
                try:
                    dummy = SimpleVocabulary(terms)
                except ValueError:
                    terms = old_terms
            break
        context = getattr(context, 'aq_parent', None)
    return SimpleVocabulary(terms)


def striplowcmp(a, b):
    return cmp(a.strip().lower(), b.strip().lower())


def compareFilings(a, b):
    asa = (getattr(a, 'sort_as', None) or '').strip()
    bsa = (getattr(b, 'sort_as', None) or '').strip()
    if asa:
        if bsa:
            return striplowcmp(asa, bsa)
        return -1
    if bsa:
        return 1
    rez = striplowcmp(a.office, b.office)
    if rez == 0:
        return striplowcmp(a.title, b.title)
    return rez


class FilingsView(BrowserView):
    """ support for filings template """

    def getFilings(self):
        target_path = '/'.join(self.context.getPhysicalPath())
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []
        matches = catalog(
            object_provides=ICandidateFiling.__identifier__,
            review_state="published",
            path=target_path
        )
        for rez in matches:
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
                s = last_office
                office_name_misc = getattr(rez, 'office_name_misc', None)
                if office_name_misc is not None:
                    s = '%s (%s)' % (s, office_name_misc)
                candidates = []
                offices.append((s, candidates))
            candidates.append(rez)
        return categories
