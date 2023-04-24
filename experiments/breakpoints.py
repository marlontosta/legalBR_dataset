from extract_tokens_lines import Breakpoint, PDFExtractParts
import re

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



#A ORDEM DOS BREAKPOINTS IMPORTA!!
stj_breakpoints = Breakpoint(r'.+:.+', label = 'PARTES', function = text_function, previous_label='None')
stj_breakpoints.add(r'^ ?E ?M ?E ?N ?T ?A ?$',label='EMENTA',function=text_function)
stj_breakpoints.add(r'^ ?A ?C ?. ?R ?D ?. ?O ?$',label='ACORDAO',function=text_function)
stj_breakpoints.add(770,field='y',label='None',function=coordMore, single=True)
stj_breakpoints.add(r'^C ?E ?R ?T ?I ?D ?. ?O +D ?E +J ?U ?L ?G ?A ?M ?E ?N ?T ?O$',label='CERTIDAO_DE_JULGAMENTO',function=text_function)
stj_breakpoints.add(r'^C ?E ?R ?T ?I ?D ?. ?O$',label='CERTIDAO',function=text_function)
stj_breakpoints.add(r'^A ?U ?T ?U ?A ?. ?. ?O$',label='AUTUACAO',function=text_function)
stj_breakpoints.add(r'^—? ?R ?E ?L ?A ?T ?. ?R ?I ?O ?—?(\(\w*\))?$',label='RELATORIO',function=ignoreCase)
stj_breakpoints.add(r'^(— )?V ?O ?T ?O ?:?.*(— )?$',label='VOTO',function=text_function)
stj_breakpoints.add(r'^.*N ?º.*\d{4}/(\d|-).?',label='None',function=text_function)
stj_breakpoints.add(25,field='y',label='None',function=coordLess, single=True)
trf2_breakpoints = Breakpoint(r'(^.* : [A-Za-z]+.*)', label = 'PARTES', function = text_function, single=True)
trf2_breakpoints.add(r'^ ?E ?M ?E ?N ?T ?A ?$',label='EMENTA',function=text_function)
trf2_breakpoints.add(r'^ ?A ?C ?. ?R ?D ?. ?O ?$',label='ACORDAO',function=text_function)
trf2_breakpoints.add(r'^.*(N ?º|CNJ).* : \d+(\d|\.|-| |\(|\))*$',function =ignoreCase,single=True)
trf2_breakpoints.add(r'^(— )?V ?O ?T ?O ?:?.*(— )?$',label='VOTO',function=text_function)
trf2_breakpoints.add(r'^—? ?R ?E ?L ?A ?T ?. ?R ?I ?O ?—?(\(\w*\))?',label='RELATORIO',function=ignoreCase)
trf2_breakpoints.add(r'^O ?R ?I ?G ?E ?M ? ?:',label='None',function=ignoreCase, single=True)
trf2_breakpoints.add(r'^É ?(com)?o( o)? voto.?$',label='None',function=text_function, previous_label='VOTO',include_current=False)
trf2_breakpoints.add(r'^Trata-se de.*$',label='RELATORIO',function=text_function, previous_label='ACORDAO')
trf2_breakpoints.add(r'^Neste sentido:?$',label='VOTO',function=ignoreCase, previous_label='RELATORIO')
trf2_breakpoints.add(r'^\d\d?\d?$',label='None',function=text_function, single=True)

tjpb_breakpoints = Breakpoint(r'(^PODER JUDICI.RIO$)', text_function, single=True)
tjpb_breakpoints.add(r'^É (com)?o( o)? voto.?$',label='None',function=text_function, previous_label='VOTO',include_current=False)
#tjpb_breakpoints.add(r'^.*Acórdão.*$',label='ACORDAO',function=text_function,previous_label='None')
#tjpb_breakpoints.add(86,label='CABECALHO',function=cabecalho,single=True,field='y0')
#tjpb_breakpoints.add(774,label='RODAPE',function=rodape,single=True,field='y1')
tjpb_breakpoints.add(r'^(?!.*OAB).*n\.*º* \d+.*\d+$',ignoreCase,single=True)
tjpb_breakpoints.add(r'^_+$',single=True,function=text_function)
tjpb_breakpoints.add(r'^Relatora?.?:.*$',label='PARTES',function=text_function,previous_label='None')
tjpb_breakpoints.add(r'^[A-Z]+ ?:.*$',label='PARTES',function=text_function, previous_label='None')
tjpb_breakpoints.add(r'^V ?i ?s ?t ?o ?s.?(,.*$|$)',label='ACORDAO',function=ignoreCase, previous_label='EMENTA')
#tjpb_breakpoints.add(r'^VISTOS.?,.*$',label='ACORDAO',function=text_function, previous_label='EMENTA')
tjpb_breakpoints.add(r'^—? ?R ?E ?L ?A ?T ?. ?R ?I ?O ?—?$',label='RELATORIO',function=ignoreCase, previous_label='ACORDAO')
tjpb_breakpoints.add(r'^Trata-se de.*$',label='RELATORIO',function=text_function, previous_label='ACORDAO')
tjpb_breakpoints.add(r'^(— )?V ?O ?T ?O ?:?.*(— )?$',label='VOTO',function=text_function)
tjpb_breakpoints.add(r'^Neste sentido:?$',label='VOTO',function=ignoreCase, previous_label='RELATORIO')
tjpb_breakpoints.add(r'^É .*o relat.?rio\.',label='VOTO',function=ignoreCase, previous_label='RELATORIO',include_current=False)
tjpb_breakpoints.add(r'^.*$',label='EMENTA',function=all_upper, previous_label='PARTES')
tjpb_breakpoints.add(r'^\d\d?\d?$',label='None',function=text_function, single=True)


tjmg_breakpoint = Breakpoint(r'(^Tribunal de Justiça de Minas Gerais$)', ignoreCase, single=True)
tjmg_breakpoint.add(r'^(\s|\.|/|-|\d)*$',label='None',function=text_function, single=True)
tjmg_breakpoint.add(r'^.*APELA(NTE|DO) ?(\(A\))? ?(\(S\))? ?:.*$', label = 'PARTES',function=text_function)
tjmg_breakpoint.add(r'^.*EMBARGA(NTE|DO) ?(\(A\))? ?(\(S\))? ?:.*$', label = 'PARTES',function=text_function)
tjmg_breakpoint.add(r'^.*IMPETRA(NTE|DO) ?(\(A\))? ?(\(S\))? ?:.*$', label = 'PARTES',function=text_function)
tjmg_breakpoint.add(r'^.*AGRAVA(NTE|DO) ?(\(A\))? ?(\(S\))? ?:.*$', label = 'PARTES',function=text_function)
tjmg_breakpoint.add(r'^.*INTERESSADO ?(\(A\))? ?(\(S\))? ?:.*$', label = 'PARTES',function=text_function)
tjmg_breakpoint.add(r'^.*REQUER(ENTE|IDO) ?(\(A\))? ?(\(S\))? ?:.*$', label = 'PARTES',function=text_function)
tjmg_breakpoint.add(r'^.*PACIENTE ?(\(S\))? ?:.*$', label = 'PARTES',function=text_function)
tjmg_breakpoint.add(r'^.*V.TIMA ?(\(S\))? ?:.*$', label = 'PARTES',function=text_function)
#tjmg_breakpoint.add(r'^Relator.?:.*$',label='METADADOS',function=ignoreCase)
tjmg_breakpoint.add(r'^EMENTA: .*$', label = 'EMENTA',previous_label = 'None',function=text_function)
tjmg_breakpoint.add(r'^A.?C.?Ó.?R.?D.?Ã.?O$', label = 'ACORDAO',function=text_function)
tjmg_breakpoint.add(r'^(>+|ADIADO)$', label='None', function=text_function)
tjmg_breakpoint.add(r'^S.MULA ?:.*$', label = 'SUMULA',function=text_function)
tjmg_breakpoint.add(r'^DESA?\. .*\(?RELATORA?\)?$', label='VOTO', function=text_function, previous_label='ACORDAO', include_current=False)
tjmg_breakpoint.add(r'^((O|A) SRA?. )?DESA?\..*:$', label='VOTO', function=text_function, include_current=False)
#tjmg_breakpoint.add(r'^.*É (com)?o? voto.?$', label = 'EMEMNTA',function=text_function, include_current=False)


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



tribunal_breakpoints = {
    'stj' : stj_breakpoints,
    'trf2': trf2_breakpoints,
    'tjpb': tjpb_breakpoints,
    'tjmg': tjmg_breakpoint,
    'stf' : stf_breakpoints,
}