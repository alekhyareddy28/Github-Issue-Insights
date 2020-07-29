import csv
import sys
nargs=len(sys.argv)
ofileName='mergedDataset.csv'
with open(ofileName, "wb") as f:
    o=csv.writer(f)
    for i in range(1,nargs):
        with open(sys.argv[i], "rb") as g:
            fi=csv.reader(g)
            o.writerows(fi)