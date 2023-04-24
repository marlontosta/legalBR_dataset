import token
from xmlrpc.client import Boolean
import logging
from pdfplumber_extractor import PDFPlumberTokenExtractor
import pdfplumber, re

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

class Breakpoint:
    breakpoints = []
    def __init__(self, regex, function, field:str='Text', label:str='None' , single:Boolean =False, include_current:Boolean=True, previous_label:str='*'):
        self.breakpoints = []
        breakpoint = {'regex'   :regex,
                      'label'   :label,
                      'single'  :single,
                      'include_current':include_current,
                      'previous_label' :previous_label,
                      'function':function,
                      'field': field
        }

        self.breakpoints.append(breakpoint)

    def add(self, regex, function, field:str='Text', label:str='None' , single:Boolean =False, include_current:Boolean=True, previous_label:str='*'):
        breakpoint = {'regex'   :regex,
                      'label'   :label,
                      'single'  :single,
                      'include_current':include_current,
                      'previous_label' :previous_label,
                      'function':function,
                      'field': field
        }
        self.breakpoints.append(breakpoint)
    
    def remove(self, regex, field:str='Text', label:str='None'):
        for item in self.breakpoints:
            if item['regex'] == regex and item['field'] == field and item['label'] == label:
                self.breakpoints.remove(item)

    def check(self, line, current_label):
        text_line = lines_to_text(line)
        for bp in self.breakpoints:
            if(bp['field'] == 'Text'):
                field = text_line
            else:
                field = line[bp['field']]

            if bp['function'](field,bp['regex'], current_label, bp['previous_label']):
                return bp['label'], bp['single'], bp['include_current']


class PDFExtractParts:
    def __init__(self, pdf_path:str):
        try:
            with pdfplumber.open(pdf_path) as self.pdf:
                pdf_extractor = PDFPlumberTokenExtractor()
                self.pdf_pages = []

                
                for pdf_page in self.pdf.pages:         
                    page = {}
                    page['page_number'] = pdf_page.page_number
                    pdf_page = pdf_page.dedupe_chars(tolerance=0.1)


                    tokens = pdf_extractor.obtain_word_tokens(pdf_page)

                    #tokens = [x for x in pdf_extractor.obtain_word_tokens(pdf_page) if x['size']>2]
                    lines_y = list(dict.fromkeys(list(map(lambda x: x['y'], tokens))))
                    lines_y.sort(key=float)

                    lines = []

                    for i in range(len(lines_y)):
                        lines.append([])

                    for token in tokens:
                        index = lines_y.index(token['y'])
                        lines[index].append(token)

                    line_dict = []
                    for i, line in enumerate(lines):
                        line_x0 = min(list(dict.fromkeys(list(map(lambda x: x['x'], line)))))
                        line_width = max(list(dict.fromkeys(list(map(lambda x: x['x']+x['width'], line))))) - line_x0
                        line_y0 = min(list(dict.fromkeys(list(map(lambda y: y['y'], line)))))
                        line_height = max(list(dict.fromkeys(list(map(lambda y: y['y']+y['height'], line))))) - line_y0
                         
                        line_dict.append({'x':line_x0,
                                        'width':line_width,
                                        'y':line_y0,
                                        'height': line_height,
                                        'tokens' : line})
                        
                    #print(line_dict,"\n\n")
                        #line_dict.append({'line_bbox':lines_bbox,'tokens': line})

                    page['lines'] = line_dict
                    self.pdf_pages.append(page)
        except Exception as e:
            raise e

    
    '''def label_parts(self, breakpoints):
        section_label = None
        for page in self.pdf_pages:
            #print(pages, breakpoints)
            for line in page['lines']:
                print(line)
                line['section_label'] = section_label
                #print(self.lines_to_text(line),end = ' - ')
                for bp in breakpoints:
                    #[r'^\d+$', None, True, False]
                    #print(bp, end = ' ')
                    if re.match(bp[0], self.lines_to_text(line)) and (bp[4] == section_label or bp[4] == '*'):
                        print(bp)
                        if not bp[3]:
                            line['section_label'] = bp[1]
                            break
                        line['section_label'] = section_label
                        section_label = bp[1]

                        if bp[2]: 
                            line['section_label'] = section_label
                        break'''

    def label_parts(self, breakpoints):
        section_label = 'None'
        for page in self.pdf_pages:
            for line in page['lines']:
                line['section_label'] = section_label
                try:
                    new_label,single,include_current = breakpoints.check(line, section_label)
                except:
                    continue

                if single:
                    line['section_label'] = new_label
                    continue
                else:
                    section_label = new_label

                if include_current:
                    line['section_label'] = new_label
    
    def tokens_to_text(self):
        line_text = ''
        for page in self.pdf_pages:
            for lines in page['lines']:
                for line in lines['tokens']:
                    line_text += (line['text'])+' '
                line_text += '\n'
        return line_text.strip()


    #procura um texto dentro do arquivo pdf
    def find(self, text):
        for page in self.pdf_pages:
            for line in page['lines']:
                line_text = ''
                for token in line['tokens']:
                    line_text += (token['text'])+' '
                if re.match(text,line_text.strip()):
                    return (line['x'], line['width'], line['y'], line['height'])            
            
        return False



def lines_to_text(line):
        line_text = ''
        for token in line['tokens']:
            line_text += (token['text'])+' '

        return line_text.strip()
    

def get_lines(pdf_page):
    text_pdf = []
    for page in pdf_page:
        text_page = []
        for line in page['lines']:
            text_line = []
            for token in line['tokens']:
                print(token['text'])
                text_line
            text_page += text_line+'\n'
        text_pdf += text_page
    return text_pdf
        


def format_doc(file):
    with pdfplumber.open(file) as pdf:
        pdf_extractor = PDFPlumberTokenExtractor()
        pdf_pages = []
        #print(pdf)
        for pdf_page in pdf.pages:
            page = {}
            page['page_number'] = pdf_page.page_number

            tokens = pdf_extractor.obtain_word_tokens(pdf_page)
            #print(tokens)
            
            lines_y = list(dict.fromkeys(list(map(lambda x: x['y'], tokens))))
            #print()
            lines = [list()] * len(lines_y)
            for i in range(len(lines_y)):
                lines[i] = []

            for token in tokens:
                index = lines_y.index(token['y'])
                (lines[index]).append(token)

            line_dict = []
            for line in lines:
                line_x0 = min(list(dict.fromkeys(list(map(lambda x: x['x'], line)))))
                line_x1 = max(list(dict.fromkeys(list(map(lambda x: x['x']+x['width'], line)))))
                line_y0 = min(list(dict.fromkeys(list(map(lambda y: y['y'], line)))))
                line_y1 = max(list(dict.fromkeys(list(map(lambda y: y['y']+y['height'], line)))))
                lines_bbox = {'x0':line_x0, 'x1':line_x1, 'y0':line_y0, 'y1': line_y1}
                
                line_dict.append({'line_bbox':lines_bbox,'tokens': line})

            page['lines'] = line_dict

            pdf_pages.append(page)
            
        return pdf_pages