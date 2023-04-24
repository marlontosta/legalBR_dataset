from datetime import date, datetime
from email.mime import base
from pickle import FALSE
from sys import meta_path
from extract_tokens_lines import Breakpoint, PDFExtractParts
from pymongo import MongoClient
from tqdm import tqdm
import re, logging, os
from multiprocessing import Pool


RED = '\033[91m'
ENDC = '\033[0m'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


corpus = MongoClient().juridico

for path, subdirs, files in os.walk('/home/juridico/pdfs/stf'):
    for name in files:
        if name.endswith('.pdf'):
            corpus['stf_crawler'].insert_one({"pdf_file" : os.path.join(path, name)})
            #print(os.path.join(path, name))
