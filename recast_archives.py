# rewrite election result pages to get the write class and interface

from plone.app.textfield.value import RichTextValue
from plone.app.linkintegrity.exceptions import LinkIntegrityNotificationException
from transaction import commit
from zope.component import createObject
from zope.component.hooks import setSite

import datetime
import re


app = app
site = app.yolo_recorder_sites.elections
setSite(site)
catalog = site.portal_catalog

brains = catalog(portal_type='election_result')
for brain in brains:
    if brain.meta_type == 'Dexterity Container':
        obj = brain.getObject()
        folder = obj.aq_parent
        print obj.absolute_url()

        new_obj = createObject("election_result")
        new_obj.id = obj.id
        new_obj.title = obj.title
        new_obj.district = obj.district
        new_obj.edate = obj.edate
        new_obj.body = obj.body
        new_obj.subject = obj.subject
        try:
            folder.manage_delObjects([obj.id])
        except LinkIntegrityNotificationException:
            pass
        folder[new_obj.id] = new_obj
        commit()
