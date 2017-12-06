
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

# os.system("taskset -p 0xff %d" % os.getpid())


def data_initialize():

    global entities
    entities = util.get_entities(chunks=True)
    entities.set_index(['article', 'entity'], inplace=True)
    print('Entities loaded!')


def extract(article):

    if len(article.page_name) > 250:
        return

    print(article.page_name.encode('utf8'), '\n')

    # get the linked entities within the article
    #article_entities = entities[entities['article'] == article.page_id, 'entity']
    #article_entities = entities.loc[entities.article.str.match(article.page_id), 'entity']
    #article_entities = entities.loc[entities.article == article.page_id, 'entity']
    try:
        article_entities = entities.loc[(article.page_id,)].index
    except:
        with open(settings.PATH_DATAOBJECTS + 'unfound_articles.txt', 'a', encoding='utf-8') as err:
            err.write(article.page_name)
            err.write('\n')
            err.close()
            return

    # get the article content
    article_body = article.to_string()

    G = pd.DataFrame(columns=['article', 'entity', 'mention'], dtype='unicode')

    for entity in article_entities:

        try:
            pattern = nlp.get_entity_pattern(entity)

            for pair in re.finditer(pattern, article_body):
                mention, entity = pair.group()[1:].split(']')
                entity = entity[1:-1]
                if nlp.invalid_entity(entity):
                    continue
                if mention.strip() == '' or len(mention) > 249:
                    continue

                G.loc[len(G.index)] = [article.page_name, entity, mention]

                # we should strip mentions from ''

        except:
            pass

    G.to_hdf(settings.PATH_DATAOBJECTS + str(os.getpid()) + '.hdf5',
             format='table', append=True, data_columns=True,
             key='articles_entities_mentions_graph', encoding='utf-8',
             min_itemsize={'article': 300, 'entity': 300, 'mention': 300})

if __name__ == '__main__':

    #mgr = Manager()
    #ns = mgr.Namespace()
    # get all linked entities of Wikipedia
    #ns.entities = util.get_entities(chunks=True)
    #entities = util.get_entities(chunks=True)

    #partial_extract = partial(extract, ns.entities)
    #partial_extract = partial(extract, get_article_entities(entities, None))

    p = Pool(processes=14, initializer=data_initialize, initargs=(), maxtasksperchild=200)

    with open(settings.PATH_ARTICLES, 'rb') as a:

        t0 = time.time()

        for work in p.imap(extract, data.iter_annotations(a), chunksize=500):
            pass

        print('\n')
        print('JOINING NOW')

        p.close()
        p.join()

        print('\n')
        print('DONE')

        t1 = time.time()
        t = t1-t0
        print(t)
