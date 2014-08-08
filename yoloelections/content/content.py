# -*- coding: utf-8 -*-
#
from interfaces import (
    IElectionResult,
    ICandidateFiling,
    ICandidateFilings,
)

from plone.dexterity.content import Container
from plone.dexterity.content import Item
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import implements


class ElectionResult(Item):
    implements(IElectionResult)


class CandidateFiling(Item):
    implements(ICandidateFiling)


class CandidateFilings(Container):
    implements(ICandidateFilings)


def setOffice(obj, event):
    ''' Sets office name on folder if needed
    '''

    if ICandidateFiling.providedBy(obj):
        if obj.office == u"New Office":
            new_office = u"%s | %s" % (
                obj.office_category.strip(),
                obj.office_name.strip(),
                )
            obj.office = new_office
            parent = obj.aq_parent
            offices = parent.offices
            if offices is None:
                offices = u''
            if offices:
                offices = offices.strip() + "\n"
            parent.offices = offices + new_office

            messages = IStatusMessage(obj.REQUEST)
            messages.add(u"Office added", type=u"info")


