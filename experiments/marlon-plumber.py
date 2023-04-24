import pdfplumber

#file = '/home/marlon/DireitoDigital/PDF/STJ/stj_20210329.pdf'
file = '/home/marlon/DireitoDigital/PDF/STJ/stj_20200520.pdf'

pdf = pdfplumber.open(file)
'''with pdfplumber.open(file) as pdf:
    first_page = pdf.pages[0]
    print(first_page.chars[0])
'''

#arquivo = open('/home/marlon/DireitoDigital/PDF/STJ/stj_20200520.txt', "a")
doc = ""
for page in pdf.objects:
    print(page)
    #doc += page.extract_text()
    #arquivo.write(doc)
    #print(page)

#print(doc)
import re

m = re.search('(.*[A-Za-z]+(\d)+.*\n)*(.*Petição.*:.*(\d)*.*)*\n(.*Página( )+(\d)+( )+de( )+(\d)+)+', doc)
if m:
    doc = re.sub('(.*[A-Za-z]+(\d)+.*\n)*(.*Petição.*:.*(\d)*.*)*\n(.*Página( )+(\d)+( )+de( )+(\d)+)+','##RODAPE##',doc)
    rodape = m.group(0)
    #print(m.groups)
    print('Rodapé: ' + rodape)
    #print(doc)

m = re.search('( )*(Superior Tribunal de Justiça)+', doc)
if m:
    doc = re.sub('( )*(Superior Tribunal de Justiça)+','##CABECALHO##',doc)
    cabecalho = m.group(0)
    #print(m.groups)
    print('Cabeçalho: ' + cabecalho)
    #print(doc)

m = re.search('( )*(Superior Tribunal de Justiça)+', doc)
if m:
    doc = re.sub('( )*(Superior Tribunal de Justiça)+','##CABECALHO##',doc)
    cabecalho = m.group(0)
    #print(m.groups)
    print('Cabeçalho: ' + cabecalho)
    #print(doc)


import os   
regex = 'VOTO\n(.*(\s)*.*)*Federal'
m = re.search(regex, doc)

while m:
    #doc = re.sub('( )*(Superior Tribunal de Justiça)+','##CABECALHO##',doc)
    partes = m.group(0)
    #print(m.groups)
    print('Titulo e Partes: ' + partes)
    #print(doc)
    regex += '(.*:.*)*(\s)*.*(\s*(?!EMENTA))'
    #regex += r'.*(?![Ementa,Relatório]).*'
    print(regex)
    m = re.search(regex, doc)




#print(doc)