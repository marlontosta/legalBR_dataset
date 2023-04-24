from multiprocessing import Pool
import os
import datasets
from numpy import save
import pandas as pd
from pymongo import MongoClient
import collections
OUTPUT_DIR = 'dataset'


def prepare_datasets(path: str):
    df_train = pd.read_csv(os.path.join(path, 'train.tsv'), sep="\t", usecols=(1, 2))
    df_validation = pd.read_csv(os.path.join(path, 'dev.tsv'), sep="\t", usecols=(1, 2))
    df_test = pd.read_csv(os.path.join(path, 'test.tsv'), sep="\t", usecols=(1, 2))
    df_train['labels'] = df_train['labels'].apply(int)
    df_test['labels'] = df_test['labels'].apply(int)
    df_validation['labels'] = df_validation['labels'].apply(int)
    return df_train, df_validation, df_test


filter = {'dataset': 'trainmini'}
def lines_to_text(line):
        line_text = ''
        for token in line['tokens']:
            line_text += (token['text'])+' '

        return line_text.strip()

LABELS = {
    "None": 0,
    "PARTES": 1,
    "EMENTA": 2,
    "ACORDAO": 3,
    "RELATORIO": 4,
    "VOTO": 5,
    "SUMULA": 6,
    "CERTIDAO_DE_JULGAMENTO" : 7,
    "AUTUACAO" : 8,
    "CERTIDAO": 9
}

def get_lines_all_courts(tribunais, split='trainmini', limit=0):
    for tribunal in tribunais:
        yield from get_lines(tribunal, split, limit)

def get_docs_all_courts(tribunais, split='trainmini', limit=0):
    for tribunal in tribunais:
        print(tribunal, split)
        yield from get_docs(tribunal, split, limit)

def get_lines(tribunal, split, limit=0):
    mongocoll = MongoClient().juridico[tribunal+'_labeled_lines']
    filter = {
        'trainmini' : {'dataset':'trainmini'},
        'train' : {'$or':[{'dataset':'train'}, {'dataset':'trainmini'},{'dataset':{'$exists':False}}]},
        'validation' : {'dataset':'validation'},
        'test' : {'dataset':'test'},
        'dev' : {'dataset' : 'dev'}
    }
    for doc in mongocoll.find(filter[split],{'process_id' : 0,
            #'document.page_number': 1,
            'document.lines.tokens.width' : 0,
            'document.lines.tokens.y' : 0,
            'document.lines.tokens.x' : 0,
            'document.lines.tokens.height' : 0,
            'document.lines.tokens.font' : 0,
            'document.lines.tokens.size' : 0,
            #'document.lines.width' : 1,
            #'document.lines.y' : 1,
            #'document.lines.x' : 1,
            #'document.lines.size' : 1,
            #'document.lines.height' : 1,
            'gold' :0,
            'dataset' :0}).limit(limit):

        for lines in doc['document']:
            page_num = lines['page_number']
            for line in lines['lines']:
                text_line = lines_to_text(line)
                yield text_line, line['x'], line['width'], line['y'], line['height'], page_num, line['section_label']
                #{ "x" : 56, "width" : 482.99975999999947, "y" : 182.77800000000002, "height" : 14,


def get_docs(tribunal, split, limit=0):
    mongocoll = MongoClient().juridico[tribunal+'_labeled_lines']
    filter = {
        'trainmini' : {'dataset':'trainmini'},
        'train' : {'$or':[{'dataset':'train'}, {'dataset':'trainmini'},{'dataset':{'$exists':False}}]},
        'validation' : {'dataset':'validation'},
        'test' : {'dataset':'test'},
        'dev' : {'dataset':'dev'}
    }
    for doc in mongocoll.find(filter[split],{'process_id' : 0,
            'document.lines.tokens.width' : 0,
            'document.lines.tokens.y' : 0,
            'document.lines.tokens.x' : 0,
            'document.lines.tokens.height' : 0,
            'document.lines.tokens.font' : 0,
            'document.lines.tokens.size' : 0,
            'gold' :0,
            'dataset' :0}).limit(limit):
        doc_lines = []  
        for page in doc['document']:
            page_num = page['page_number']

            
            for line in page['lines']:
                text_line = lines_to_text(line)
                doc_lines.append((text_line, line['x'], line['width'], line['y'], line['height'], page_num, line['section_label']))
        yield doc_lines, doc['pdf_file']


if __name__ == "__main__":        
        
    for dataset_name in ['train']:
        
        
        '''for doc in get_docs_all_courts(['tjmg','tjpb','trf2','stj'], dataset_name, 0):
            dataset = doc[0]
            df = pd.DataFrame(dataset, columns=['text', 'x', 'width', 'y', 'height', 'page', 'label'])
            output_file = os.path.join(os.path.dirname(os.path.abspath(doc[1])), f'{prefix}-{os.path.splitext(os.path.basename(doc[1]))}.tsv'.format(string))
            df.to_csv(output_file, sep='\t')'''

            
        def save_tsv(doc):
            pdf_lines = doc[0]
            file_path = doc[1].replace('/juridico/pdfs/','/juridico/dataset/'+dataset_name+'/')
            df = pd.DataFrame(pdf_lines, columns=['text', 'x', 'width', 'y', 'height', 'page', 'label'])
            output_file = os.path.join(os.path.dirname(os.path.abspath(file_path)), f'{os.path.splitext(os.path.basename(doc[1]))[0]}.tsv'.format(dataset_name))
            
            if os.path.exists(output_file):
                return#'''
            try:
                os.makedirs(os.path.dirname(output_file))
            except FileExistsError:
                df.to_csv(output_file, sep='\t')
                return
            df.to_csv(output_file, sep='\t')

        
        for tribunal in ['stj']:
            for doc in get_docs(tribunal, dataset_name, limit=0):
                save_tsv(doc)
                

            '''with Pool(25) as p:
            p.map(save_tsv, doc_list)#'''


            '''doc_list = list(get_docs_all_courts([tribunal], dataset_name, limit=0))
            with Pool(20) as p:
                p.map(save_tsv, doc_list)#'''
        
        '''#doc_list = list(get_docs_all_courts(['stj'], 'test', 0))
        for doc in get_docs_all_courts(['tjmg','stf','tjpb','trf2','stj'], dataset_name, 0):
            save_tsv(doc)#'''

    '''dataset_name = 'train'
    doc_list = list(get_docs_all_courts(['tjpb'], dataset_name, limit=0))
    with Pool(20) as p:
        p.map(save_tsv, doc_list) #'''

    '''with Pool(20) as p:
        p.map(save_tsv, list(get_docs_all_courts(['tjpb', 'trf2','stj'], dataset_name, limit=limit))) #'''


    print('All documents were downloaded successfully')
