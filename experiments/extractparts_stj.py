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
from breakpoints import tribunal_breakpoints
from argparse import ArgumentParser

RED = '\033[91m'
ENDC = '\033[0m'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

TRIBUNAL = ''

def label_one(file):
    print(file)
    mongoconn = MongoClient()
    labeled = mongoconn["juridico"][TRIBUNAL+"_labeled_lines"]
    crawler = mongoconn["juridico"][TRIBUNAL+"_crawler"]
    try:
        pdf_file = PDFExtractParts(file['pdf_file'])
        pdf_file.new_label_parts(tribunal_breakpoints['TRIBUNAL'])
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
        print(file)
        mongoconn.close()



def main():
    parser = ArgumentParser(
        description='Process pdf documents in corpus.')
    parser.add_argument('tribunal', help='Court')
    parser.add_argument('threads', help='Threads')
    args = parser.parse_args()


    TRIBUNAL = args.tribunal

    filter = {'$or':[{'labeled' : {'$exists' : 0}},{'labeled':0}]}

    file_list = list(MongoClient()['juridico'][TRIBUNAL+'_crawler'].find(filter,{'pdf_file':1}))

    print('Processing ',len(file_list), 'documents')

    with Pool(args.threads) as p:
        p.map(label_one, file_list)

if __name__ == '__main__':
    main()
