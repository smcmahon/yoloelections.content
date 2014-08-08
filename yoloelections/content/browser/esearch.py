# -*- coding: utf-8 -*-

from datetime import date
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


class ElectionSearch(BrowserView):
    """ support for archive search template """

    def edates(self):
        # return list of election dates; list of tuples (ISO, readable)

        edates = list(self.context.portal_catalog.uniqueValuesFor('edate'))
        edates.reverse()

        rez = [(e.isoformat(), e.strftime('%B %d, %Y').replace(' 0', ' ')) for e in edates]
        rez.insert(0, ('', 'Any Date'))
        return rez

    def districts(self):
        # return list of districts
        return [(s, s) for s in self.context.portal_catalog.uniqueValuesFor('district')]


class ElectionReport(BrowserView):
    """ support for archive report template """

    def query(self):
        # Archive catalog lookup; arguments in request.
        # sort by date (descending), district, title

        request = self.request
        context = self.context

        def cmpb(a, b):
            return cmp(
                (a.edate, a.district.lower(), a.title.lower()),
                (b.edate, b.district.lower(), b.title.lower())
                )

        query = {
            'path': '/'.join(context.archives.getPhysicalPath()),
            'portal_type': 'election_result',
            }

        SearchableText = request.get('eltext')
        edate = request.get('election-date')
        district = request.get('districts')
        if SearchableText:
            query['SearchableText'] = SearchableText
        if edate:
            query['edate'] = date(*[int(i) for i in edate.split('-')])
        if district:
            query['district'] = district

        brains = list(context.portal_catalog(query))
        brains.sort(cmpb)
        return [
            {'district':b.district, 'edate':b.edate.strftime('%B %d, %Y').replace(' 0', ' '), 'url':b.getURL(), 'title':b.Title or b.getId}
            for b in brains]
