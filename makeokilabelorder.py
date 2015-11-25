import json
import os
import math
import codecs
import sys

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


count=0
linecount=0
supadict={}



with codecs.open('mediuminfo.json', 'r', encoding='utf8') as info:
    for line in info:
        linecount += 1
        try:
            obj = json.loads(line)
            okiobj = {}
            field = 'location'
            if obj.get('__restricted_location', {}):
                field = '__restricted_location'
            #if obj[field]['country_code'] != '':
            okiobj['country'] = obj.get(field, {}).get('country', '')
            okiobj['city'] = obj.get(field, {}).get('city', '')
            okiobj['longitude'] = str(obj.get(field, {}).get('longitude', ''))
            okiobj['latitude'] = str(obj.get(field, {}).get('latitude', ''))
            okiobj['os'] = obj.get('metadata', {}).get('os', '')
            okiobj['dev_type'] = obj.get('metadata', {}).get('device_type', '')
            okiobj['ip'] = obj['ip']
            okiobj['org'] = getorg(obj)
            okiobj['hostname'] = gethostname(obj)
            okiobj['tags'] = obj.get('tags', [])
            supadict[obj['ip']] = okiobj
            #outfile.write(json.dumps(okiobj) + ', ')
            #outlist.write(obj['ip'] + ' ' + obj['location']['country_code'] + '\n')
            count+=1
        except:
            print(linecount)
            print(sys.exc_info())
            continue
    #outlist.close()
print('Ended with obj count ' + str(count))

with codecs.open('okieslabels.json', 'w', encoding='utf8') as outfile:
    orderfile = codecs.open('labels.json', 'r', encoding='utf8')
    orderlist = json.loads(orderfile.readline())
    orderfile.close()
    outfile.write('[')
    for order_elem in orderlist:
        outfile.write(json.dumps(supadict.get(order_elem, {'ip': order_elem})) + ', \n')
    outfile.write(']')        

