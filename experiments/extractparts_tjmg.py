from datetime import datetime
from distutils import text_file
from pickle import FALSE

from scipy.fftpack import idct
from extract_tokens_lines import Breakpoint, PDFExtractParts
from pymongo import MongoClient
from tqdm import tqdm

import re

#file = f'/home/juridico/pdfs/tjmg/2011/10/20/1000210000528500100052858220108130002.pdf' 
    #partes single
    #notas taquigráficas
    #sem indicativo de relatório

#file = f'/home/juridico/pdfs/tjmg/2013/01/07/1000011085391800108539186320118130000.pdf'
    #gold

#file = f'/home/juridico/pdfs/tjmg/2013/01/07/.pdf'
    #bom, mas não é golden
    #notas taquigráficas

#file = f'/home/juridico/pdfs/tjmg/2014/01/07/1002411004460900100446097620118130024.pdf'
    #gold

#ile = f'/home/juridico/pdfs/tjmg/2015/12/16/1000014043328500004332859120148130000.pdf'
    #gold

#file = f'/home/juridico/pdfs/tjmg/2016/11/01/1000016070222100161421169020158130024.pdf'
    #gold

#file = f'/home/juridico/pdfs/tjmg/2017/01/01/1000016039084500003908451220168130000.pdf'
    #partes single
    #relatorio confund-se com os votos

#file = f'/home/juridico/pdfs/tjmg/2018/06/06/1000015083851400260098507620148130024.pdf'
    #ementa após o voto - verificar nos outros
    #arquivo tem voto vencido - bom para testes
    #gold

#file = f'/home/juridico/pdfs/tjmg/2019/04/04/1000016069245500400435132020198130000.pdf'
    #possui ementa do voto
    #partes single - ok
    #gold

#file = f'/home/juridico/pdfs/tjmg/2020/05/05/1000017039183300313612781120198130000.pdf' #1 linha
    #gold

file = f'/home/juridico/pdfs/tjmg/2021/10/13/1000020479190900310810887420218130000.pdf' #1 linha
    #GOLD

corpus = MongoClient().juridico.tjmg_crawler
labeled_corpus = MongoClient().juridico.tjmg_labeled_lines

section_label = None
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



'''tjpb_breakpoint = Breakpoint(r'(^PODER JUDICI.RIO$)', text_function, single=True)
#bp_teste.add(86,label='CABECALHO',function=cabecalho,single=True,field='y0')
#bp_teste.add(774,label='RODAPE',function=rodape,single=True,field='y1')
tjpb_breakpoint.add(r'^(?!.*OAB).*n\.*º* \d+.*\d+$',ignoreCase,single=True)
tjpb_breakpoint.add(r'^_+$',single=True,function=text_function)
tjpb_breakpoint.add(r'^Relator.?:.*$',label='PARTES',function=text_function,previous_label=None)
tjpb_breakpoint.add(r'^[A-Z]+ ?:.*$',label='PARTES',function=text_function, previous_label=None)
tjpb_breakpoint.add(r'^Vistos.?,.*$',label='ACORDAO',function=ignoreCase, previous_label='EMENTA')
#bp_teste.add(r'^VISTOS.?,.*$',label='ACORDAO',function=text_function, previous_label='EMENTA')
tjpb_breakpoint.add(r'^—? ?RELAT.RIO ?—?$',label='RELATORIO',function=text_function, previous_label='ACORDAO')
tjpb_breakpoint.add(r'V O T O$',label='VOTO',function=text_function, previous_label='RELATORIO')
tjpb_breakpoint.add(r'^(— )?VOTO:?.*(— )?$',label='VOTO',function=text_function, previous_label='RELATORIO')
tjpb_breakpoint.add(r'^.*$',label='EMENTA',function=all_upper, previous_label='PARTES')
tjpb_breakpoint.add(r'^É como voto.?$',label='NAO SEI',function=text_function, previous_label='VOTO',include_current=False)
tjpb_breakpoint.add(r'^\d\d?\d?$',label='None',function=text_function, single=True)'''




 



def adjust_breakpoints(pdf_file):

    

    #tjmg_breakpoint.add(r'.*',label='EMENTA',function=all_upper, previous_label='None')
    



print(datetime.now())


RED = '\033[91m'
ENDC = '\033[0m'
    





temp = PDFExtractParts(file)
temp.new_label_parts(adjust_breakpoints(file))



filter = {'pdf_file': {'$exists': True}}

file_list = list(corpus.find(filter, {'pdf_file': 1}))

def label_many(file_list):
    for file in file_list:
        try:
            pdf_file = PDFExtractParts(file['pdf_file'])
            tjmg_breakpoint = adjust_breakpoints(pdf_file)
            pdf_file.new_label_parts(tjmg_breakpoint)
            yield pdf_file.pdf_pages, file['_id']
        except:
            corpus.update_one({'pdf_file': file['pdf_file']},{'$set': {'file_health': 'damaged'}})

#label_many(file_list)
for doc, id in tqdm(label_many(file_list), total= len(file_list)):
    print(id)
    #ins_ids = labeled_corpus.insert_one(
                   #{'proccess_id': id, 'document': doc})

    #ins_ids = labeled_corpus.findOneAndUpdate(
    #    {'process_id': id, '$or': [{'gold' : False}, {'gold':{'$exists':False}}]},{'document': doc})