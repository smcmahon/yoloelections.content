# -*- coding: utf-8 -*-

from Products.Five import BrowserView

import csv
import cStringIO

# District, Office; Candidate/Title; Designation; Party preference; Statement Filename


class VoterGuideView(BrowserView):
    """ support for voter guide template """

    def guideItems(self, ballot=0):

        reader = csv.reader(cStringIO.StringIO(self.context.guide_data.data), dialect='excel')
        # import pdb; pdb.set_trace()
        rez = []
        for row in reader:
            doffice, title, desig, pary, statement, ballots = row
            rez.append([doffice, title, desig, pary, statement, ballots])
        return rez
