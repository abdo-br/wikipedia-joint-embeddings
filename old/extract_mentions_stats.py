
import re
import random
import pandas as pd
import settings
import read_data as data

# DataFrames to store stats
Graph = pd.DataFrame(columns=['Article', 'Entity', 'Mention'], dtype='unicode')

i = 0
# Iterate over Wikipedia articles
# and find mentions & entities
# and store stats
with open(settings.PATH_ARTICLES, 'rb') as a:

    # valid file name dictionary
    valid_filename = str.maketrans('', '', r'<>:"/\|?*')

    # compile the regex pattern of (mention, entity) pair
    pattern = r'\[[^\[\]]*?\](?=\([^\[]+?\))\([^\[]+?\)'
    MentionEntity_Pair = re.compile(pattern)

    for article in data.iter_annotations(a):

        # Get random articles
        # if random.randint(0, 1) == 1: continue

        # print article name
        print(article.page_name, ' ', i, '\n')
        # print(i,'\n')

        # get the article content
        article_body = article.to_string()

        # save the article
        # with open(Settings.PATH_OUTPUT+article.page_name.translate(valid_filename)+'.txt', 'w', encoding='utf-8') as processed_article:
        #   processed_article.write(article_body)

        # find entity mention pairs
        # e.g. Link >>>> [European Union](European Union) <<<< Entity

        for pair in MentionEntity_Pair.finditer(article_body):
            mention, entity = pair.group()[1:].split(']')
            if entity[1] == ')': continue
            if '(' in entity[1:]:
                entity = entity[1:]
            else:
                entity = entity[1:-1]

            # store the new pair
            Graph.loc[len(Graph.index)] = [article.page_name, entity, mention.replace('\'\'', '')]

        i += 1

        if settings.NUM_ARTICLES != -1 and i > settings.NUM_ARTICLES: break

    # aggregate
    # and save results
    Graph.to_pickle(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.gzip', compression='gzip')
    Graph.to_csv(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.csv', encoding='utf-8', index=False)

    Final_Graph = Graph.groupby(by=['Entity', 'Mention'], sort=False).count()
    # save results
    Final_Graph.to_pickle(settings.PATH_DATAOBJECTS+'entities_mentions_graph.gzip', compression='gzip')
    Final_Graph.to_csv(settings.PATH_DATAOBJECTS+'entities_mentions_graph.csv', encoding='utf-8')

    # fix results look
    Final_Graph.reset_index(level=0, inplace=True)
    Final_Graph.reset_index(inplace=True)
