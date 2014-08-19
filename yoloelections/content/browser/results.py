# -*- coding: utf-8 -*-

from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from plone.app.textfield.value import RichTextValue
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from transaction import commit
from zope.component import createObject
from zope.component.hooks import setSite

import datetime
import re

mpat = re.compile(r'''\<meta name="(.+?)" content="(.+?)".*?\>''', re.DOTALL)
charset = 'UTF-8'


class ImportView(BrowserView):
    """ Convert pages to election results """

    def __call__(self):
        context = self.context
        target_path = '/'.join(context.getPhysicalPath())

        catalog = getToolByName(context, 'portal_catalog')

        brains = catalog(portal_type='Document', path=target_path)
        for brain in brains:
            if brain.id.endswith('.html'):
                obj = brain.getObject()
                folder = obj.aq_parent
                id = brain.id
                text = obj.getRawText().decode(charset)
                mdict = dict(mpat.findall(text))
                title = mdict.get('title', '').decode(charset).strip()
                edate = mdict.get('edate', '').decode(charset)
                district = mdict.get('district', '').decode(charset)
                if title:
                    new_id = id[:-5]
                    print id, new_id, title, edate, district
                    new_obj = createObject("election_result")
                    new_obj.id = new_id
                    new_obj.title = title
                    new_obj.district = district
                    year, month, day = edate.split('-')
                    new_obj.edate = datetime.date(int(year), int(month), int(day))
                    new_obj.body = RichTextValue(text, 'text/html', 'text/html')
                    folder[new_id] = new_obj
                    try:
                        folder.manage_delObjects([id])
                    except LinkIntegrityNotificationException:
                        pass
                    commit()
