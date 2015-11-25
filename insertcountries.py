from __future__ import division
import json
import os
import codecs
import re


TABLE = 'projects_country'
ps_TABLE = 'projects_powerstation'
isp_TABLE = 'projects_isp'

DROP_STMT = 'DROP TABLE IF EXISTS %s;\nDROP TABLE IF EXISTS %s;\nDROP TABLE IF EXISTS %s;\n' % (TABLE, ps_TABLE, isp_TABLE)
CREATE_STMT_country = 'CREATE TABLE %s (country_code varchar PRIMARY KEY NOT NULL, name varchar, population varchar, using_inet varchar, using_inet_per varchar, color varchar);\n' % TABLE
CREATE_STMT_nps = 'CREATE TABLE %s (id uuid PRIMARY KEY DEFAULT uuid_generate_v4(), name varchar, status varchar, power varchar, latitude varchar, longitude varchar, country_code varchar);\n' % ps_TABLE
CREATE_STMT_isp = 'CREATE TABLE %s (id uuid PRIMARY KEY DEFAULT uuid_generate_v4(), name varchar, country_code varchar);\n' % isp_TABLE
INSERT_STMT_country = 'INSERT INTO %s (country_code, name, population, using_inet, using_inet_per, color) VALUES (%%s);\n' % TABLE
INSERT_STMT_nps = 'INSERT INTO %s (name, status, power, latitude, longitude, country_code) VALUES %%s;\n' % ps_TABLE
INSERT_STMT_isp = 'INSERT INTO %s (name, country_code) VALUES %%s;\n' % isp_TABLE

def getcoords(coordstring):
    try:
        (lat_str, lon_str) = coordstring.split(' ')
        lat = getcoord(lat_str)
        lon = getcoord(lon_str)
        return (lat, lon)
    except ValueError as e:
        print(type(coordstring))
        print(coordstring)
        return ('', '')

def getcoord(string):
    dms_tuple = string.split('.')
    dms_numeric = tuple(int(item) for item in dms_tuple[:-1])
    coord = (dms_numeric[0] + dms_numeric[1]/60 + dms_numeric[2]/3600)*(-1 if dms_tuple[3] in ['S', 'W'] else 1)
    return str(coord)

country_reference = {}

countryfile = codecs.open('country.json', 'r', encoding='utf8')
raw_country = json.loads(countryfile.read())
countryfile.close()
if raw_country and type(raw_country) is list:
    for countryobj in raw_country:
        cid = countryobj['code']
        if country_reference.get(cid, {}):
            for key in country_reference[cid]:
                if country_reference[cid][key] == '0':
                    country_reference[cid][key] = countryobj[key]
        else:
            country_reference[cid] = dict((x, countryobj[x]) for x in countryobj)

for cid in country_reference:
    obj = country_reference[cid]
    if obj['using_inet'] == '0' and obj['using_inet_per'] != '0':
        obj['using_inet'] = str(divmod(int(obj['population']), 100)[0] * int(obj['using_inet_per']))
          
with codecs.open('countries.sql', 'w', encoding='utf8') as sqlfile:
    sqlfile.write(DROP_STMT + CREATE_STMT_country + CREATE_STMT_nps + CREATE_STMT_isp)
    for cid in country_reference:
        obj = country_reference[cid]
        country_valuelist = [cid, obj['name'].replace('\'', '\'\''), \
            obj['population'], obj['using_inet'], obj['using_inet_per'], obj['color']]
        print(country_valuelist)
        country_valuestring = u', '.join(u'\'{0}\''.format(a) for a in country_valuelist)
        sqlfile.write(INSERT_STMT_country % country_valuestring)
        if obj['nps'] and type(obj['nps']) is list:
            country_nps = []
            for nps in obj['nps']:
               coords = getcoords(nps['coordinate'])
               nps_valuelist = [nps['name'].replace('\'', '\'\''), \
                   nps['status'].replace('\'', '\'\''), nps['power'],\
                   coords[0], coords[1], cid]
               country_nps.append(u'({0})'.format(u', '.join(u'\'{0}\''.format(a) for a in nps_valuelist)))
            sqlfile.write(INSERT_STMT_nps % ', '.join(country_nps))
    ispfile = codecs.open('isp_providers.json', 'r')
    isp_reference = json.loads(ispfile.read())
    for cid in isp_reference:
        lst = isp_reference[cid]
        if lst and type(lst) is list:
            country_isp = []
            for item in lst:
                isp_valuelist = [item.replace('\'', '\'\''), cid]
                country_isp.append(u'({0})'.format(u', '.join(u'\'{0}\''.format(a) for a in isp_valuelist)))
            sqlfile.write(INSERT_STMT_isp % ', '.join(country_isp))


