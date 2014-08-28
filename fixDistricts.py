from transaction import commit

old_new = [
    (u'CA Assembly, Eighth District', u'CA Assembly, 8th District'),
    (u'CA Assembly, Fourth District', u'CA Assembly, 4th District'),
    (u'CA Assembly, Second District', u'CA Assembly, 2nd District'),
    (u'CA Assembly, Seventh District', u'CA Assembly, 7th District'),
    (u'CA Senate, Fifth District', u'CA Senate, 5th District'),
    (u'CA Senate, Fourth District', u'CA Senate, 4th District'),
    (u'CA Senate, Third District', u'CA Senate, 3rd District'),
    (u'U.S. Representative, First District', u'U.S. Representative, 1st District'),
    (u'U.S. Representative, Second District', u'U.S. Representative, 2nd District'),
    (u'U.S. Representative, Sixth District', u'U.S. Representative, 6th District'),
    (u'U.S. Representative, Third District', u'U.S. Representative, 3rd District'),
    (u'US Representative, Sixth District', u'US Representative, 6th District'),
]

app = app

pc = app.yolo_recorder_sites.elections.portal_catalog
for oldd, newd in old_new:
    for brain in pc(district=oldd):
        obj = brain.getObject()
        print obj.absolute_url()
        obj.district = newd
    commit()

