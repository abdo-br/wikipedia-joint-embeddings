
import re
import util
import settings
import pandas as pd
import nlp_util as nlp
import read_data as data

# get all linked entities of Wikipedia
entities = util.get_entities(chunks=True)

# DataFrames to store stats
Graph = pd.DataFrame(columns=['article', 'entity', 'mention'], dtype='unicode')

i = 0
# Iterate over Wikipedia articles
# and find mentions & entities
# and store stats
with open(settings.PATH_ARTICLES, 'rb') as a:

    for article in data.iter_annotations(a):

        # get the linked entities within the article
        article_entities = entities[entities.article == article.page_id]

        # get the article content
        article_body = article.to_string()

        # print article name
        #print(article.page_name, ' ', i, '\n')

        # save the article
        with open(settings.PATH_OUTPUT+article.page_name.translate(util.valid_filename())+'.txt', 'w', encoding='utf-8') as processed_article:
            processed_article.write(article_body)

        for index, entity in article_entities['entity'].iteritems():

            pattern = nlp.get_entity_pattern(entity)

            for pair in re.finditer(pattern, article_body):
                mention, entity = pair.group()[1:].split(']')
                entity = entity[1:-1]
                #print(entity)
                if nlp.invalid_entity(entity):
                    #print(entity)
                    continue
                if mention.strip() == '': continue

                # store the new pair
                Graph.loc[len(Graph.index)] = [article.page_name, entity, mention.replace('\'\'', '')]

        i += 1

        if settings.NUM_ARTICLES != -1 and i > settings.NUM_ARTICLES: break

    # aggregate
    # and save results
    Graph.to_hdf(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.hdf5', format='table', data_columns=True, key='articles_entities_mentions_graph', min_itemsize={'article' : 200, 'entity' : 200, 'mention' : 200})
    Graph.to_pickle(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.gzip', compression='gzip')
    Graph.to_csv(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.csv', encoding='utf-8', index=False)

    Final_Graph = Graph.groupby(by=['entity', 'mention'], sort=False).count()
    # save results
    Final_Graph.to_pickle(settings.PATH_DATAOBJECTS+'entities_mentions_graph.gzip', compression='gzip')
    Final_Graph.to_csv(settings.PATH_DATAOBJECTS+'entities_mentions_graph.csv', encoding='utf-8')

    # fix results look
    Final_Graph.reset_index(level=0, inplace=True)
    Final_Graph.reset_index(inplace=True)
