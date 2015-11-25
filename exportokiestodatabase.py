import json
import os
import codecs

TABLE = 'projects_okies_test_big'
DROP_STMT = 'DROP TABLE IF EXISTS %s;\n' % TABLE
CREATE_STMT = 'CREATE TABLE %s (id uuid PRIMARY KEY DEFAULT uuid_generate_v4(), ip varchar, city varchar, country varchar, latitude varchar, longitude varchar, hostname varchar, org varchar, os varchar, dev_type varchar, asn varchar);\n' % TABLE
INSERT_STMT = 'INSERT INTO %s (ip, city, country, latitude, longitude, hostname, org, os, dev_type, asn) \
VALUES (%%s);\n' % TABLE

def getcertificate(obj):
    protocols = obj.get('tags', [])
    certificate = {}
    if 'smtp' in protocols:
        certificate = obj.get('p25', {}).get('smtp', {}).get('starttls', {}).get('tls', {}).get('certificate', {})
    elif 'https' in protocols:
        certificate = obj.get('p443', {}).get('https', {}).get('tls', {}).get('certificate', {})
    elif 'pop3' in protocols:
        certificate = obj.get('p110', {}).get('pop3', {}).get('starttls', {}).get('tls', {}).get('certificate', {})
    elif 'imap' in protocols:
        certificate = obj.get('p143', {}).get('imap', {}).get('starttls', {}).get('tls', {}).get('certificate', {})
    elif 'imaps' in protocols:
        certificate = obj.get('p993', {}).get('imaps', {}).get('tls', {}).get('tls', {}).get('certificate', {})
    elif 'pop3s' in protocols:
        certificate = obj.get('p995', {}).get('pop3s', {}).get('tls', {}).get('tls', {}).get('certificate', {})
    return certificate
    

def getorg(obj):
    certificate = getcertificate(obj)
    organization = ''
    if certificate:
        orglist = certificate.get('parsed', {}).get('subject', {}).get('organization', [])
        organization = orglist[0] if (type(orglist) is list and orglist) else orglist
    if not organization:
        organization = obj.get('autonomous_system', {}).get('organization', '')
    return organization

def gethostname(obj):
    certificate = getcertificate(obj)
    hostname = ''
    if certificate:
         hostlist = certificate.get('parsed', {}).get('extensions', {}).get('subject_alt_name', {}).get('dns_names', [])
         hostname = hostlist[0] if hostlist else ''
    return hostname

with codecs.open('addbigokies.sql', 'w', encoding='utf8') as sqlfile:
    sqlfile.write(DROP_STMT + CREATE_STMT)
    with codecs.open('superinfo.json', 'r', encoding='utf8') as jsonfile:
        for line in jsonfile:
            try:
                obj = json.loads(line)
                field = 'location'
                if obj.get('__restricted_location', {}):
                    field = '__restricted_location'
                if obj.get(field, {}).get('country_code') != '':
                    valuelist = [obj.get('ip'), 
                    obj.get(field, {}).get('city').replace('\'', '\'\''), \
                    obj.get(field, {}).get('country_code'), \
                    str(obj.get(field, {}).get('latitude', '')), \
                    str(obj.get(field, {}).get('longitude', '')), \
                    gethostname(obj).replace('\'', '\'\''), \
                    getorg(obj).replace('\'', '\'\''), \
                    obj.get('metadata', {}).get('os', '').replace('\'', '\'\''), \
                    obj.get('metadata', {}).get('dev_type', '').replace('\'', '\'\''), \
                    str(obj.get('autonomous_system', {}).get('asn', '')) ]
                    valuestring = ', '.join('\'{0}\''.format(a) for a in valuelist)
                    sqlfile.write(INSERT_STMT % valuestring)
            except:
                continue
