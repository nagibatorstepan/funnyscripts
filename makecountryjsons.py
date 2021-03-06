import json
import os
import math
import codecs

count=0
filedictionary = {}
if not os.path.isdir('country_ips'):
    os.mkdir('country_ips')
with open('superinfo.json', 'r') as info:
    for line in info:
        try:
            obj = json.loads(line)
            field = 'location'
            if obj.get('__restricted_location', {}):
                field = '__restricted_location'
            if obj[field]['country_code'] != '':
                cc = obj[field]['country_code']
                if not filedictionary.get(cc, {}):
                    print('About to open ' + cc)
                    filedictionary[cc] = open('country_ips/' + cc, 'w')      
                filedictionary[cc].write(line)
                count+=1
        except:
            continue
print('Ended with obj count ' + str(count))
for cc in filedictionary:
    filedictionary[cc].close()

