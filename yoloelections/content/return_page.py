# -*- coding: utf-8 -*-

from Products.Five import BrowserView

# import cgi
import csv
import cStringIO
# import re


fields = {
    'Page': 'Page',
    'Contest #': 'contest',
    'Contest Name': 'contest_name',
    'Cadn/choice name': 'choice_name',
    'PARTY': 'party',
    'RANK': 'rank',
    'cont code': None,
    'choice code': None,
    'options': 'options',
    'ballots cast': 'ballots_cast',
    'votes': 'votes',
    'precincts ': 'precincts',
    'prec reporting': 'prec_reporting',
    'VOTE W TIEBREAKER': 'vote_tiebreaker',
}
int_fields = [
    'contest',
    'rank',
    'ballots_cast',
    'options',
    'votes',
    'precincts',
    'prec_reporting',
]
float_fields = [
    'vote_tiebreaker',
]
sort_order = (
    'contest',
    'rank',
)


def utf16Fix(data):
    if data[0] == '\xff':
        return data.decode('utf16').encode('utf8')
    return data


def contest_cmp(a, b):
    for crit in sort_order:
        ccmp = cmp(a[crit], b[crit])
        if ccmp:
            return ccmp
    return 0


class ReturnPageView(BrowserView):
    """ support for return page template """

    def contests(self):
        reader = csv.DictReader(
            cStringIO.StringIO(utf16Fix(self.context.return_data.data)),
            dialect='excel'
        )
        rows = []
        for row in reader:
            rez = {}
            for akey in row.keys():
                fixed_key = fields[akey]
                if fixed_key is not None:
                    if fixed_key in int_fields:
                        rez[fixed_key] = int(row[akey])
                    elif fixed_key in float_fields:
                        rez[fixed_key] = float(row[akey])
                    else:
                        rez[fixed_key] = row[akey]
            rows.append(rez)
        rows.sort(contest_cmp)
        contests = []
        last_contest = 0
        for row in rows:
            contest_no = row['contest']
            if contest_no != last_contest:
                last_contest = contest_no
                this_contest = dict(
                    contest_name=row['contest_name'],
                    precincts=row['precincts'],
                    prec_reporting=row['prec_reporting'],
                    ballots_cast=row['ballots_cast'],
                    choices=[],
                    options=row['options'],
                )
                contests.append(this_contest)
            this_contest['choices'].append(dict(
                choice_name=row['choice_name'],
                party=row['party'],
                votes=row['votes'],
                klass=(row['options'] >= row['rank']) and 'leading' or None,
            ))
        return contests
