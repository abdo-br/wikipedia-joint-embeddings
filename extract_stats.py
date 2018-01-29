
import os
import re
import time
import util
import sys, getopt
import settings
import pandas as pd
import nlp_util as nlp
import read_data as data
from functools import partial
from multiprocessing import Manager, Pool, freeze_support


def initialize_entities():

    global entities
    entities = util.get_entities()
    entities = util.split_dataframe(entities)
    print('Entities loaded!')


def extract(article):

    #print(article.page_name.encode('utf8'), '\n')

    # linked entities within article
    q = 'article == "{}"'.format(article.page_id)
    article_entities = entities['{}'.format(util.get_hash(article.page_id))].query(q)
    article_entities = article_entities.loc[article_entities.valid == 'True', 'entity']

    article_body = article.to_string()

    G = pd.DataFrame(columns=['article', 'entity', 'mention'], dtype='unicode')

    for entity in article_entities:
        for pair in re.finditer(nlp.get_entity_pattern(entity), article_body):
            values = pair.group()[1:].split(']')
            mention = values[0]
            entity = values[1][1:-1]

            G.loc[len(G.index)] = [article.page_name, entity, mention]

            # we should strip mentions from ''

    G.to_hdf(settings.PATH_DATAOBJECTS + 'stats/' + str(os.getpid()) + '.hdf5', format='table',
             append=True, complib='blosc', complevel=3, key='', encoding='utf-8',
             min_itemsize={'article': 500, 'entity': 500, 'mention': 500})


if __name__ == '__main__':

    cores = 3

    opts, args = getopt.getopt(sys.argv[1:], 'c:')
    for opt, arg in opts:
        if opt == '-c':
            cores = int(arg)

    #mgr = Manager()
    #ns = mgr.Namespace()
    # get all linked entities of Wikipedia
    #ns.entities = util.get_entities()
    #entities = util.get_entities()

    #partial_extract = partial(extract, ns.entities)
    #partial_extract = partial(extract, get_article_entities(entities, None))

    p = Pool(processes=cores, initializer=initialize_entities, initargs=(), maxtasksperchild=200)

    with open(settings.PATH_ARTICLES, 'rb') as a:

        j = 0
        tic = time.time()

        try:

            for work in p.imap(extract, data.iter_annotations(a), chunksize=1000):

                j += 1
                print(j)

        except Exception as e:

            with open('STATS_ERRORS.txt', 'a') as err:
                err.write(a.page_id)

    print('\n')
    print('JOINING NOW')

    p.close()
    p.join()

    print('\n')
    print('DONE')

    toc = time.time()
    print((toc-tic) % 60)
