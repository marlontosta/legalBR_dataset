from datetime import datetime
from pickle import FALSE
from extract_tokens_lines import Breakpoint, PDFExtractParts
from pymongo import MongoClient
from tqdm import tqdm
import re
import numpy as np
from collections import Counter


def printStatistics(TRIBUNAL, SPLIT):
    mongocoll = MongoClient().juridico[TRIBUNAL+'_labeled_lines']

    num_docs = 0 
    num_pages = 0
    num_lines = 0

    doc_labels = []

    if SPLIT == 'train':
        filter = {'$match' : {'dataset':{'$exists': 0}}}
    else:
        filter = {'$match' : {'dataset':SPLIT}}

    for doc in mongocoll.aggregate([filter,{'$project' : 
                                {'page':"$document.lines.section_label"}
                            }]):#,{'$limit' : 5 }]):
        num_docs += 1
        num_pages += len(doc['page'])
        #page_labels = [item for sublist in doc['page'] for item in sublist]
        page_labels = list(map(lambda x: (x if x in ['PARTES','EMENTA','ACORDAO','RELATORIO','VOTO'] else 'OUTROS'), [item for sublist in doc['page'] for item in sublist]))

        #for pages in doc['labels']:
        num_lines += len(page_labels)
        
        doc_labels.append(page_labels)
        

    #doc_labels = 

    print(f'{SPLIT.upper()}\t&\t{num_docs}\t&\t{num_pages}({round(num_pages/num_docs,2)}/documento)\t&\t{num_lines}({round(num_lines/num_pages,2)}/pagina)& \hline')
    #print('Numero de documentos\t', num_docs)
    #print('Numero de páginas\t', num_pages,'\tMédia\t',round(num_pages/num_docs,2), '\tpáginas por documento')
    #print('Numero de linhas\t', num_lines,'\tMédia\t',round(num_lines/num_pages,2), '\tlinhas por página')

    classes = Counter([item for sublist in doc_labels for item in sublist])

    for i in classes:
        #print(i, "\t\t", classes[i], ' ocorrências\t', round(100*(int(classes[i])/num_lines),2),'\n\n')
        print(f'{round(100*(int(classes[i])/num_lines),2)}/{i},')
    print(f'A distribuição das classes no documentos do {TRIBUNAL.upper()} no dataset {SPLIT.upper()}')
    print(f'classes-{TRIBUNAL.lower()}-{SPLIT.lower()}')


for TRIBUNAL in ['tjmg', 'tjpb', 'trf2']:
    for SPLIT in ['trainmini','train', 'validation']:
        print('\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        printStatistics(TRIBUNAL, SPLIT)