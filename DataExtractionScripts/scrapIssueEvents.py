#!/usr/bin/env python
# coding: utf-8

#run from root folder
#usage: python scrapIssueEvents.py <archive_stamp> <path_to_auth_token>
#the auth_token file is a single line with <username>,auth_token
# In[2]:


import json
import os
import sys
import requests
import numpy as np
import csv

# In[90]:


dictResponses={}
filePath=os.path.abspath('Datasets/'+sys.argv[1]+'.json')
combinedList=[]

fileObj = open(filePath,'rb')
data = json.load(fileObj)
for event in data:
    try:
        if(event["type"] == "IssuesEvent" and event["payload"]["action"] == "closed"):
            combinedList.append([0,event["payload"]["issue"]])
        if(event["type"] == "PullRequestEvent" and event["payload"]["action"] == "closed"):
            combinedList.append([1,event["payload"]["pull_request"]])
    except:
        pass
fileObj.close()

issuePrArr=[]
count=0
pattfile=sys.argv[2]
with open(pattfile,'r') as f:
    pat_u,pat_t = f.read().strip().split(",")
for i in combinedList:
    if i[0]==1:
        continue
    ev=i[1]
    count+=1
    if count in dictResponses:
        continue
    r = requests.get(ev["events_url"],auth=(pat_u,pat_t))
    print(str(count) + " " + str(r.status_code))
    if r.status_code == 404:
        dictResponses[count]=[]
    elif(r.status_code==200):
        dictResponses[count]=[]
        for event in json.loads(r.content):
            if("event" in event and event["event"] == "referenced"):
                if(event["commit_id"] is not None):
                    dictResponses[count].append(event["commit_id"])
                    j=max(0,count-10)
                    while j<count+10:
                        if combinedList[j][0]==1 and combinedList[j][1]["merge_commit_sha"] == event["commit_id"]:
                            issuePrArr.append([ev["title"],ev["body"],''.join([label["name"] for label in ev["labels"]]),combinedList[j][1]["title"],combinedList[j][1]["body"]])
                        j+=1
            

with open(filePath+"commMap.csv", "wb") as f:
    w = csv.writer(f)
    for key, val in dictResponses.items():
        w.writerow([key, [x.encode('UTF-8') for x in val]])