import os
from os import close
import pdfplumber
from pdfminer.layout import LAParams, LTContainer, LTText, LTTextBoxHorizontal, LTTextLineHorizontal
from pdfminer.high_level import extract_pages
from decimal import Decimal
import re
import json
from snorkel.labeling import labeling_function
import pandas as pd


file = '/home/marlon/DireitoDigital/PDF/STJ/stj_20210329.pdf'


#print(pages_miner)
def busca_texto(json_data, bbox, page_number):
    for page in json_data:
        if(page["pdf_data"]["page"]!= page_number):
            continue
        for line in page["text_lines_horizontal"]:
            #print(line)
            if(line["bbox"] == bbox):
                return line
# ID; regex para identificar a palavra na linha; regex para palavra no meio do texto


def json_trf2(pdf):
    regexSecoes = [["EMENTA", re.compile("e\s*m\s*e\s*n\s*t\s*a"), re.compile("((?<=\n)e\s*m\s*e\s*n\s*t\s*a(?=\s*:|\n))")],
               ["ACÓRDÃO", re.compile("a\s*c\s*ó\s*r\s*d\s*ã\s*o"), re.compile("((?<=\n)a\s*c\s*ó\s*r\s*d\s*ã\s*o(?=\s*:|\n))")],
               ["VOTO", re.compile("v\s*o\s*t\s*o"), re.compile("((?<=\n)v\s*o\s*t\s*o(?=\s*:|\n))")],
               ["RELATÓRIO", re.compile("r\s*e\s*l\s*a\s*t\s*ó\s*r\s*i\s*o"), re.compile("((?<=\n)r\s*e\s*l\s*a\s*t\s*ó\s*r\s*i\s*o(?=\s*:|\n))")]]

    pages_miner = list(extract_pages(pdf, laparams=LAParams(all_texts=True)))
    texto = "" # Variável que acumula os textos de cada seção para serem extraídos.
    partesText = [] # Lista que recebe as diferentes partes da seção PARTES, buscando evitar que trechos de seu texto acabe em outras seções. Quando um novo loop "for" é executado, caso o valor da variável e_txt conste na lista, o loop atual é interrompido e um próximo e_txt é avaliado.
    cur_sec = "PARTES"
    partesMark = 0 # Marcador que identifica se a seção PARTES já foi completamente identificada. Quando se muda para outra seção, partesMark recebe o valor 1. Enquanto o valor da variável for 0, a lista "partesText" armazenará os conjuntos de textos que forem surgindo.
    json_data = []
    for pdf_page in pages_miner:
        page = {"file_name":pdf.split('/')[-1], "page":pdf_page.pageid}
        text_lines_horizontal = []
        # elementos selecionados para serem coloridos
        labeled_elements = []
        #for obj in box:
        for i_e, e in enumerate(pdf_page):
          #print(type(e))
          if isinstance(e, LTTextBoxHorizontal):
            if e.y0 > 780:
                # cabeçalho
                for line in e:
                  if isinstance(line, LTTextLineHorizontal):
                    linha = {"bbox":[line.x0,line.y0,line.x1,line.y1],"text":line.get_text(), "section_label":None}
                    text_lines_horizontal.append(linha)
                continue

            if e.y1 < 70:
                # rodapé
                for line in e:
                  if isinstance(line, LTTextLineHorizontal):
                    linha = {"bbox":[line.x0,line.y0,line.x1,line.y1],"text":line.get_text(), "section_label":None}
                    text_lines_horizontal.append(linha)
                continue
            
            # clean text
            e_txt = e.get_text().lower().strip()
            if partesMark == 1:
                if e_txt in partesText:
                    continue
            markBreak = 0 # Marcador que impede que um conjunto de texto seja integralmente adicionado à variável "texto" caso se conste que o conjunto de textos possui mais de uma seção dentro dele            
                
            for ident, linha, palavra in regexSecoes:
                
              # divide o trecho de texto que possua mais de uma seção dentro dele em subtextos
              if re.search(palavra, e_txt):                 
                temp = palavra.split(e_txt)                    
                for item in temp:                        
                  #print("\n###\n")
                  #print("Subconjunto de texto >>\n", item)
                  #print("\n###\n")
                  if re.match(linha, item):
                    for line in e:
                      linha = {"bbox":[line.x0,line.y0,line.x1,line.y1],"text":line.get_text(), "section_label":cur_sec}
                      text_lines_horizontal.append(linha)
                    '''with open("{}_{}.txt".format(pdf, cur_sec), "w") as text_file:
                        text_file.write(texto)           '''
                    texto = "" # "reset" da variável após a extração
                    cur_sec = ident                            
                    partesMark = 1
                    #print("Texto da seção PARTES: ", partesText)
                    #markBreak = print("Page: "+str(i_page)+" E_type: "+str(type(e)))
                  if partesMark == 0:
                    partesText.append(item)
                  texto = texto + item                          

              else:                
                  if re.match(linha, e_txt):   
                    for line in e:
                      linha = {"bbox":[line.x0,line.y0,line.x1,line.y1],"text":line.get_text(), "section_label":cur_sec}
                      text_lines_horizontal.append(linha)
                      #with open("{}_{}.txt".format(pdf, cur_sec), "w") as text_file:
                          #text_file.write(texto)           
                      #print("Versão final da seção {} >>\n".format(cur_sec), texto)
                      texto = "" # "reset" da variável após a extração
                      cur_sec = ident
                      partesMark = 1
                      #print("Texto da seção PARTES: ", partesText)
                  if partesMark == 0:
                              partesText.append(e_txt)
   
              for obj in e:
                #print(type(obj))
                linha = {"bbox":[obj.x0,obj.y0,obj.x1,obj.y1],"text":obj.get_text(), "section_label":cur_sec}
                text_lines_horizontal.append(linha)
          json_data.append({"pdf_data": page, "text_lines_horizontal": text_lines_horizontal})
    return json_data
        



#cria json com atributos e rotulos
def json_stj(file_path, titulos = ["partes", "relatório", "ementa", "voto", "acórdão", "termo de julgamento", "autuação", "embargos de declaração", "termo", "certidão", "certidão de julgamento"]):
    pages_miner = list(extract_pages(file_path, laparams=LAParams(all_texts=True)))

    pdf_page = {}
    partes = []
    titulo = ""
    parte = ""
    json_data = []
    for page in pages_miner:
        pdf_page = {"file_name":file.split('/')[-1], "page":page.pageid}
        text_lines_horizontal = []
        for box in page:
            if isinstance(box, LTTextBoxHorizontal):
                for obj in box:
                    if isinstance(obj, LTTextLineHorizontal):
                        #print(obj.get_text().lower().strip())
                        if obj.y1 < 77 or obj.get_text().strip() == '':
                            linha = {"bbox":[obj.x0,obj.y0,obj.x1,obj.y1],"text":obj.get_text(), "section_label":None}
                            text_lines_horizontal.append(linha)
                            break
                        if(obj.get_text().lower().strip() in titulos or re.search("\w*.*Nº \d+\.*\d*\.*\d* - \w\w.*", obj.get_text())):
                            partes.append((titulo,parte))
                            titulo = str(obj.get_text().upper().strip())
                            if(re.search("\w*.*Nº \d+\.*\d*\.*\d* - \w\w.*", obj.get_text())):
                                titulo = "PARTES"
                                linha = {"bbox":[obj.x0,obj.y0,obj.x1,obj.y1],"text":obj.get_text(), "section_label":None}
                                text_lines_horizontal.append(linha)
                                continue
                            parte = ""
                            #print(titulo)
                            #i += 1
                        obj.section_label = titulo
                        #print(obj.x0, obj.y0, obj.x1, obj.y1, obj.get_text(), obj.section_label)
                        linha = {"bbox":[obj.x0,obj.y0,obj.x1,obj.y1],"text":str(obj.get_text()), "section_label":obj.section_label}
                        text_lines_horizontal.append(linha)
        json_data.append({"pdf_data": pdf_page, "text_lines_horizontal": text_lines_horizontal})
    return json_data

def cria_dataset_nao_anotado(pdf_path):
    dataset = pd.DataFrame(columns=["file_name", "x0", "y0", "x1", "y1", "text", "page" ])
    for file in os.listdir(pdf_path):
        if file.endswith(".pdf"):
            pages_miner = list(extract_pages(pdf_path+ '/' + file, laparams=LAParams(all_texts=True)))
            for page in pages_miner:
                for box in page:
                    if isinstance(box, LTTextBoxHorizontal):
                        for obj in box:
                            if isinstance(obj, LTTextLineHorizontal):
                                line = [file, obj.x0,obj.y0,obj.x1,obj.y1, obj.get_text(),page.pageid]
                                df_length = len(dataset)
                                dataset.loc[df_length] = line
                                #dataset.append(line)
    return dataset

'''
json_data = json_stj(file)
with open(os.path.splitext(file)[0] + ".json", 'w') as j:
    json.dump(json_data, j, sort_keys = True, indent = 4,ensure_ascii = False)

file = '/home/marlon/DireitoDigital/PDF/STJ/stj_20191011.pdf'
json_data = json_stj(file)
with open(os.path.splitext(file)[0] + ".json", 'w') as j:
    json.dump(json_data, j, sort_keys = True, indent = 4,ensure_ascii = False)
'''

ABSTAIN = -1
PARTES = 0
RELATORIO = 1
EMENTA = 2
VOTO = 3
ACORDAO = 4
TERMO_DE_JULGAMENTO = 5
AUTUACAO = 6
EMBARGOS_DE_DECLARACAO = 7
TERMO = 8
CERTIDAO = 9
CERTIDAO_DE_JULGAMENTO = 10

file_path = '/home/marlon/DireitoDigital/PDF/STJ'


@labeling_function()
def lf_label_stj(x):
    #print(x)
    bbox = [x["x0"],x["y0"],x["x1"],x["y1"]]
    
    line = busca_texto(json_stj(file_path+"/"+x["file_name"]), bbox, x["page"])
    #print(line)
    if line is None:
        return ABSTAIN
    else:
        if(line["section_label"] is not None):
            #print(line["section_label"])
            return ["partes", "relatório", "ementa", "voto", "acórdão", "termo de julgamento", "autuação", "embargos de declaração", "termo", "certidão", "certidão de julgamento"].index(line["section_label"].lower())
    return ABSTAIN


@labeling_function()
def ls_label_trf2(x):
    #print(x)
    bbox = [x["x0"],x["y0"],x["x1"],x["y1"]]
    
    line = busca_texto(json_trf2(file_path+"/"+x["file_name"]), bbox, x["page"])
    #print(line)
    if line is None:
        return ABSTAIN
    else:
        if(line["section_label"] is not None):
            #print(line["section_label"])
            return ["partes", "relatório", "ementa", "voto", "acórdão", "termo de julgamento", "autuação", "embargos de declaração", "termo", "certidão", "certidão de julgamento"].index(line["section_label"].lower())
    return ABSTAIN


line = {
    "bbox": [
            298.2,
            656.442,
            362.30789999999996,
            669.442
        ],
    "page": 2,
    "text": "ACÓRDÃO\n"
}
#line = {'bbox': [177.10000000000002, 85.108, 559.264, 97.108], 'text': 'no  REsp  1.526.138/MG,  Rel.  Min.  Maria  Thereza  de  Assis  Moura,  Corte \n', "page" : 1}
#print(lf_label_section_json(line, '/home/marlon/DireitoDigital/PDF/STJ/stj_20191011.pdf'))

df = cria_dataset_nao_anotado('/home/marlon/DireitoDigital/PDF/STJ')
df.to_csv(file_path+'/dataset.csv')



#print(df_train)
#print(df_test)


from snorkel.labeling import PandasLFApplier

lfs = [lf_label_stj,ls_label_trf2]

applier = PandasLFApplier(lfs=lfs)
L_train = applier.apply(df=df_train)

print(L_train)
      #turn = turn % 2


extract_stj, extract_trf2 = (L_train != ABSTAIN).mean(axis=0)
print(f"lf_label_stj coverage: {lf_label_stj * 100:.1f}%")
print(f"ls_label_trf2 coverage: {ls_label_trf2 * 100:.1f}%")