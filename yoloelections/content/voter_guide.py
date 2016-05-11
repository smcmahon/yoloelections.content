# -*- coding: utf-8 -*-

from Products.Five import BrowserView

import cgi
import csv
import cStringIO
import re

# District, Office; Candidate/Title; Designation; Party preference; Statement Filename; ballots
# New:
# District, Office; Candidate/Title; Designation; Party preference; statement; statement spanish; impartial analysis; argument for; rebuttal to argument for; argument against; rebuttal to argument against; full text pdf; ballot types


class VoterGuideView(BrowserView):
    """ support for voter guide template """

    def guideItems(self):

        target_ballot = int(self.request.get('ballot', '0'))

        reader = csv.reader(cStringIO.StringIO(self.context.guide_data.data), dialect='excel')
        # import pdb; pdb.set_trace()
        last_doffice = None
        offices = []
        candidates = []
        count = 0
        for row in reader:
            count += 1
            if count == 1:
                continue

            candidate = None
            if len(row) == 6:
                new_style = False
                doffice, candidate, desig, party, statement, ballots = [s.strip().decode('utf8', 'replace') for s in row]
            elif len(row) == 13:
                new_style = True
                doffice, candidate, desig, party, statement, statement_es, analysis, afor, rebut_afor, aag, rebut_aa, full_text, ballots = [s.strip().decode('utf8', 'replace') for s in row]
            else:
                continue

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

            if new_style:
                statement = "?statement=%s" % count
            if new_style and statement_es:
                statement_es = "?statement=%s;l=es" % count
            else:
                statement_es = ''
            candidates.append({
                'candidate': candidate,
                'desig': desig,
                'party': party,
                'statement': statement,
                'statement_es': statement_es,
                'label': label,
            })

        return offices

    def getStatement(self):

        reader = csv.reader(cStringIO.StringIO(self.context.guide_data.data), dialect='excel')
        row_number = int(self.request.get('statement', '0'))
        language = self.request.get('l', 'en')
        count = 0
        for row in reader:
            count += 1
            if count == row_number:
                doffice, candidate, desig, party, statement, statement_es, analysis, afor, rebut_afor, aag, rebut_aag, full_text, ballots = [s.strip().decode('utf8', 'replace') for s in row]
                if language == 'es':
                    statement = statement_es
                else:
                    statement = "\nXXXBREAKXXX\n".join([statement, analysis, afor, rebut_afor, aag, rebut_aag])
                statement = cgi.escape(statement, quote=True)
                formatted = []
                for s in statement.split('\n'):
                    if s == s.upper():
                        formatted.append("<h3>%s</h3>" % s)
                    else:
                        formatted.append("<p>%s</p>" % s)
                statement = '\n'.join(formatted)
                statement = statement.replace('XXXBREAKXXX', "<p>&nbsp;</p>")
                info = {
                    'doffice': doffice,
                    'candidate': candidate,
                    'desig': desig,
                    'party': party,
                    'statement': statement,
                }
                return info
        return ""
