
import re
import util
import nlp_util as nlp
import read_data as data
import pandas as pd
import settings
from enum import Enum

Original = ''
Final = ''

class Level(Enum):
    Linked_Entity = 1
    Mentions = 2 # mentions of article & mentions of article entities
    X = 3

# can be a method to load the knowledge base
entities = util.get_entities(chunks=True)
graph = pd.read_pickle(settings.PATH_DATAOBJECTS+'articles_entities_mentions_graph.gzip', compression='gzip')
stats = pd.read_pickle(settings.PATH_DATAOBJECTS+'entities_mentions_graph.gzip', compression='gzip')
stats.reset_index(level=0, inplace=True)
stats.reset_index(inplace=True)
stats = stats.rename(columns={'article':'freq'})

# temporary fix
stats = stats.rename(columns={'Article':'freq', 'Mention':'mention', 'Entity':'entity'})
graph = graph.rename(columns={'Article':'article', 'Mention':'mention', 'Entity':'entity'})

# set index for effiecent filtring
entities.set_index(['article', 'entity'], inplace=True)
graph.set_index(['article', 'entity'], inplace=True)

def disambiguate(text, mention):
    # naive approach
    most_frequent_entity = stats.at[stats.loc[stats.mention == mention, 'freq'].idxmax(axis=0), 'entity']

    return nlp.get_entity_id(most_frequent_entity)

def search(article, text):

    annotations = pd.DataFrame(columns=['Article', 'Level', 'Mention', 'EntityID', 'Offset', 'Sentence', 'The_Sentence'], dtype='unicode', index=None)

    # maybe text is unclean !!!!!!!!!!!!!
    article_body = text

    # search for mentions of the article
    # and for mentions of the article entities

    # mentions of article
    article_mentions = graph.loc[(article.page_name,)]
    # get entities of article
    article_entities = article_mentions.index.tolist()

    mentions = graph.loc[graph.index.isin(article_entities, 'entity'), 'mention']

    mentions = mentions.append(article_mentions['mention'], ignore_index=True)

    # TODO
    # stem the mentions

    mentions.drop_duplicates(inplace=True)
    mentions = util.sorted_dataframe(mentions, mentions.str.len(), False)

    regex_input = article_body
    for mention in mentions:
        for match in re.finditer(re.escape(mention), regex_input):
            annotations.loc[len(annotations.index)] = [article.page_name, Level(2).name, match.group(), disambiguate(None, match.group()), match.start(), -1, None]
            article_body = nlp.replace_part_of_text(article_body, '☵' * len(match.group()), match.start(), len(match.group()))

    return article_body, annotations, list(mentions)

def annotate(article, linked_entities_only=False):

    annotations = pd.DataFrame(columns=['Article', 'Level', 'Mention', 'EntityID', 'Offset', 'Sentence', 'The_Sentence'], dtype='unicode', index=None)

    # clean on the content
    article_body = nlp.get_clean_article(article.to_string())

    global Original
    Original = article_body

    # find the linked entities
    # get the linked entities within the article
    article_entities = entities.loc[(article.page_id,)].index

    regex_input = article_body
    for entity in article_entities:
        for pair in re.finditer(nlp.get_entity_pattern(entity), regex_input):
            mention, entity = pair.group()[1:].split(']')
            entity = entity[1:-1]
            if nlp.invalid_entity(entity): continue
            annotations.loc[len(annotations.index)] = [article.page_name, Level(1).name, mention, nlp.get_entity_id(entity), pair.start() , -1, None]
            article_body = article_body.replace(pair.group(), '☰' * len(mention))

    # fix the other mentions offsets
    # work on copy of annotations
    rows = annotations[['Level', 'EntityID', 'Offset']].copy(deep=True)
    annotations['Ori_Offset'] = annotations['Offset']

    for index, annotation in annotations.iterrows():
        for i, row in rows.iterrows():
            if row['Offset'] < annotation['Ori_Offset']:
                annotations.loc[index, 'Offset'] -= len(row['EntityID']) + 4

    # search for more entities
    if not linked_entities_only:
        article_body, search_annotations = search(article, article_body)
        annotations = annotations.append(search_annotations)

    # reconstruct the article
    for row in annotations.itertuples():
        article_body = nlp.replace_part_of_text(article_body, row.Mention, row.Offset, len(row.Mention))

    global Final
    Final = article_body

    # map offsets to sentences
    sentences_spans = []
    tokenized_sents = nlp.get_sentences(article_body)
    for sentence in nlp.get_sentences_spans(article_body, tokenized_sents):
        sentences_spans.append(sentence)

    annotations = util.sorted_dataframe(annotations, annotations.Offset, True)
    annotations[['Sentence', 'The_Sentence']] = pd.DataFrame(list(annotations['Offset'].map(lambda x: nlp.get_sentence_number(sentences_spans, x))))

    return annotations, article_body

# test
i = 0
with open(settings.PATH_ARTICLES, 'rb') as a:
    for article in data.iter_annotations(a):
        i += 1
        if i == 578:
            print(article.page_name)
            G = search(article, article.to_string())
            break
