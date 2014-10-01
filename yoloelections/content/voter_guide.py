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
        first = True
        last_doffice = None
        offices = []
        candidates = []
        for row in reader:
            if first:
                first = False
                continue
            doffice, candidate, desig, party, statement, ballots = [s.strip().decode('utf8', 'replace') for s in row]
            if not candidate:
                continue
            if doffice != last_doffice:
                last_doffice = doffice
                candidates = []
                offices.append({
                    'doffice': doffice,
                    'candidates': candidates,
                    })
            candidates.append({
                    'candidate': candidate,
                    'desig': desig,
                    'party': party,
                    'statement': statement,
                })

#            my_ballots = []
#            for ballot in [s.strip() for s in ballots.split(',')]:
#                if '-' in ballot:
#                    start, end = ballot.split('-')
#                    my_ballots += range(int(start), int(end)+1)
#                else:
#                    my_ballots.append(int(ballot))
#                my_ballots.append(ballot)
#            rez.append([doffice, title, desig, pary, statement, ballots,
#                        my_ballots])
        return offices
