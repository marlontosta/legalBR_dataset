from cProfile import label
from datetime import date, datetime
from email.mime import base
from pickle import FALSE
from sys import meta_path
from extract_tokens_lines import Breakpoint, PDFExtractParts
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
import re, logging, os
from multiprocessing import Pool


RED = '\033[91m'
ENDC = '\033[0m'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


labeled_corpus = MongoClient().juridico.stf_labeled_lines

file_list = ['/home/juridico/pdfs/stf/1171430/1171430.pdf']
file_list.append('/home/juridico/pdfs/stf/1171420/1171420.pdf')
for file in labeled_corpus.find():
    file_list.append(file['pdf_file'])

file = f'/home/juridico/pdfs/stf/14/14.pdf'
# file = f'/home/juridico/pdfs/tjmg/2011/09/01/1002410093329000105839202620108130000.pdf'



section_label = None
#def label_pdf(pdf_file):vvvv

def text_function(field, regex, current_label, expected_label):
    return re.match(regex, field) and (expected_label == current_label or expected_label == '*')

def len_text(field, regex, current_label, expected_label):
    return re.match(regex, field) and (expected_label == current_label or expected_label == '*')

def all_upper(field, regex, current_label, expected_label):
    return field.isupper() and re.match(regex, field) and (current_label == expected_label or expected_label == '*')

def coordLess(coord,valor, current_label, expected_label):
    return coord < valor and (current_label == expected_label or expected_label == '*')

def coordMore(coord,valor, current_label, expected_label):
    return coord > valor and (current_label == expected_label or expected_label == '*')

def ignoreCase(field, regex, current_label, expected_label):
    ignorecase = re.compile(regex, re.IGNORECASE)
    return ignorecase.match(field) and (expected_label == current_label or expected_label == '*')

def combine(f1, f2):
    return lambda field, regex, current_label, expected_label : f1(field, regex, current_label, expected_label) and f2(field, regex, current_label, expected_label)


TRIBUNAL = 'stf'
#A ORDEM DOS BREAKPOINTS IMPORTA!!
#trf2_breakpoints = Breakpoint(r'(^[A-Za-z]+ ?: ?[A-Za-z]+*)', label = 'PARTES', function = text_function, single=True, previous_label='None')

stf_breakpoints = Breakpoint(r'^(Supremo Tribunal Federal ?)+$',label='None',function=text_function,single=True)
stf_breakpoints.add(800,field='y',label='None',function=coordMore, single=True)
stf_breakpoints.add(r'^Extrato de Ata - .*',label='None',function=ignoreCase,single=False)
stf_breakpoints.add(5,field='height',label='None',function=coordLess, single=True)
stf_breakpoints.add(70,field='y',label='None',function=coordLess, single=True)
stf_breakpoints.add(103,field='y',label='None',function=coordLess, previous_label='ACORDAO')
stf_breakpoints.add(500,field='x',label='None',function=coordMore, single=True)
#stf_breakpoints.add(r'.* / .*$',label='None', previous_label='None' ,function=text_function,single=True)


stf_breakpoints.add(r'^ ?E? ?M ?E ?N ?T ?A ?(:.*| ?$)',label='EMENTA',function=ignoreCase)
stf_breakpoints.add(r'.+: ?.+', label = 'PARTES', function = text_function, previous_label='None')
stf_breakpoints.add(r'.+: .+', label = 'PARTES', function = text_function, previous_label='PARTES')


stf_breakpoints.add(r'É o relat.rio.',label='None',function=text_function,include_current=False)


#stf_breakpoints.add(r'^((?!:).)*$', label = 'EMENTA', function = all_upper, previous_label='PARTES')

#stf_breakpoints.add(r'^( ?M ?E ?N ?T ?A ?)+$',label='EMENTA',function=text_function)

stf_breakpoints.add(r'^(—? ?R? ?E ?L ?A ?T ?. ?R ?I ?O ?—?(\(\w*\))?)+$',label='RELATORIO',function=ignoreCase)
stf_breakpoints.add(r'^((— )?V? ?O ?T ?O ?:?.*(— )?.*)+',label='VOTO',function=text_function)
stf_breakpoints.add(r'^( ?A ?C ?. ?R ?D ?. ?O ?)+$',label='ACORDAO',function=text_function)
stf_breakpoints.add(r'^(EXTRATO DE ATA ?)+$',label='EXTRATO_DE_ATA',function=text_function)
stf_breakpoints.add(r'.*P.gina \d+ de \d+',label='None',function=text_function,single=True)
#stf_breakpoints.add(r'.*URMA$',label='None',function=text_function,single=True)
stf_breakpoints.add(r'^Inteiro Teor do Acórdão.*$',label='None',function=text_function,single=True)
stf_breakpoints.add(r'^Inteiro Teor do Acórdão.*$',label='None',function=text_function,single=True)





#temp.label_parts(breakpoints=tjpb_gab_benedito_breakpoints)
for file in file_list:
    temp = PDFExtractParts(file)

    pdf_file = temp.pdf_pages

    temp.label_parts(stf_breakpoints)
    print(file)

    #temp.label_parts(breakpoints=tjpb_gab_benedito_breakpoints)

    for page in temp.pdf_pages:
        for line in page['lines']:
            for token in line['tokens']:
                print(token['text'], end = ' ')
            print(f"{RED}{line['section_label']} {line['y']}{ENDC}")#,'\t\t\t', line['line_bbox'], line['tokens'][0]['font'])
        print("\n\n")



exit()

filter = {'pdf_file': {'$exists': True}}

file_list = list(MongoClient()['juridico'][TRIBUNAL+'_crawler'].find({'$or':[{'labeled' : {'$exists' : 0}},{'labeled':0}]},{'pdf_file':1}))

print('Processing ',len(file_list), 'documents')
#find(filter, {'pdf_file': 1}))

def label_one(file):
    mongoconn = MongoClient()
    labeled = mongoconn["juridico"][TRIBUNAL+"_labeled_lines"]
    crawler = mongoconn["juridico"][TRIBUNAL+"_crawler"]
    try:
        pdf_file = PDFExtractParts(file['pdf_file'])
        pdf_file.new_label_parts(stj_breakpoints)
        try:
            labeled.insert_one(
                        {'process_id': file['_id'], 'document': pdf_file.pdf_pages})
            crawler.update_one({'_id': file['_id']},{'$set': {'labeled': 1}})
        except DuplicateKeyError as e:
            mongoconn.close()
            return
        except:
            crawler.update_one({'_id': file['_id']},{'$set': {'file_health': 'damaged'}})
        finally:
            mongoconn.close()
    except:
        crawler.update_one({'_id': file['_id']},{'$set': {'file_health': 'damaged'}})
    finally:
        mongoconn.close()

#with Pool(25) as p:
#    p.map(label_one, file_list)


'''
for file in file_list:
    label_one(file)



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