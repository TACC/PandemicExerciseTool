#!/usr/bin/env python3
import pymongo
import json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["PES"]
mycol = mydb["days"]
mycol.drop()


for i in range(100):
    with open(f'output/OUTPUT_{i}.json', 'r') as f:
        mydict = json.load(f)
        mycol.insert_one(mydict)