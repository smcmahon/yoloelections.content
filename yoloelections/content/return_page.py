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

required_variables = (
    "contest_title",
    "choice_title",
    "choice_party",
    "precincts_reporting",
    "precincts_total",
    "precincts_percent",
    "choice_votes",
    "choice_percent",
    "cast_votes",
    "cast_votes_percent",
)

BAD_COLMAP = 1000

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

    def getColumnMap(self):
        # get a dictionary from the context that maps column titles to variable names
        column_map = {}
        rows = getattr(self.context, 'column_map', '').split(u"\n")
        for row in rows:
            mapping = row.strip().split(u'|')
            if len(mapping) == 2:
                column_map[mapping[0]] = mapping[1]
        return column_map

    # @ram.cache(lambda *args: time() // 60)
    def contests(self):
        data = cStringIO.StringIO(self.context.return_data.data[csv_skipbytes:])
        reader = csv.reader(data, dialect=csv_dialect)
        rowcount = 0
        last_contest_title = ''
        contests = []
        contest_number = 0
        var_indices = {}
        column_map = self.getColumnMap()

        def getValueFromRow(row, var_name):
            idx = var_indices.get(var_name)
            if idx == BAD_COLMAP:
                return "Missing from column map: {}".format(var_name)
            return row[idx]

        for row in reader:
            rowcount += 1
            if rowcount == 1:
                # this row is the column titles;
                # construct a mapping of column titles to column numbers
                for var_name in required_variables:
                    try:
                        # look up the column title in our column_map;
                        # find the column title index in our title row
                        var_indices[var_name] = row.index(column_map.get(var_name, u'missing column'))
                    except ValueError:
                        # we couldn't find the column title;
                        # prepare to register a complaint when we're asked for this value.
                        var_indices[var_name] = BAD_COLMAP
                # print var_indices
                continue
            if len(row) == 0:
                continue
            contest_title = getValueFromRow(row, 'contest_title')
            if contest_title != last_contest_title:
                last_contest_title = contest_title
                contest_number += 1
                if self.context.show_all_zeros:
                    contests.append(dict(
                        contest_titles=self.entitle(getValueFromRow(row, 'contest_title')).split(' - '),
                        contest_number=contest_number,
                        precincts_reporting='0',
                        precincts_total=getValueFromRow(row, 'precincts_total'),
                        precincts_percent='0.00',
                        cast_votes='0',
                        cast_votes_percent='0.00',
                        choices=[],
                    ))
                else:
                    contests.append(dict(
                        contest_titles=self.entitle(getValueFromRow(row, 'contest_title')).split(' - '),
                        contest_number=contest_number,
                        precincts_reporting=getValueFromRow(row, 'precincts_reporting'),
                        precincts_total=getValueFromRow(row, 'precincts_total'),
                        precincts_percent=getValueFromRow(row, 'precincts_percent'),
                        cast_votes=getValueFromRow(row, 'cast_votes'),
                        cast_votes_percent=getValueFromRow(row, 'cast_votes_percent'),
                        choices=[],
                    ))
            if self.context.show_all_zeros:
                contests[-1]['choices'].append(dict(
                    choice_title=self.entitle(getValueFromRow(row, 'choice_title')),
                    choice_party=getValueFromRow(row, 'choice_party'),
                    choice_votes='0',
                    choice_percent='0.00',
                ))
            else:
                contests[-1]['choices'].append(dict(
                    choice_title=self.entitle(getValueFromRow(row, 'choice_title')),
                    choice_party=getValueFromRow(row, 'choice_party'),
                    choice_votes=getValueFromRow(row, 'choice_votes'),
                    choice_percent=getValueFromRow(row, 'choice_percent'),
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
