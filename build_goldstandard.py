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
entities = util.get_entities()
print('Entities Loaded!')

articles = pickle.load(open(settings.PATH_KB + 'gs_articles.pickle', 'rb'))

gold_standard = pd.DataFrame(columns=['article', 'mention', 'used_entity', 'entity', 'entity_id', 'offset', 'sentence', 'the_sentence'], dtype='unicode', index=None)


def annotate(article):

    annotations = pd.DataFrame(columns=['article', 'level', 'mention', 'used_entity', 'entity', 'entity_id', 'offset', 'sentence', 'the_sentence'], dtype='unicode', index=None)

    article_entities = entities.loc[entities.article == article.page_id]

    if article_entities.empty:
        annotations = annotations.drop(['level'], axis=1)
        return annotations, article.to_string()

    article_body = article.to_string()

    article_body = nlp.get_paragraphs(article_body)
    del article_body[0]
    article_body = '\n\n'.join([p.strip() for p in article_body])
    article_body = nlp.clean_article(article_body)

    regex_input = article_body
    for index, entity_row in article_entities.iterrows():
        for pair in re.finditer(nlp.get_entity_pattern(entity_row['used_entity']), regex_input):
            mention, entity = pair.group()[1:].split(']')
            entity = entity[1:-1]
            if util.invalid_entity(entity):
                annotations.loc[len(annotations.index)] = [article.page_name, util.Level(3).name, mention, entity, entity, None, pair.start() , -1, None]
                article_body = article_body.replace(pair.group(), '☲' * len(mention))
            else:
                resolved = entity_row['entity']
                annotations.loc[len(annotations.index)] = [article.page_name, util.Level(1).name, mention, entity, resolved, nlp.get_entity_id(resolved), pair.start(), -1, None]
                article_body = article_body.replace(pair.group(), '☰' * len(mention))

    # fix other mentions offsets
    # work on copy of annotations
    rows = annotations[['used_entity', 'offset']].copy(deep=True)
    annotations['ori_offset'] = annotations['offset']

    for index, annotation in annotations.iterrows():
        for i, row in rows.iterrows():
            if row['offset'] < annotation['ori_offset']:
                annotations.loc[index, 'offset'] -= len(row['used_entity']) + 4

    # reconstruct the article
    for row in annotations.itertuples():
        article_body = nlp.replace_part_of_text(article_body, row.mention, row.offset, len(row.mention))

    # map offsets to sentences
    sentences_spans = []
    tokenized_sents = nlp.get_sentences(article_body)
    for sentence in nlp.get_sentences_spans(article_body, tokenized_sents):
        sentences_spans.append(sentence)

    # filtre out invalid enitites
    # drop Level column
    annotations = annotations.loc[annotations.level != util.Level(3).name]
    annotations = annotations.drop(['level'], axis=1)

    annotations = util.sorted_dataframe(annotations, annotations.offset, True)
    annotations[['sentence', 'the_sentence']] = pd.DataFrame(list(annotations['offset'].map(lambda x: nlp.get_sentence_number(sentences_spans, x))))

    return annotations, article_body


for article in articles:
    print(article.page_name)
    gs, body = annotate(article)

    with open(settings.PATH_GOLD_STANDARD +
              article.page_name.translate(util.valid_filename()) +
              '.txt', 'w', encoding='utf-8') as b:

        b.write(body)

    gold_standard = gold_standard.append(gs)

# save the gold standard as csv
gold_standard.to_csv(settings.PATH_GOLD_STANDARD + 'annotations.csv', encoding='utf-8', index=False)
