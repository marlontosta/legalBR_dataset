import pdfplumber
from pdfminer.layout import LAParams, LTContainer, LTText
from pdfminer.high_level import extract_pages
from decimal import Decimal

file = '/home/eraldo/lia/src/lia-pln-datasets-models/pln-juridico/stf/751181305.pdf'


def process_textual_componenets(element, res=[]):
    if isinstance(element, LTText):
        res.append(element)
    elif isinstance(element, LTContainer):
        for e in element:
            process_textual_componenets(e, res)
    return res

laparams = {"all_texts": True}

# pages_miner = list(extract_pages(file, laparams=LAParams(**laparams)))
# txt_elements = process_textual_componenets(pages_miner[0])

with pdfplumber.open(file, laparams=laparams) as pdf:
    pages_plumber = pdf.pages

    page = pages_plumber[0]
    words = page.extract_words()
    im = page.to_image(resolution=300)
    txt_elements = process_textual_componenets(page.layout)

    rects = [tuple(Decimal(v) for v in (e.x0, e.y1, e.x1, e.y0)) for e in txt_elements]
    im.draw_rects(rects)
