# -*- coding: utf-8 -*-

from datetime import date
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

import re


class ArchiveView(BrowserView):
    """ Archived Election View """


class ArchiveFolderView(BrowserView):
    """ View for folders of election results """

    def folder_contents(self):
        """ return a list of dicts of election results """

        def brain_cmp(a, b):
            return cmp(
                (a.district.lower(), a.Title.lower()),
                (b.district.lower(), b.Title.lower())
                )

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = list(catalog(
            path='/'.join(self.context.getPhysicalPath()),
            portal_type='election_result',
            ))
        brains.sort(brain_cmp)
        return [
            {'district':b.district,
            'url':b.getURL(),
            'title':b.Title or b.getId}
            for b in brains]

    def folder_title(self):
        """ get a title from 8-digit folder name """
        context = self.context

        title = context.Title()
        if title:
            return title
        id = context.getId()
        match = re.match(r'^(\d{4})(\d{2})(\d{2})$', id)
        if match:
            year, month, day = match.groups()
            return date(int(year), int(month), int(day)).strftime('%B %d, %Y').replace(' 0', ' ')
        else:
            return id

