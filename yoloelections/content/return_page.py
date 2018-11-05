# -*- coding: utf-8 -*-

from plone.i18n.normalizer import idnormalizer
from plone.memoize import ram
from Products.Five import BrowserView
from time import time

import csv
import cStringIO

# column headers mapped to field keys
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
# These fields get converted to integers
int_fields = [
    'contest',
    'rank',
    'ballots_cast',
    'options',
    'votes',
    'precincts',
    'prec_reporting',
]
# These fields get converted to floats
float_fields = [
    'vote_tiebreaker',
]
# sort hierarchy
sort_order = (
    'page',
    'contest',
    'rank',
)
# corrections for string.title results
title_fixups = (
    (' The ', ' the '),
    (' A ', ' a '),
    (' Of ', ' of '),
    ('1St ', '1st '),
    ('2Nd ', '2nd '),
    ('3Rd ', '3rd '),
    ('4Th ', '4th '),
    ('5Th ', '5th '),
    ('6Th ', '6th '),
    ('7Th ', '7th '),
    ('8Th ', '8th '),
    ('Usd', 'USD'),
    ('Jusd', 'JUSD'),
    ('Ws ', 'WS '),
    ('Us ', 'US '),
)


def utf16Fix(data):
    # if this looks like utf16, convert to utf8
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
    # title case with fixups
    contest = contest.title()
    for s, r in title_fixups:
        contest = contest.replace(s, r)
    return contest


def as_pct(num, denom):
    if denom == 0:
        return "0.0%"
    return "{:0.1f}%".format(100.0 * num / denom)


class ReturnPageView(BrowserView):
    """ support for return page template
        Parses the csv file in return_data,
        returns a list of pages;
        each page is a dict with keys:
            page_title,
            page_id,
            contests
        page_id is a normalized id created from the page title.
        contests is a list of contest dicts:
            contest_name,
            precincts,
            prec_reporting,
            ballots_cast,
            choices,
            options
        choices is a list of candidate/choice dicts:
            choice_name,
            party,
            votes,
            klass
        klass is a css class used to highlight leaders.
    """

    # @ram.cache(lambda *args: time() // 60)
    def pages(self):
        reader = csv.DictReader(
            cStringIO.StringIO(utf16Fix(self.context.return_data.data)),
            dialect='excel'
        )

        # parse the csv, sort it
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

        # construct pages list
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
                    prec_percent=as_pct(row['precincts'], row['prec_reporting']),
                    ballots_cast=row['ballots_cast'],
                    choices=[],
                    options=row['options'],
                    multi_option=row['options'] > 1,
                    total_votes=0,
                )
                contests.append(this_contest)
            this_contest['total_votes'] += row['votes']
            this_contest['choices'].append(dict(
                choice_name=row['choice_name'].title(),
                party=row['party'],
                votes=row['votes'],
                votes_rep=commaize(row['votes']),
                klass=(row['options'] >= row['rank']) and 'leading' or None,
            ))
        # compute some percentages
        for page in pages:
            for contest in page['contests']:
                total_votes = contest['total_votes']
                ballots_cast = contest['ballots_cast']
                for choice in contest['choices']:
                    choice['vote_pct'] = as_pct(choice['votes'], total_votes)
                    choice['ballot_pct'] = as_pct(choice['votes'], ballots_cast)

        return pages
