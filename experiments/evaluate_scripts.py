import sklearn.metrics as skm
from pymongo import MongoClient
from bson.objectid import ObjectId
from extractparts import label_one



for tribunal in ['stj', 'tjmg', 'tjpb', 'stf', 'trf2']:
    y_true = []
    y_pred = []
    LABELS = ['PARTES','EMENTA','ACORDAO','RELATORIO','VOTO', 'OUTROS']
    print(tribunal.upper())
    mongocoll = MongoClient().juridico[tribunal+'_labeled_lines']
    #get manually labeled files list
    for trib_doc in mongocoll.find({'gold': True}):
        for doc_true, doc_pred in zip(trib_doc['document'], label_one(trib_doc['pdf_file'], tribunal)):
            for lines_true, lines_pred in zip(doc_true['lines'], doc_pred['lines']):
                pred = lines_pred['section_label']
                true = lines_true['section_label']
                if pred not in ['PARTES','EMENTA','ACORDAO','RELATORIO','VOTO']:
                    pred = 'OUTROS'
                if true not in ['PARTES','EMENTA','ACORDAO','RELATORIO','VOTO']:
                    true = 'OUTROS'
                y_true.append(true)
                y_pred.append(pred)
                
                #print(lines_true['section_label'], lines_pred['section_label'])
        #'''

    metrics = {**{
            'accuracy': round(skm.accuracy_score(y_true, y_pred),3),
            'balanced accuracy': round(skm.balanced_accuracy_score(y_true, y_pred),3),
            'precision': round(skm.precision_score(y_true, y_pred, average='weighted'),3),
            'recall': round(skm.recall_score(y_true, y_pred, average='weighted'),3),
            'f1': round(skm.f1_score(y_true, y_pred, average='weighted'),3),
            'f1 micro': round(skm.f1_score(y_true, y_pred, average='micro'),3),
            'f1 macro': round(skm.f1_score(y_true, y_pred, average='macro'),3),
            'cohen kappa': round(skm.cohen_kappa_score(y_true, y_pred),3),
            'matthews' : round(skm.matthews_corrcoef(y_true, y_pred),3)
            },**dict(zip(LABELS, skm.f1_score(y_true, y_pred, average=None)))}



    [print(key,':',round(value,3)) for key, value in metrics.items()]