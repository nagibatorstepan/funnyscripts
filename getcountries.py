import json
countries = []
with open('smallinfo.json', 'r') as f:
   for line in f:
        try:
            obj = json.loads(f)
