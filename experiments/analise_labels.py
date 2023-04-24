from datetime import datetime
from pickle import FALSE
from extract_tokens_lines import Breakpoint, PDFExtractParts
from pymongo import MongoClient
from tqdm import tqdm
import re
from split_dataset import split_docs
from bson.objectid import ObjectId
from argparse import ArgumentParser



RED = '\033[91m'
#RED = '\033[1;41m'
ENDC = '\033[0m'
NONE        = ('\033[1;31m','\033[1;41m')
EMENTA      = ('\033[1;32m','\033[1;42m')
PARTES      = ('\033[1;33m','\033[1;43m')
ACORDAO     = ('\033[1;34m','\033[1;44m')
VOTO        = ('\033[1;35m','\033[1;45m')
RELATORIO   = ('\033[1;36m','\033[1;46m')
SUMULA      = ('\033[1;94m', '\033[1;104m')

DESTAQUE = '\033[1;95m'

COLORS = {
'RED' : '\033[91m',
#'RED' : '\033[1;41m',
'ENDC' : '\033[0m',
'None'        : ('\033[1;31m','\033[1;41m'),
'EMENTA'      : ('\033[1;32m','\033[1;42m'),
'PARTES'      : ('\033[1;33m','\033[1;43m'),
'ACORDAO'     : ('\033[1;34m','\033[1;44m'),
'VOTO'        : ('\033[1;35m','\033[1;45m'),
'RELATORIO'   : ('\033[1;36m','\033[1;46m'),
'SUMULA'      : ('\033[1;94m', '\033[1;104m'),
'CERTIDAO_DE_JULGAMENTO' : ('\033[1;32m','\033[1;42m'),
'AUTUACAO'    : ('\033[1;33m','\033[1;43m'),
'CERTIDAO'    : ('\033[1;34m','\033[1;44m'),
'EXTRATO_DE_ATA' : ('\033[1;32m','\033[1;42m'),

'DESTAQUE' : '\033[1;95m'
}

def main():
    parser = ArgumentParser(
        description='Process pdf documents in corpus.')
        
    parser.add_argument('tribunal', help='Court')
    args = parser.parse_args()

    
    TRIBUNAL = args.tribunal
    mongocoll = MongoClient().juridico[TRIBUNAL+'_labeled_lines']

    #file_list = []
    #file_list.append(list(mongocoll.aggregate([{'$project' : {'process_id': 1, "document.page_number":1,"document.lines.tokens.text":1,"document.lines.section_label":1, "document.lines.x":1, "document.lines.y":1, "document.lines.height":1} }, { '$limit': 1 }])))

    #for documents in file_list:
    #for document in split_docs(TRIBUNAL,'test'):
    for document in mongocoll.find({'dataset':'test'},):
            if 'gold' in document.keys() and document['gold']:
                continue
            #print(document['document'])
            for page in document['document']:
                revisado = False
                while not revisado:
                    print("#################################################################################################################################")
                    print(f"####{DESTAQUE} PROCESSO: {document['process_id']} ### P A G I N A {page['page_number']} {ENDC} ##PDF: {document['pdf_file']}###################################")
                    print("#################################################################################################################################")
                    y = 0
                    for index, line in enumerate(page['lines']):
                        for br in range(int((line['y'] - y)/(line['height']+0.1))-1):
                            #limit gaps between text blocks
                            if(br >= 5): break
                            print("")
                        y = line['y']
                        COLOR = COLORS[line['section_label']]
                        for x in range(int(line['x']/3)):
                            print(' ',end='')

                        for token in line['tokens']:
                            print(f"{COLOR[1]}{token['text']} {ENDC}",end='')
                        print(f"\r{COLOR[0]}{index} {line['section_label']}{ENDC}")
                    
                    rep = str(input('Confira a página e responda:\nA anotação está correta [S/n]: '))
                    if rep.upper() != 'N':
                        revisado = True
                    while rep.upper() == 'N':
                        lin = str(input('informe a linha onde está o erro: '))
                        nlabel = str(input('informe o novo rótulo da linha: '))
                        startLine = int(lin.split('-')[0])
                        if len(lin.split('-')) == 1: stopLine = startLine
                        else: stopLine = int(lin.split('-')[1])
                        print(startLine, stopLine)
                        for clin in range (startLine, stopLine+1):
                            print(clin, page['lines'][clin]['section_label'], '->', nlabel)
                            page['lines'][clin]['section_label'] = nlabel

                        rep = str(input('Fim da edição? [S/n]: '))
            rep = str(input('O documento está totalmente correto? [S/n]: '))
            if rep.strip().upper() != 'N':
                mongocoll.update_one(
                    {
                        '_id': ObjectId(document['_id'])
                    },
                    {
                        "$set": 
                        { 
                            "document": document['document'],
                            "gold": True
                        }
                    })

            print(F'{DESTAQUE}DOCUMENTO FINALIZADO{ENDC}')



if __name__ == "__main__":
    main()