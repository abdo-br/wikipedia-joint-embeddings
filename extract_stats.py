
import os
import re
import time
import util
import settings
import pandas as pd
import nlp_util as nlp
import read_data as data
from functools import partial
from multiprocessing import Manager, Pool


def initialize_entities():

    global entities
    entities = util.get_entities(chunks=True)
    print('Entities loaded!')


def extract(article):

    print(article.page_name.encode('utf8'), '\n')

    # linked entities within article
    article_entities = entities.loc[entities.article == article.page_id, 'entity']

    try:

        article_body = article.to_string()

        G = pd.DataFrame(columns=['article', 'entity', 'mention'], dtype='unicode')

        for entity in article_entities:
            for pair in re.finditer(nlp.get_entity_pattern(entity), article_body):
                mention, entity = pair.group()[1:].split(']')
                entity = entity[1:-1]
                if nlp.invalid_entity(entity):
                    continue

                G.loc[len(G.index)] = [article.page_name, entity, mention]

                # we should strip mentions from ''

        G.to_hdf(settings.PATH_DATAOBJECTS + 'stats/' + str(os.getpid()) + '.hdf5', format='table',
                 append=True, complib='blosc', complevel=3, key='', encoding='utf-8',
                 min_itemsize={'article': 500, 'entity': 500, 'mention': 500})

    except:
        pass


if __name__ == '__main__':

    #mgr = Manager()
    #ns = mgr.Namespace()
    # get all linked entities of Wikipedia
    #ns.entities = util.get_entities(chunks=True)
    #entities = util.get_entities(chunks=True)

    #partial_extract = partial(extract, ns.entities)
    #partial_extract = partial(extract, get_article_entities(entities, None))

    p = Pool(processes=24, initializer=initialize_entities, initargs=(), maxtasksperchild=200)

    with open(settings.PATH_ARTICLES, 'rb') as a:

        tic = time.time()

        for work in p.imap(extract, data.iter_annotations(a), chunksize=1000):
            pass

        print('\n')
        print('JOINING NOW')

        p.close()
        p.join()

        print('\n')
        print('DONE')

        toc = time.time()
        print((toc-tic) % 60)
