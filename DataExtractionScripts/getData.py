import requests
import gzip
import json
url = 'https://data.gharchive.org/2011-02-12-3.json.gz'
filename = "dataset_sample.json.gz"
file_Dataset_Unzipped = "dataset_sample.json"
r = requests.get(url)
with open(filename, 'wb') as f:
    f.write(r.content)
handle = gzip.open(filename)
with open(file_Dataset_Unzipped, 'w') as out:
    for line in handle:
        out.write(line)