
import os
import re
import time
import pandas as pd
import settings
import read_data as data
from multiprocessing import Pool

# compile the regex pattern
pattern = r'\[[^\[\]]*?\](?=\([^\[]+?\))\([^\[]+?\)'
MentionEntity_Pair = re.compile(pattern)

def extract(article):

    # print article name
    #print(article.page_name.encode('utf8'), '\n')

    # get the article content
    article_body = article.to_string()
    print(os.getpid())
    print(article.page_name.encode('utf8'), '\n')

    # find entity mention pairs
    # e.g. Link >>>> [European Union](European Union) <<<< Entity

    G = pd.DataFrame(columns=['Article', 'Entity', 'Mention'], dtype='unicode')

    try:

        for pair in MentionEntity_Pair.finditer(article_body):
            mention, entity = pair.group()[1:].split(']')
            if entity[1] == ')': continue
            if '(' in entity[1:]:
                entity = entity[1:]
            else:
                entity = entity[1:-1]

            # store the new pair
            G.loc[len(G.index)] = [article.page_name, entity, mention.replace('\'\'', '')]
    except:
        pass

    return G

if __name__ == '__main__':

    with open(settings.PATH_ARTICLES, 'rb') as a:

        #logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

        Graph = pd.DataFrame(columns=['Article', 'Entity', 'Mention'], dtype='unicode')

        p = Pool(processes=20, maxtasksperchild=200)
        t0 = time.time()
        i = 0
        #Graph = Graph.append(p.imap(extract, data.iter_annotations(a)))
        for work in p.imap(extract, data.iter_annotations(a), chunksize=10):
            Graph = Graph.append(work)

        t1 = time.time()
        t = t1-t0
        print(t)

        print('\n')
        print('JOINING NOW')

        p.close()
        p.join()

        print('\n')
        print('DONE')

        # aggregate
        # and save results
