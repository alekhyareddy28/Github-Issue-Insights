#!/usr/bin/env python
# coding: utf-8

#run from root folder
#usage: python combine.py <archive_stamp> <output_dataset_location>
# In[1]:


import json
import os
import numpy as np
import csv
import sys

# In[2]:


filePath=os.path.abspath('Datasets/'+sys.argv[1]+'.json')


# In[5]:


commitInfoFilePath = filePath[:-5]+".jsoncommMap.csv"


# In[6]:


fileObj = open(filePath,'rb')
data = json.load(fileObj)
combinedL=[]
for event in data:
    try:
        if(event["type"] == "IssuesEvent" and event["payload"]["action"] == "closed"):
            combinedL.append([0,event["payload"]["issue"]])
        if(event["type"] == "PullRequestEvent" and event["payload"]["action"] == "closed"):
            combinedL.append([1,event["payload"]["pull_request"]])
    except:
        pass
fileObj.close()
commitL=dict()
with open(commitInfoFilePath,'r') as fo:
    csvFile = csv.reader(fo)
    for lines in csvFile:
        commitL[int(lines[0])]=[] if lines[1]=='[]' else [y[1:-1] for y in lines[1][1:-1].split(', ')]

# In[13]:


issuePrArr=[]
count=0


# In[14]:

count=0
combinedIndex=0
window=10
for item in combinedL:
    combinedIndex+=1
    if item[0]==1:
        continue
    ev=item[1]
    count+=1
    if count in commitL:
        for commit in commitL[count]:
            j=max(0,combinedIndex-window)
            while j<combinedIndex+window:
                if combinedL[j][0]==1 and combinedL[j][1]["merge_commit_sha"] == commit:
                    issuePrArr.append([ev["title"],ev["body"],','.join([label["name"] for label in ev["labels"]]),combinedL[j][1]["title"],combinedL[j][1]["body"]])
                j+=1


postproc=[]
for ipr in issuePrArr:
    postproc.append([ipr[i].encode('UTF-8').encode('string-escape') for i in range(5)])

f=open(sys.argv[2], "wb")
w = csv.writer(f,quoting=csv.QUOTE_ALL)
for line in postproc:
    w.writerow(line)
f.close()
