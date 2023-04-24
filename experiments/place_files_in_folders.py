from datetime import date, datetime
from email.mime import base
from pickle import FALSE
from sys import meta_path
from extract_tokens_lines import Breakpoint, PDFExtractParts
from pymongo import MongoClient
from tqdm import tqdm
import re, logging, os
from multiprocessing import Pool


RED = '\033[91m'
ENDC = '\033[0m'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


labeled_corpus = MongoClient().juridico.stj_labeled_lines


#filter = {'pdf_file': {'$exists': True}}
filter = {'pdf_file':{'$regex':'^/home/juridico/pdfs/stj/....(?!/).*$'}}

file_list = list(MongoClient().juridico.stj_crawler.find(filter,{'pdf_file':1}))
#find(filter, {'pdf_file': 1}))

def moveFile(file):
    corpus = MongoClient()
    #######SEPARA OS ARQUIVOS POR DATA EM PASTAS. 
    ##O INTUITO É EVITAR UM GRANDE NUMERO DE ARQUIVOS NO MESMO LOCAL. 
    if os.path.dirname(file['pdf_file']) != '/home/juridico/pdfs/stj':
        return
    
    filename = file['pdf_file'].split('-')
    date_path = filename[0].split('_')
    new_base_path = os.path.join(*date_path)

    if not os.path.exists(new_base_path):
        os.makedirs(new_base_path)

    new_path = (os.path.join(*(new_base_path, '-'.join(filename[1:]))))
    #print(new_path)

    try:
        os.rename(file['pdf_file'], new_path)
        corpus.juridico.stj_crawler.update_one({'pdf_file': file['pdf_file']},{'$set': {'pdf_file': new_path}})
    except:
        try:
            if os.path.exists(new_path):
                corpus.juridico.stj_crawler.update_one({'pdf_file': file['pdf_file']},{'$set': {'pdf_file': new_path}})
        except BaseException as e:
            print(e)
    corpus.close()


with Pool(20) as p:
    p.map(moveFile, file_list)






'''
def label_many(file_list):
    for file in file_list:
        try:
            pdf_file = PDFExtractParts(file['pdf_file'])
            pdf_file.new_label_parts(trf2_breakpoints)
            yield pdf_file.pdf_pages, file['_id']
        except:
            corpus.update_one({'pdf_file': file['pdf_file']},{'$set': {'file_health': 'damaged'}})
        
for doc, id in tqdm(label_many(file_list), total= len(file_list)):
    #print(doc)
    #ins_ids = labeled_corpus.insert_one(
    #                {'process_id': id, 'document': doc})
    continue

'''