from pymongo import MongoClient
from bson.objectid import ObjectId

#'trf2', 'stf', 'tjpb', 'tjmg'
for tribunal in ['trf2']:
    mongocoll = MongoClient().juridico[tribunal+'_labeled_lines']
    
    filter = {'$or':[{'dataset':'test'},{'dataset':'dev'},{'dataset':'validation'}]}
    fixed_list = [pdf_file['pdf_file'] for pdf_file in list(mongocoll.find(filter,{'pdf_file':1}))]#lista dev, test, val
    docs = []
    cont = 0
    for item in mongocoll.find({'$and':[{'dataset':{'$ne':'dev'}},{'dataset':{'$ne':'test'}}]},{'pdf_file':1}):
        print('.', end='')
        if item['pdf_file'] in fixed_list:
            #print('remover esse',end='')
            cont+=1
            mongocoll.update_one({'_id':item['_id']},{'$set': {'repetido': True}})
            continue
        else:
            docs.append(item['pdf_file'])
    print(tribunal, cont, len(docs))