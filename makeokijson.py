import json
import os
import math
import codecs
import sys

count=0
#supadict=[]
outfile = codecs.open('kindaokies.json', 'w', encoding='utf8')
outfile.write('[')
with codecs.open('smallinfo.json', 'r', encoding='utf8') as info:
    for line in info:
        try:
            obj = json.loads(line)
            okiobj = {}
            if obj['location']['country_code'] != '':
                okiobj['country'] = obj['location']['country']
                okiobj['city'] = obj['location']['city']
                okiobj['longitude'] = str(obj['location']['longitude']) if obj['location']['longitude'] else ''
                okiobj['latitude'] = str(obj['location']['latitude']) if obj['location']['latitude'] else ''
                #if not obj['metadata']:
                okiobj['os'] = '' 
                okiobj['dev_type'] = ''
                #else:
                okiobj['os'] = obj['metadata']['os'] #obj.get('metadata', {}).get('os', '')
                okiobj['dev_type'] = obj['metadata']['device_type']#obj.get('metadata', {}).get('device_type', '')
                okiobj['ip'] = obj['ip']
                okiobj['org'] = obj['autonomous_system']['organization']
                okiobj['hostname'] = ''
               # supadict.append(okiobj)
                outfile.write(json.dumps(okiobj) + ', ')
                #outlist.write(obj['ip'] + ' ' + obj['location']['country_code'] + '\n')
                count+=1
        except:
            continue
outfile.write(']')
outfile.close()
    #outlist.close()
print('Ended with obj count ' + str(count))
