from transformers import TFData2VecVisionForImageClassification
from extract_tokens_lines import PDFExtractParts
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import logging
from multiprocessing import Pool
from bson.objectid import ObjectId

from itertools import repeat


from functools import partial
from argparse import ArgumentParser
import pandas as pd
import json

import breakpoints

RED = '\033[91m'
ENDC = '\033[0m'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def label_all(TRIBUNAL, Threads = 4):
    corpus = MongoClient().juridico[TRIBUNAL+'_labeled_lines']

    filter = {'$and': [{'pdf_file': {'$exists': True}},{'gold':{'$exists':False}}]}
    #############
    #filter = {'$and': [{'pdf_file': {'$exists': True}},{'gold':{'$exists':False}},{'dataset':'test'}]}
    #filter = {'$and': [{'pdf_file': {'$exists': True}},{'dataset':'test'}]}

    file_list = list(corpus.find(filter, {'pdf_file': 1}))

    ##################
    #for file in file_list:
    #    generate_labels(file, TRIBUNAL=TRIBUNAL)
    #return


    with Pool(Threads) as p:
        #p.map(partial(generate_labels, TRIBUNAL=TRIBUNAL),file_list)
        p.starmap(generate_labels, zip(file_list, repeat(TRIBUNAL)))
        #p.map(generate_labels,file_list)
        
def generate_labels(file, TRIBUNAL):
    mongoconn = MongoClient()

    try:
        doc = label_one(file['pdf_file'],TRIBUNAL) 
        ##print(json.dumps(doc[0], sort_keys=False, indent=4))
        mongoconn.juridico[TRIBUNAL+'_labeled_lines'].update_one(
                    {'pdf_file': file['pdf_file']},{'$set': {'document': doc}})

    except:
        mongoconn.juridico[TRIBUNAL+'_crawler'].update_one({'_id': file['_id']},{'$set': {'file_health': 'damaged'}})
    finally:
        mongoconn.close()
        return


def label_one(file, TRIBUNAL):
    mongoconn = MongoClient()
    
    bp=breakpoints.tribunal_breakpoints[TRIBUNAL]
    try:
        pdf_file = PDFExtractParts(file)
        if TRIBUNAL == 'tjmg':
            if (pdf_file.find(r'(É.*o relat.?rio\.?|Pois bem\.|.*dou por relatado.|Conheço do recurso.|.*DECIDO)')):
                bp.add(r'^V.?O.?T.?O ?$', label = 'RELATORIO',function=breakpoints.text_function, include_current=False)
                bp.add(r'(É(,? (\w|\s)*,)? o relatório\.|Pois bem\.|^.*dou por relatado.|^Conheço do recurso.)', label = 'VOTO',function=breakpoints.text_function, include_current=False)
            else:
                bp.add(r'^V.?O.?T.?O$', label = 'VOTO',function=breakpoints.text_function)
                
        pdf_file.label_parts(bp)
    except:
        mongoconn.juridico[TRIBUNAL+'_crawler'].update_one({'pdf_file': file},{'$set': {'file_health': 'damaged'}})
    finally:
        mongoconn.close()
        return pdf_file.pdf_pages



def label_many(file_list, TRIBUNAL):
    breakpoints=breakpoints.tribunal_breakpoints[TRIBUNAL]
    for file in file_list:
        try:
            pdf_file = PDFExtractParts(file['pdf_file'])
            pdf_file.label_parts(breakpoints)
            yield pdf_file.pdf_pages, file['_id']
        except:
            MongoClient().juridico[TRIBUNAL+'_crawler'].update_one({'pdf_file': file['pdf_file']},{'$set': {'file_health': 'damaged'}})
        


def main():
    parser = ArgumentParser(
        description='Process pdf documents in corpus.')
    
    parser.add_argument('tribunal', help='Court')
    parser.add_argument('threads', help='Threads')
    args = parser.parse_args()

    print(args)
    label_all(args.tribunal,int(args.threads))

def test(file, tribunal):
    temp = PDFExtractParts(file)

    pdf_file = temp.pdf_pages

    temp.label_parts(breakpoints=breakpoints.tribunal_breakpoints[tribunal])
    print(file)

    #temp.label_parts(breakpoints=tjpb_gab_benedito_breakpoints)

    for page in temp.pdf_pages:
        for line in page['lines']:
            for token in line['tokens']:
                print(token['text'], end = ' ')
            print(f"{RED}{line['section_label']} {line['y']}{ENDC}")#,'\t\t\t', line['line_bbox'], line['tokens'][0]['font'])
        print("\n\n")

if __name__ == "__main__":
    main()
    #test('/home/juridico/pdfs/trf2/2017/03/10/00067956820164020000.pdf', 'trf2')