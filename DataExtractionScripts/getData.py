import requests
import gzip
import os
import json
import sys
#run from root folder
#usage: python getData.py <archive_timestamp>
if not os.path.exists('Datasets'):
    os.makedirs('Datasets')
timestamp = sys.argv[1]
# refer https://www.gharchive.org/ for acceptable timestamp inputs
url = 'https://data.gharchive.org/' + timestamp + '.json.gz'
filename = "Datasets/" + timestamp + ".json.gz"
file_Dataset_Unzipped = "Datasets/" + timestamp + ".json"
r = requests.get(url)
with open(filename, 'wb') as f:
    f.write(r.content)
handle = gzip.open(filename)
with open(file_Dataset_Unzipped, 'w') as out:
    out.write('[')
    for line in handle:
        out.write(line + ',')
    out.write('{}]')