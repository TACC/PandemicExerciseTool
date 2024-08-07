#!/usr/bin/env python3
import pymongo
import json
import sys

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["PES"]
mycol = mydb["days"]


myquery = {'day': int(sys.argv[1])}
mydoc = mycol.find(myquery)
for x in mydoc:
    print(x)