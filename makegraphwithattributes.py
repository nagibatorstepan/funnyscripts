import json
import os
import math
import codecs

with open('bigvertices.dot', 'w') as dotfile:
    dotfile.write('graph G{\n')
    for cc in os.listdir('country_ips'):
        countryfile = open('country_ips/' + cc, 'r')
        lines = countryfile.readlines()
        countryfile.close()
        for line in lines:
            dotfile.write('\"%s\" [\"country\"=\"%s\"];\n' % (line[:-1], cc))
    dotfile.write('}')
