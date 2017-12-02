
import os
import re
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

    # find entity mention pairs
    # e.g. Link >>>> [European Union](European Union) <<<< Entity

    G = pd.DataFrame(columns=['Article', 'Entity', 'Mention'], dtype='unicode')

    try:

        for pair in MentionEntity_Pair.finditer(article_body):
            print(pair).group()
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

        p = Pool(processes=3, maxtasksperchild=100)
        #Graph = Graph.append(p.imap(extract, data.iter_annotations(a)))
        for work in p.imap(extract, data.iter_annotations(a), chunksize=2000):
            Graph = Graph.append(work)

        print('\n')
        print('JOINING NOW')

        p.close()
        p.join()

        print('\n')
        print('DONE')

        # aggregate
        # and save results

        try:
            Graph.to_hdf(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.hdf5', format='table', data_columns=True, key='articles_entities_mentions_graph')
        except:
            pass

        try:
            Graph.to_csv(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.csv', encoding='utf-8', index=False, chunksize=2000)
        except:
            pass

        try:
            Graph.to_pickle(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.gzip', compression='gzip')
        except:
            pass

        try:
            Final_Graph = Graph.groupby(by=['Entity', 'Mention'], sort=False).count()
        except:
            pass

            # save results
        try:
            Final_Graph.to_hdf(settings.PATH_DATAOBJECTS+'entities_mentions_graph.hdf5', format='table', data_columns=True, key='entities_mentions_graph')
        except:
            pass

        try:
            Final_Graph.to_csv(settings.PATH_DATAOBJECTS+'entities_mentions_graph.csv', encoding='utf-8', chunksize=2000)
        except:
            pass

        try:
            Final_Graph.to_pickle(settings.PATH_DATAOBJECTS+'entities_mentions_graph.gzip', compression='gzip')
        except:
            pass

            # fix results look
            #Final_Graph.reset_index(level=0, inplace=True)
            #Final_Graph.reset_index(inplace=True)
