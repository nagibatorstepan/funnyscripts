import json
import os
import math
import codecs
import sys

count=0
supadict={}

with codecs.open('smallinfo.json', 'r', encoding='utf8') as info:
    for line in info:
        try:
            obj = json.loads(line)
            okiobj = {}
            if obj['location']['country_code'] != '':
                okiobj['country'] = obj['location']['country']
                okiobj['city'] = obj['location']['city']
                okiobj['longitude'] = str(obj.get('location', {}).get('longitude', ''))
                okiobj['latitude'] = str(obj.get('location', {}).get('latitude', ''))
                #if not obj['metadata']:
                okiobj['os'] = '' 
                okiobj['dev_type'] = ''
                #else:
                okiobj['os'] = obj.get('metadata', {}).get('os', '')
                okiobj['dev_type'] = obj.get('metadata', {}).get('device_type', '')
                okiobj['ip'] = obj['ip']
                okiobj['org'] = obj['autonomous_system']['organization']
                okiobj['hostname'] = ''
                supadict
                supadict[obj['ip']] = okiobj
                #outfile.write(json.dumps(okiobj) + ', ')
                #outlist.write(obj['ip'] + ' ' + obj['location']['country_code'] + '\n')
                count+=1
        except:
            continue
    #outlist.close()
print('Ended with obj count ' + str(count))

with codecs.open('okieslabels.json', 'w', encoding='utf8') as outfile:
    orderfile = codecs.open('labels.json', 'r', encoding='utf8')
    orderlist = json.loads(orderfile.readline())
    orderfile.close()
    outfile.write('[')
    for order_elem in orderlist:
        outfile.write(json.dumps(supadict[order_elem]) + ', \n')
    outfile.write(']')        

