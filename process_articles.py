
import re
import util
import nlp_util as nlp
import settings
import read_data as data
import pandas as pd

# get all linked entities of Wikipedia
entities = util.get_entities(True)
entities.set_index(['article', 'entity'], inplace=True)

class Sentences():

    def __iter__(self):

        i = 1

        # create dictionary for entities
        entities_dectionary = pd.DataFrame(columns=['EntityID', 'Entity'], index=None)

        # read articles
        # and process linked entities
        with open(settings.PATH_ARTICLES, 'rb') as a:

            for article in data.iter_annotations(a):
                i += 1
                outPath = settings.PATH_OUTPUT + article.page_name.translate(util.valid_filename())

                # get the linked entities within the article
                try:
                    article_entities = entities.loc[(article.page_id,)].index
                except:
                    with open(settings.PATH_DATAOBJECTS + 'w2v_unfound_articles.txt', 'a', encoding='utf-8') as err:
                        err.write(article.page_name)
                        err.write('\n')
                        err.close()
                        continue

                # get clean article
                article_body = nlp.get_clean_article(article.to_string())

                # find and replace entities
                for entity in article_entities:

                    # create entity id
                    entity_id = nlp.get_entity_id(entity)

                    # save the new Entity ID
                    # and prevent duplicates
                    if entity_id not in entities_dectionary['EntityID'].values:
                        entities_dectionary.loc[len(entities_dectionary.index)] = [entity_id, entity]

                    # replace mention and entity with Entity ID
                    # process special characters
                    pair = nlp.get_entity_pattern(entity)

                    # replace the mention (alias) and entity
                    article_body = re.sub(pair, entity_id, article_body)

                # tokenize and yield sentences
                sentences = nlp.get_sentences(article_body)
                for sentence in sentences:
                    sentence = nlp.remove_punctuation(sentence)
                    yield sentence.split()

                # save the article
                with open(outPath, 'w', encoding='utf-8') as body:
                    body.write(article_body)

                if settings.NUM_ARTICLES != -1 and i > settings.NUM_ARTICLES: break

        # save dictionary for entities
        entities_dectionary.to_pickle(settings.PATH_DATAOBJECTS+'entities_dectionary.gzip',
                                      compression='gzip')
