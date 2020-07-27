import requests
import gzip
import os
import json
if not os.path.exists('Datasets'):
    os.makedirs('Datasets')
url = 'https://data.gharchive.org/2011-02-12-3.json.gz'
filename = "Datasets/dataset_sample.json.gz"
file_Dataset_Unzipped = "Datasets/dataset_sample.json"
r = requests.get(url)
with open(filename, 'wb') as f:
    f.write(r.content)
handle = gzip.open(filename)
with open(file_Dataset_Unzipped, 'w') as out:
    for line in handle:
        out.write(line)