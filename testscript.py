import json
import os
import math
import codecs

count=0
supadict=[]
with open('superinfo.json', 'r') as info:
    for line in info:
        try:
            obj = json.loads(line)
            field = 'location'
            if obj.get('__restricted_location', {}):
                field = '__restricted_location'
            if obj[field]['country_code'] != '':
                supadict.append((obj['ip'], obj[field]['country_code']))
                #outlist.write(obj['ip'] + ' ' + obj['location']['country_code'] + '\n')
                count+=1
        except:
            continue
    #outlist.close()
print('Ended with obj count ' + str(count))
supadict = sorted(supadict, key=lambda elem: elem[1])
print(supadict[0])
countryvar = supadict[0][1]
countryfile = open('country_ips/' + countryvar, 'w')
for elem in supadict:
    if countryvar != elem[1]:
        countryfile.close()
        countryvar = elem[1]
        countryfile = open('country_ips/' + countryvar, 'w')
    countryfile.write(elem[0] + '\n')
countryfile.close()

with open('superbigrandom.dot', 'w') as dotfile:
    for f in os.listdir('country_ips'):
        countryfile = open('country_ips/' + f, 'r')
        lines = countryfile.readlines()
        countryfile.close()
        numlinks = int(len(lines)*1.46)
        countrylinks = []
        for i in range(numlinks):
            src = int(codecs.encode(os.urandom(4), 'hex'), 16) % len(lines)
            dst = int(codecs.encode(os.urandom(4), 'hex'), 16) % len(lines)
            countrylinks.append((src, dst))
        unique = set(countrylinks)
        for item in unique:
            dotfile.write('\"%s\" -> \"%s\";\n' % (lines[item[0]][:-1], lines[item[1]][:-1]))


with open('superbigrandom.dot', 'a') as dotfile:
    countries = os.listdir('country_ips')
    for i in range(int(len(countries)*100)):
        src_country = int(codecs.encode(os.urandom(4), 'hex'), 16) % len(countries)
        dst_country = int(codecs.encode(os.urandom(4), 'hex'), 16) % len(countries)       
        if dst_country == src_country:
            dst_country = int(codecs.encode(os.urandom(4), 'hex'), 16) % len(countries)
        src_file = open('country_ips/' + countries[src_country], 'r')
        src_lines = src_file.readlines()
        src_file.close()
        dst_file = open('country_ips/' + countries[dst_country], 'r')
        dst_lines = dst_file.readlines()
        dst_file.close()
        src = int(codecs.encode(os.urandom(4), 'hex'), 16) % len(src_lines)
        dst = int(codecs.encode(os.urandom(4), 'hex'), 16) % len(dst_lines)
        dotfile.write('\"%s\" -> \"%s\";\n' % (src_lines[src][:-1], dst_lines[dst][:-1]))                        

