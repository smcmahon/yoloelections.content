# -*- coding: utf8 -*-

"""

usage: bin/client1 run src/yoloelections.content/upload_archive.py 20160607

"""

from plone.app.textfield.value import RichTextValue
from transaction import commit
from zope.component import createObject
from zope.component.hooks import setSite

import datetime
import os
import os.path
import re
import sys

app = app

mpat = re.compile(r'''\<meta name="(.+?)" content="(.+?)".*?\>''', re.DOTALL)

source_path = os.path.join(os.getcwd(), 'archive')
target_path = 'election-returns/archives/%s' % sys.argv[3]
charset = 'UTF-8'

site = app.yolo_recorder_sites.elections
setSite(site)
# catalog = site.portal_catalog
folder = site.restrictedTraverse(target_path)

for fn in os.listdir(source_path):
    if fn.startswith('.'):
        continue
    filename = os.path.join(source_path, fn)
    if fn.endswith('.html'):
        f = open(filename, 'ra')
        source = f.read()
        f.close()
        text = source.replace('&#x2588;', '█').decode(charset)
        mdict = dict(mpat.findall(text))
        title = mdict.get('title', '')
        edate = mdict.get('edate', '')
        district = mdict.get('district', '')
        if title:
            new_id = fn[:-5]
            print fn, new_id, title, edate, district
            new_obj = createObject("election_result")
            new_obj.id = new_id
            new_obj.title = title
            new_obj.district = district
            year, month, day = edate.split('-')
            new_obj.edate = datetime.date(int(year), int(month), int(day))
            new_obj.body = RichTextValue(text, 'text/html', 'text/html')
            folder[new_id] = new_obj
            commit()
