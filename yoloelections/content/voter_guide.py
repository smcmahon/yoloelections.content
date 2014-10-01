# -*- coding: utf-8 -*-

from Products.Five import BrowserView

import csv
import cStringIO
import re

# District, Office; Candidate/Title; Designation; Party preference; Statement Filename; ballots


class VoterGuideView(BrowserView):
    """ support for voter guide template """

    def guideItems(self):

        target_ballot = int(self.request.get('ballot', '0'))

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

            if target_ballot:
                my_ballots = []
                for ballot in [s.strip() for s in re.split(r"[, ]", ballots)]:
                    if '-' in ballot:
                        start, end = ballot.split('-')
                        my_ballots += range(int(start), int(end) + 1)
                    else:
                        my_ballots.append(int(ballot))
                if target_ballot not in my_ballots:
                    continue

            if doffice != last_doffice:
                last_doffice = doffice
                candidates = []
                offices.append({
                    'doffice': doffice,
                    'candidates': candidates,
                    })
            if candidate.startswith('Measure'):
                label = 'Analysis, text and arguments'
            else:
                label = 'Statement'
            candidates.append({
                    'candidate': candidate,
                    'desig': desig,
                    'party': party,
                    'statement': statement,
                    'label': label,
                })

        return offices
