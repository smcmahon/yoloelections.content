# -*- coding: utf-8 -*-

from plone.i18n.normalizer import idnormalizer
# from plone.memoize import ram
from Products.Five import BrowserView
# from time import time

import csv
import cStringIO


csv_dialect = 'excel'
csv_charset = 'utf8'
csv_skipbytes = 3
csv_skiprows = 1

col_contest_number = 5
col_contest_title = 0
col_choice_title = 13
col_choice_party = 14
col_precincts_reporting = 2
col_precincts_total = 3
col_precincts_percent = 4
col_choice_votes = 25
col_choice_percent = 26
col_cast_votes = 37
col_cast_votes_percent = 38

# corrections for string.title results
title_fixup_pairs = (
    (u' The ', u' the '),
    (u' A ', u' a '),
    (u' Of ', u' of '),
    (u'1St ', u'1st '),
    (u'2Nd ', u'2nd '),
    (u'3Rd ', u'3rd '),
    (u'4Th ', u'4th '),
    (u'5Th ', u'5th '),
    (u'6Th ', u'6th '),
    (u'7Th ', u'7th '),
    (u'8Th ', u'8th '),
    (u'Usd', u'USD'),
    (u'Jusd', u'JUSD'),
    (u'Djusd', u'DJUSD'),
    (u'Ws ', u'WS '),
    (u'Us ', u'US '),
    (u'Iii', u'III')
)


class ReturnPageView(BrowserView):
    """ support for return page template
        Parses the csv file in return_data,
        returns a list of contests;
        contests is a list of contest dicts:
            contest_titles,
            precincts_reporting,
            precincts_total,
            precincts_percent,
            cast_votes,
            cast_votes_percent,
            choices,
        choices is a list of candidate/choice dicts:
            choice_title,
            choice_party,
            choice_votes,
            choice_percent,
    """

    def entitle(self, contest):
        # title case with fixups
        # convert to unicode first to get good case transforms for extended charset
        contest = contest.decode('utf8').title()
        # built-in transforms
        for s, r in title_fixup_pairs:
            contest = contest.replace(s, r)
        # transforms specified in the content item
        for line in (getattr(self.context, 'title_fixups', '') or '').split(u'\n'):
            pair = line.split(u'|')
            if len(pair) > 1:
                contest = contest.replace(pair[0], pair[1])
        return contest

    # @ram.cache(lambda *args: time() // 60)
    def contests(self):
        # include_contests = set((getattr(self.context, 'contests_to_include', '') or '').split())
        # exclude_contests = set((getattr(self.context, 'contests_to_exclude', '') or '').split())
        data = cStringIO.StringIO(self.context.return_data.data[csv_skipbytes:])
        reader = csv.reader(data, dialect=csv_dialect)
        rowcount = 0
        last_contest_title = ''
        contests = []
        contest_number = 0
        for row in reader:
            rowcount += 1
            if rowcount <= csv_skiprows:
                continue
            if len(row) == 0:
                continue
            contest_title = row[col_contest_title]
            # if include_contests and contest_number not in include_contests:
            #     continue
            # if contest_number in exclude_contests:
            #     continue
            if contest_title != last_contest_title:
                last_contest_title = contest_title
                contest_number += 1
                if self.context.show_all_zeros:
                    contests.append(dict(
                        contest_titles=self.entitle(row[col_contest_title]).split(' - '),
                        contest_number=contest_number,
                        precincts_reporting='0',
                        precincts_total=row[col_precincts_total],
                        precincts_percent='0.00',
                        cast_votes='0',
                        cast_votes_percent='0.00',
                        choices=[],
                    ))
                else:
                    contests.append(dict(
                        contest_titles=self.entitle(row[col_contest_title]).split(' - '),
                        contest_number=contest_number,
                        precincts_reporting=row[col_precincts_reporting],
                        precincts_total=row[col_precincts_total],
                        precincts_percent=row[col_precincts_percent],
                        cast_votes=row[col_cast_votes],
                        cast_votes_percent=row[col_cast_votes_percent],
                        choices=[],
                    ))
            if self.context.show_all_zeros:
                contests[-1]['choices'].append(dict(
                    choice_title=self.entitle(row[col_choice_title]),
                    choice_party=row[col_choice_party],
                    choice_votes='0',
                    choice_percent='0.00',
                ))
            else:
                contests[-1]['choices'].append(dict(
                    choice_title=self.entitle(row[col_choice_title]),
                    choice_party=row[col_choice_party],
                    choice_votes=row[col_choice_votes],
                    choice_percent=row[col_choice_percent],
                ))
        return contests

    def pages(self):
        # paginated contests
        # returns a list of pages;
        # each page is a dict with keys:
        #     page_title,
        #     page_id,
        #     contests
        # page_id is a normalized id created from the page title.

        contests = self.contests()
        pagination = getattr(self.context, 'pagination', '') or ''
        pagination = [s for s in [s.strip() for s in pagination.split('\n')] if s]

        if len(pagination):
            # create a dict of contests with the contest numbers as keys.
            # contests_by_number = [(contest['contest_number'], contest) for contest in contests]
            pages = []
            for page in pagination:
                page_title, contest_numbers = page.split('|')
                contest_numbers = [int(i) for i in contest_numbers.split()]
                pages.append(dict(
                    page_title=page_title,
                    page_id=idnormalizer.normalize(page_title),
                    contests=[contest for contest in contests if contest['contest_number'] in contest_numbers]
                ))
            return pages
        else:
            return [dict(
                page_title="All",
                page_id="all_contests",
                contests=contests
            )]
