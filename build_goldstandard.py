# -*- coding: utf-8 -*-
"""
@author: Abdulrahman Bres
"""

import re
import util
import pickle
import settings
import nlp_util as nlp
import pandas as pd


# load articles & entities
entities = util.get_entities(chunks=True)
entities.set_index(['article', 'entity'], inplace=True)
articles = pickle.load(open(settings.PATH_DATAOBJECTS + settings.FILE_GOLD_STANDARD_ARTICLES, 'rb'))
tokenizer = pickle.load(open(settings.PATH_DATAOBJECTS + settings.FILE_TOKENIZER, 'rb'))

gold_standard = pd.DataFrame(columns=['Article', 'Mention', 'Used_Entity', 'Entity', 'EntityID', 'Offset', 'Sentence', 'The_Sentence'], dtype='unicode', index=None)


def annotate(article):

    annotations = pd.DataFrame(columns=['Article', 'Level', 'Mention', 'Used_Entity', 'Entity', 'EntityID', 'Offset', 'Sentence', 'The_Sentence'], dtype='unicode', index=None)

    # clean on the content
    article_body = nlp.get_clean_article(article.to_string())

    # find the linked entities
    # get the linked entities within the article

    article_entities = entities.loc[(article.page_id,)].index

    regex_input = article_body
    for entity in article_entities:
        for pair in re.finditer(nlp.get_entity_pattern(entity), regex_input):
            mention, entity = pair.group()[1:].split(']')
            entity = entity[1:-1]
            if nlp.invalid_entity(entity):
                annotations.loc[len(annotations.index)] = [article.page_name, util.Level(3).name, mention, entity, entity, None, pair.start() , -1, None]
                article_body = article_body.replace(pair.group(), '☲' * len(mention))
            else:
                erd = nlp.resolve_redirect(entity)
                if erd == '~ERROR':
                    continue
                if erd == '':
                    erd = entity
                annotations.loc[len(annotations.index)] = [article.page_name, util.Level(1).name, mention, entity, erd, nlp.get_entity_id(erd), pair.start(), -1, None]
                article_body = article_body.replace(pair.group(), '☰' * len(mention))


    # fix the other mentions offsets
    # work on copy of annotations
    rows = annotations[['Used_Entity', 'Offset']].copy(deep=True)
    annotations['Ori_Offset'] = annotations['Offset']

    for index, annotation in annotations.iterrows():
        for i, row in rows.iterrows():
            if row['Offset'] < annotation['Ori_Offset']:
                annotations.loc[index, 'Offset'] -= len(row['Used_Entity']) + 4

    # reconstruct the article
    for row in annotations.itertuples():
        article_body = nlp.replace_part_of_text(article_body, row.Mention, row.Offset, len(row.Mention))

    # map offsets to sentences
    sentences_spans = []
    tokenized_sents = nlp.get_sentences(article_body, tokenizer)
    for sentence in nlp.get_sentences_spans(article_body, tokenized_sents):
        sentences_spans.append(sentence)

    # filtre out invalid enitites
    # drop Level column
    annotations = annotations.loc[annotations.Level != util.Level(3).name]
    annotations = annotations.drop(['Level'], axis=1)

    annotations = util.sorted_dataframe(annotations, annotations.Offset, True)
    annotations[['Sentence', 'The_Sentence']] = pd.DataFrame(list(annotations['Offset'].map(lambda x: nlp.get_sentence_number(sentences_spans, x))))

    return annotations, article_body


#import read_data as data
#i = 1
#with open(settings.PATH_ARTICLES, 'rb') as a:
#    for article in data.iter_annotations(a):
#        i += 1
#        if i == 253:
#            print(article.page_name)
#            gs, body = annotate(article)
#
#            with open(settings.PATH_GOLD_STANDARD +
#                      article.page_name.translate(util.valid_filename()) +
#                      '.txt', 'w', encoding='utf-8') as b:
#
#                b.write(body)
#
#            gold_standard = gold_standard.append(gs)

for article in articles:
    print(article.page_name)
    gs, body = annotate(article)

    with open(settings.PATH_GOLD_STANDARD +
              article.page_name.translate(util.valid_filename()) +
              '.txt', 'w', encoding='utf-8') as b:

        b.write(body)

    gold_standard = gold_standard.append(gs)

# save the gold standard as csv
gold_standard.to_csv(settings.PATH_GOLD_STANDARD + settings.FILE_GOLD_STANDARD, encoding='utf-8', index=False)
