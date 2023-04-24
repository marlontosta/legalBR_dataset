from multiprocessing import Pool
import os
import datasets
import pandas as pd
from pymongo import MongoClient
import collections

tribunal = 'stj'



mongocoll = MongoClient().juridico[tribunal+'_labeled_lines']
filter = {'$and':[{'repetido':{'$exists': 0}},{'dataset':{'$exists': 0}}]}


lista = list(mongocoll.find(filter).limit(400))
i = 0
for doc_dev in lista:
    i += 1
    mongocoll.update_one({'_id': doc_dev['_id']},{'$set':{'dataset': 'validation'}})
print(i)