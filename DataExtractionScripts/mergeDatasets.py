import csv
import sys
nargs=len(sys.argv)
ofileName='mergedDataset.csv'
with open(ofileName, "wb") as f:
    o=csv.writer(f,quoting=csv.QUOTE_ALL)
    o.writerow(["IssueTitle","IssueDescription","Label","PrTitle","PrDescription"])
    for i in range(1,nargs):
        with open(sys.argv[i], "rb") as g:
            fi=csv.reader(g,quoting=csv.QUOTE_ALL)
            o.writerows(fi)