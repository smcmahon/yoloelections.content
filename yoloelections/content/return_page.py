# -*- coding: utf-8 -*-

from plone.i18n.normalizer import idnormalizer
from plone.memoize import ram
from Products.Five import BrowserView
from time import time

import csv
import cStringIO

fields = {
    'Page': 'page',
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
    'page',
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


def commaize(anint):
    """ return number formatted with thousand comma """
    thou = anint / 1000
    if thou:
        return "%d,%03d" % (thou, anint % 1000)
    else:
        return "%d" % anint


def entitle(contest):
    contest = contest.title()
    contest = contest.replace(' The ', ' the ')
    contest = contest.replace(' A ', ' a ')
    contest = contest.replace(' Of ', ' of ')
    contest = contest.replace('1St ', '1st ')
    contest = contest.replace('2Nd ', '2nd ')
    contest = contest.replace('3Rd ', '3rd ')
    contest = contest.replace('4Th ', '4th ')
    contest = contest.replace('5Th ', '5th ')
    contest = contest.replace('6Th ', '6th ')
    contest = contest.replace('7Th ', '7th ')
    contest = contest.replace('8Th ', '8th ')
    contest = contest.replace('Usd', 'USD')
    contest = contest.replace('Jusd', 'JUSD')
    contest = contest.replace('Ws ', 'WS ')
    contest = contest.replace('Us ', 'US ')
    return contest


class ReturnPageView(BrowserView):
    """ support for return page template """

    @ram.cache(lambda *args: time() // 60)
    def pages(self):
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
        pages = []
        last_page = ''
        last_contest = 0
        for row in rows:
            page = row['page']
            if page != last_page:
                last_page = page
                contests = []
                pages.append(dict(
                    page_title=entitle(page),
                    page_id=idnormalizer.normalize(page),
                    contests=contests,
                ))
            contest_no = row['contest']
            if contest_no != last_contest:
                last_contest = contest_no
                this_contest = dict(
                    contest_name=entitle(row['contest_name']),
                    precincts=row['precincts'],
                    prec_reporting=row['prec_reporting'],
                    ballots_cast=row['ballots_cast'],
                    choices=[],
                    options=row['options'],
                )
                contests.append(this_contest)
            this_contest['choices'].append(dict(
                choice_name=row['choice_name'].title(),
                party=row['party'],
                votes=commaize(row['votes']),
                klass=(row['options'] >= row['rank']) and 'leading' or None,
            ))
        return pages
