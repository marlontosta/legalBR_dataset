from datetime import datetime
from pickle import FALSE
from extract_tokens_lines import Breakpoint, PDFExtractParts
from pymongo import MongoClient
from tqdm import tqdm
import re

RED = '\033[91m'
ENDC = '\033[0m'

corpus = MongoClient().juridico.tjpb_crawler
labeled_corpus = MongoClient().juridico.tjpb_labeled_lines


file = f'/home/juridico/pdfs/tjpb/2011/05/24/00006756820098152001.pdf'
    #GOLD
file = f'/home/juridico/pdfs/tjpb/2012/11/12/07439664820078152001.pdf'
    #GOLD
file = f'/home/juridico/pdfs/tjpb/2013/07/01/00773463020128152001.pdf'
    #decisão (sumula) sem indicativo
file = f'/home/juridico/pdfs/tjpb/2014/03/11/00018699620108150731.pdf'
    #GOLD
file = f'/home/juridico/pdfs/tjpb/2015/05/05/00000872520138150351.pdf'
    #GOLD
file = f'/home/juridico/pdfs/tjpb/2016/02/02/00000195620168150000.pdf'
    #NOME DO DESEMBARGADOR NO RODAPE
file = f'/home/juridico/pdfs/tjpb/2017/07/06/00000691420088150081.pdf'
    #GOLD
file = f'/home/juridico/pdfs/tjpb/2018/08/08/00006624320188150000.pdf'
    #GOLD
file = f'/home/juridico/pdfs/tjpb/2019/09/09/00000775020138150231.pdf'
    #seções misturadas
#file = f'/home/juridico/pdfs/tjpb/2020/02/04/00003615920178150541.pdf'
    #GOLD




#def label_pdf(pdf_file):vvvv

def text_function(field, regex, current_label, expected_label):
    return re.match(regex, field) and (expected_label == current_label or expected_label == '*')

def all_upper(field, regex, current_label, expected_label):
    return field.isupper() and (current_label == expected_label or expected_label == '*')

def coordLess(coord,valor, current_label, expected_label):
    return coord < valor and (current_label == expected_label or expected_label == '*')

def coordMore(coord,valor, current_label, expected_label):
    return coord > valor and (current_label == expected_label or expected_label == '*')

def ignoreCase(field, regex, current_label, expected_label):
    ignorecase = re.compile(regex, re.IGNORECASE)
    return ignorecase.match(field) and (expected_label == current_label or expected_label == '*')

#def gabinete(file):







'''
temp = PDFExtractParts(file)

pdf_file = temp.pdf_pages


temp.new_label_parts(tjpb_breakpoints)

#temp.label_parts(breakpoints=tjpb_gab_benedito_breakpoints)
print(datetime.now())
for page in temp.pdf_pages:
    for line in page['lines']:
        for token in line['tokens']:
            print(token['text'], end = ' ')
        print(f"{RED}{line['section_label']}{ENDC}")#,'\t\t\t', line['line_bbox'], line['tokens'][0]['font'])
'''


filter = {'pdf_file': {'$exists': True}}

file_list = list(corpus.find(filter, {'pdf_file': 1}))


def label_many(file_list):
    for file in file_list:
        try:
            pdf_file = PDFExtractParts(file['pdf_file'])
            pdf_file.new_label_parts(tjpb_breakpoints)
            yield pdf_file.pdf_pages, file['_id']
        except:
            corpus.update_one({'pdf_file': file['pdf_file']},{'$set': {'file_health': 'damaged'}})


for doc, id in tqdm(label_many(file_list), total= len(file_list)):
    #print(id)
    labeled_corpus.insert_one({'process_id': id, 'document': doc})