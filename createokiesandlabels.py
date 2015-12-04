import json
import struct
import os
import re
import codecs
import math

snd = re.compile('p\d+')
ftp_pre = re.compile('^.*220\s*')
ftp_post = re.compile('\s*FTP service ready.*\s*$')
ssh_pre = re.compile('\s+') #SSH-2.0-
ssh_post = re.compile('\s+') #-\r\n

def getservices(obj):
    servicelist = []
    for key in obj:
        if snd.match(key):
            service = ''
            servicesoft = ''
            servicebanner = ''
            if key == 'p21':
                banner = obj[key].get('ftp', {}).get('banner', {})
                service = banner.get('metadata', {}).get('description', '')
                servicebanner = banner.get('banner', '')
                if servicebanner:
                    servicebanner = re.sub(ftp_pre, '', servicebanner)
                    servicebanner = re.sub(ftp_post, '', servicebanner)
            elif key == 'p22':
                banner = obj[key].get('ssh', {}).get('banner', {})
                service = banner.get('metadata', {}).get('description', '')
                servicesoft = banner.get('software_version', '')
                servicebanner = banner.get('raw_banner', '')
            elif key == 'p25':
                banner = obj[key].get('smtp', {}).get('starttls', {})
                service = banner.get('metadata', {}).get('description', '')
                servicebanner = banner.get('banner', '')
            elif key == 'p53':
                service = obj[key].get('dns', {}).get('open_resolver', {}).get('metadata', {}).get('description', '')
            elif key == 'p80':
                banner = obj[key].get('http', {}).get('get', {})
                service = banner.get('metadata', {}).get('description', '')
                servicesoft = banner.get('headers', {}).get('server', '')
                if service.lower().find('apache') > -1 and service.lower().find('httpd') > -1:
                    service = service.replace('httpd', 'http server')
                xpoweredby = banner.get('headers', {}).get('x_powered_by', '')
                if xpoweredby:
                    servicelist.append(xpoweredby)
            elif key == 'p143':
                banner = obj[key].get('imap', {}).get('starttls', {})
                service = banner.get('metadata', {}).get('description', '')
                servicesoft = banner.get('banner', '')
            elif key == 'p443':
                #mnogo voprosov
                banner = obj[key].get('https', {}).get('tls', {})
                service = banner.get('metadata', {}).get('description', '')
            elif key == 'p110':
                banner = obj[key].get('pop3', {}).get('starttls', {})
                service = banner.get('metadata', {}).get('description')
                servicebanner = banner.get('banner', '')
            elif key == 'p502':
                service = obj[key].get('modbus', {}).get('device_id', {}).get('metadata', {}).get('description', '')
            elif key == 'p993':
                banner = obj[key].get('imaps', {}).get('tls', {})
                service = banner.get('metadata', {}).get('description', '')
                servicebanner = banner.get('banner', '')
            elif key == 'p995':
                banner = obj[key].get('pop3s', {}).get('tls', {})
                service = banner.get('metadata', {}).get('description', '')
                servicebanner = banner.get('banner', '')
            elif key == 'p1900':
                banner = obj[key].get('upnp', {}).get('discovery', {})
                service = banner.get('metadata', {}).get('description', '')
                servicebanner = banner.get('server', '')
            elif key == 'p7547':
                banner = obj[key].get('cwmp', {}).get('get', {})
                service = banner.get('metadata', {}).get('description', '')
                servicebanner = banner.get('headers', {}).get('server', '') 
            if service:
                servicelist.append(service)
            elif servicesoft:
                servicelist.append(servicesoft)
            elif servicebanner:
                servicelist.append(servicebanner)            
    return servicelist

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

def fillokiobj(obj):
    okiobj = {}
    field = 'location'
    if obj.get('__restricted_location', {}):
        field = '__restricted_location'
    #if obj[field]['country_code'] != '':
    okiobj['country'] = obj.get(field, {}).get('country', '')
    okiobj['country_code'] = obj.get(field, {}).get('country_code', '')
    okiobj['city'] = obj.get(field, {}).get('city', '')
    okiobj['longitude'] = str(obj.get(field, {}).get('longitude', ''))
    okiobj['latitude'] = str(obj.get(field, {}).get('latitude', ''))
    okiobj['os'] = obj.get('metadata', {}).get('os', '')
    okiobj['dev_type'] = obj.get('metadata', {}).get('device_type', '')
    okiobj['ip'] = obj['ip']
    okiobj['org'] = getorg(obj)
    okiobj['hostname'] = gethostname(obj)
    okiobj['tags'] = obj.get('tags', [])
    okiobj['services'] = getservices(obj)
    okiobj['asn'] = obj.get('autonomous_system', {}).get('asn', '')
    okiobj['heartbleed_vulnerable'] = obj.get('p443', {}).get('https', {}).get('heartbleed', {}).get('heartbleed_vulnerable', False)
    return okiobj

countryfolder = '_country_ips'
outfolder = 'graphinfo'
if not os.path.isdir(outfolder):
    os.mkdir(outfolder)
offset = 0
countrydict = {}
with codecs.open('okiesbig.json', 'w', encoding='utf8') as bigjson:
    biglabel = codecs.open('labels.json', 'w', encoding='utf8')
    biglabel.write('[')
    bigjson.write('[')
    for cc in os.listdir(countryfolder):
        with codecs.open(countryfolder + '/' + cc, 'r', encoding='utf8') as countryfile:
            counter = 0
            labelfile = codecs.open(outfolder + '/' + cc + '_labels.json', 'w', encoding='utf8')
            labelfile.write('[')
            okiesfile = codecs.open(outfolder + '/' + cc + '_okies.json', 'w', encoding='utf8')
            okiesfile.write('[')
            for line in countryfile:
                try:
                    obj = json.loads(line)
                    #fill okiobj
                    okiobj = fillokiobj(obj)
                    #okiobj = line[:-1]
                    okiesfile.write('%s, \n' % json.dumps(okiobj))
                    #bigjson.write(json.dumps(okiobj) + ', \n')
                    bigjson.write('%s, \n' % json.dumps(okiobj))
                    #labelfile.write('\"%s\", ' % okiobj)
                    labelfile.write('\"%s\", ' % obj['ip'])
                    biglabel.write('\"%s\", ' % obj['ip'])
                    counter += 1
                except:
                    continue
            labelfile.write(']')
            labelfile.close()
            okiesfile.write(']')
            okiesfile.close()
            countrydict[cc] = [counter, offset]
            offset += counter
    biglabel.write(']')
    biglabel.close()
    bigjson.write(']')

with open('somekoolfile.json', 'w') as filedict:
    filedict.write(json.dumps(countrydict))
print(len(countrydict))
print(offset)

linklist_layout = []
for i in range(0, offset):
    linklist_layout.append([])
linklist_true = []
for i in range(0, offset):
    linklist_true.append([])
linklist = linklist_layout

def make_complete_graph(linklist, countryvalues):
    for i in range(0, countryvalues[0]):
        for j in range(i+1, countryvalues[0]):
            linklist[i + countryvalues[1]].append(j + countryvalues[1])    


for cc in countrydict:
    total = countrydict[cc][0]
    country_offset = countrydict[cc][1]
    if total > 1:
    # make links for every vertice
        if total < 0:
            make_complete_graph(linklist, countrydict[cc])
        else:
            numlinks = int(total*1.5) + int(10 / total)
            central = int(codecs.encode(os.urandom(4), 'hex'), 16) % total
            for i in range(0, total):
                if i != central:
                    print(offset, country_offset + i)
                    linklist[country_offset + central].append(country_offset + i)                
            for i in range(0, total):
                dst = int(codecs.encode(os.urandom(4), 'hex'), 16) % total                
                if i != central:    
                    if dst == i:
                        dst = (dst+1) % total
                    linklist[country_offset + i].append(country_offset + dst)
                if dst == i:
                    dst = (dst+1) % total
                linklist_true[country_offset + i].append(country_offset + dst)
            for i in range(numlinks):
                src = int(codecs.encode(os.urandom(4), 'hex'), 16) % total
                dst = int(codecs.encode(os.urandom(4), 'hex'), 16) % total
                if src != central:
                    linklist[country_offset + src].append(country_offset + dst)
                if dst == src:
                    dst = (dst+1) % total
                linklist_true[country_offset + src].append(country_offset + dst)
'''            numlinks = int(total*2.5) + int(100 / total)
            for i in range(0, total):
                dst = int(codecs.encode(os.urandom(4), 'hex'), 16) % total
                if dst == i:
                    dst = (dst+1) % total
                linklist_true[country_offset + i].append(country_offset + dst)
            for i in range(numlinks):
                src = int(codecs.encode(os.urandom(4), 'hex'), 16) % total
                dst = int(codecs.encode(os.urandom(4), 'hex'), 16) % total
                linklist_true[country_offset + src].append(country_offset + dst)
'''


def writelinks(linklist, filename):
    with open(filename, 'wb') as linkfile:
        for i in range(offset-1):
            if len(linklist[i]) > 0:
                linkfile.write(struct.pack('<i', (i+1)*(-1)))
                for dest in linklist[i]:
                    linkfile.write(struct.pack('<i', dest+1))

# generate links between countries

allnodes = offset
countrylinks = {}
countrylist = list(key for key in countrydict)
numberoflinks = len(countrylist) * 100
for i in range(0, len(countrylist)):
    cc = countrylist[i]
    countrydict[cc][0] = float(countrydict[cc][0])
    countrylinks[cc] = int(math.ceil(numberoflinks * (countrydict[cc][0] / allnodes)))        
for cc in countrydict:
    print(cc, countrydict[cc][0], countrylinks[cc])
    i = 0
    while i < countrylinks[cc]:
        dst_number = int(codecs.encode(os.urandom(4), 'hex'), 16) % len(countrylist)
        dst_country = countrylist[dst_number]
        if (dst_country == cc or countrylinks[dst_country] < 1) and len(countrylist) != 1:
            continue
        src_vertice = int(int(codecs.encode(os.urandom(4), 'hex'), 16) % countrydict[cc][0]) + countrydict[cc][1]
        dst_vertice = int(int(codecs.encode(os.urandom(4), 'hex'), 16) % countrydict[dst_country][0]) + countrydict[dst_country][1]
        linklist[src_vertice].append(dst_vertice)
        linklist_true[src_vertice].append(dst_vertice)
        #src_line = linecache.getline('__country_ips/' + cc, src_vertice)
        #dst_line = linecache.getline('__country_ips/' + dst_country, dst_vertice)
        #dotfile.write('\"%s\" -> \"%s\";\n' % (src_line[:-1], dst_line[:-1]))
        countrylinks[cc] -= 1
        countrylinks[dst_country] -= 1
        i += 1

print(offset)
writelinks(linklist, 'links.bin')
writelinks(linklist_true, 'links_true.bin')


