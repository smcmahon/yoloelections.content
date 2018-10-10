# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.PortalTransforms.transforms.rest import rest as Rest

import cgi
import csv
import cStringIO
import re

# District, Office; Candidate/Title; Designation; Party preference; Statement Filename; ballots
# New:
# District, Office; Candidate/Title; Designation; Party preference; statement; statement spanish; impartial analysis; argument for; rebuttal to argument for; argument against; rebuttal to argument against; full text pdf; ballot types


def utf16Fix(data):
    if data[0] == '\xff':
        return data.decode('utf16').encode('utf8')
    return data


class D:
    def setData(self, data):
        self.value = data


class VoterGuideView(BrowserView):
    """ support for voter guide template """

    def guideItems(self):
        target_ballot = int(self.request.form.get('ballot', '0'))

        reader = csv.reader(cStringIO.StringIO(utf16Fix(self.context.guide_data.data)), dialect='excel')
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
            elif len(row) == 15:
                new_style = True
                doffice, candidate, desig, party, statement, statement_es, statement_ru, tax_statement, analysis, afor, rebut_afor, aag, rebut_aa, full_text, ballots = [s.strip().decode('utf8', 'replace') for s in row]
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
                        try:
                            my_ballots.append(int(ballot))
                        except ValueError:
                            pass
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
                label = 'Tax statement, analysis, text and arguments'
            else:
                label = 'Statement'

            if new_style:
                if statement or analysis or afor or rebut_afor or aag or rebut_aa:
                    statement = "?statement=%s" % count
            else:
                full_text = ''
            if new_style and statement_es:
                statement_es = "?statement=%s;l=es" % count
            else:
                statement_es = ''
            if new_style and statement_ru:
                statement_ru = "?statement=%s;l=ru" % count
            else:
                statement_ru = ''
            candidates.append({
                'candidate': candidate,
                'desig': desig,
                'party': party,
                'statement': statement,
                'statement_es': statement_es,
                'statement_ru': statement_ru,
                'full_text': full_text,
                'label': label,
            })

        return offices

    def getStatement(self):

        reader = csv.reader(cStringIO.StringIO(utf16Fix(self.context.guide_data.data)), dialect='excel')
        row_number = int(self.request.get('statement', '0'))
        language = self.request.get('l', 'en')
        count = 0
        for row in reader:
            count += 1
            if count == row_number:
                doffice, candidate, desig, party, statement, statement_es, statement_ru, tax_statement, analysis, afor, rebut_afor, aag, rebut_aag, full_text, ballots = [s.strip().decode('utf8', 'replace') for s in row]
                if language == 'es':
                    statement = statement_es
                elif language == 'ru':
                    statement = statement_ru
                else:
                    statement = u"XXXBREAKXXX".join([tax_statement, statement, analysis, afor, rebut_afor, aag, rebut_aag])
                statement = re.sub(u'(XXXBREAKXXX)*$', u'', statement)
                statement = re.sub(u'^(XXXBREAKXXX)*', u'', statement)
                statement = statement.replace(u'\r\n', u'\n')

                if u'\n\n' in statement:
                    # process as ReST
                    statement = statement.replace(u'\u2022', u'    *')
                    statement = re.sub(ur'([^\n])\n([^\n])', ur'\1 \2', statement)
                    transform = Rest()
                    data = transform.convert(statement, D())
                    statement = data.value.replace('XXXBREAKXXX', "<p><hr /></p>")
                else:
                    # minimal processing to preserve lines
                    statement = cgi.escape(statement, quote=True)
                    formatted = []
                    for s in statement.split('\n'):
                        formatted.append("%s<br />" % s)
                    statement = '\n'.join(formatted)
                    statement = statement.replace('XXXBREAKXXX', "<p><hr /></p>")

                info = {
                    'doffice': doffice,
                    'candidate': candidate,
                    'desig': desig,
                    'party': party,
                    'statement': statement,
                }
                return info
        return ""

    def getDownloadableSampleURL(self, prefix='bt'):
        target_ballot = int(self.request.form.get('ballot', '0'))
        if target_ballot:
            fn = '%s-%02d.pdf' % (prefix, target_ballot)
            obj = self.context.get(fn)
            if obj is not None:
                return obj.absolute_url()
            return ''
