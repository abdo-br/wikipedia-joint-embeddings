
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

#os.system("taskset -p 0xff %d" % os.getpid())

#def get_article_entities(entities, article):
#    return entities[entities['article'] == article.page_id]

def data_initialize():
     global entities
     entities = util.get_entities(chunks=True)
     print('Entities loaded!')

def extract(article): # entities,

    # print article name
    print(os.getpid())
    print(article.page_name.encode('utf8'), '\n')

    # get the linked entities within the article
    article_entities = entities[entities['article'] == article.page_id]

    # get the article content
    article_body = article.to_string()

    G = pd.DataFrame(columns=['article', 'entity', 'mention'], dtype='unicode')

    try:

        for index, entity in article_entities['entity'].iteritems():

            pattern = nlp.get_entity_pattern(entity)

            for pair in re.finditer(pattern, article_body):
                mention, entity = pair.group()[1:].split(']')
                if len(mention) > 250: continue
                entity = entity[1:-1]
                #print(entity)
                if nlp.invalid_entity(entity):
                    #print(entity)
                    continue
                if mention.strip() == '': continue

                # store the new pair
                G.loc[len(G.index)] = [article.page_name, entity, mention]
                # we should look at mentions later for ''

    except Exception as e:

        print(str(e))

    return G

if __name__ == '__main__':

    #mgr = Manager()
    #ns = mgr.Namespace()
    # get all linked entities of Wikipedia
    #ns.entities = util.get_entities(chunks=True)
    #entities = util.get_entities(chunks=True)

    #partial_extract = partial(extract, ns.entities)
    #partial_extract = partial(extract, get_article_entities(entities, None))

    p = Pool(processes=3, initializer=data_initialize, initargs=(), maxtasksperchild=200)

    with open(settings.PATH_ARTICLES, 'rb') as a:

        t0 = time.time()

        for work in p.imap(extract, data.iter_annotations(a), chunksize=10):
            work.to_hdf(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.hdf5',
                        format='table', append =True, data_columns=True,
                        key='articles_entities_mentions_graph',
                        min_itemsize={'article':250, 'entity':250, 'mention':250})

        print('\n')
        print('JOINING NOW')

        p.close()
        p.join()

        print('\n')
        print('DONE')

        t1 = time.time()
        t = t1-t0
        print(t)
