# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 03:07:45 2018

@author: Abdulrahman Bres
"""

import json
import requests
import nlp_util as nlp
import pandas as pd
import gold_standard as gs


def annotate(token, text, epsilon):

    annotations = pd.DataFrame(columns=['mention', 'entity', 'entity_id',
                                        'offset', 'sentence', 'the_sentence'],
                               dtype='unicode', index=None)

    sentences_spans = []
    tokenized_sents = nlp.get_sentences(text)
    for sentence in nlp.get_sentences_spans(text, tokenized_sents):
        sentences_spans.append(sentence)

    parameters = {'lang': 'en', 'gcube-token': token, 'text': text, 'epsilon': epsilon, 'long_text': '0'}
    query = r'https://tagme.d4science.org/tagme/tag'

    result = requests.post(query, data=parameters)

    data = json.loads(result.text)

    for annotation in data['annotations']:

        if 'title' not in annotation:
            continue

        sentence_num, sentence_txt = nlp.get_sentence_number(
                sentences_spans, int(annotation['start']))

        entity = annotation['title']

        annotations.loc[len(annotations.index)] = [annotation['spot'],
                                                   entity,
                                                   nlp.get_entity_id(entity),
                                                   annotation['start'],
                                                   sentence_num,
                                                   sentence_txt]
    return annotations


def get_annotations(gold_standard):

    annotations = pd.DataFrame(columns=['article', 'mention', 'entity', 'entity_id',
                                        'offset', 'sentence', 'the_sentence'],
                               dtype='unicode', index=None)

    token = '<token>'

    for article in gold_standard.articles:

        print(article.title)
        in_article = 0
        article_paragraphs = nlp.get_paragraphs(article.text)
        for paragraph in article_paragraphs:
            article_annotations = annotate(token, paragraph, 0.3)
            article_annotations['article'] = article.title
            article_annotations['sentence'] = article_annotations['sentence'].map(lambda x: x + in_article)
            annotations = annotations.append(article_annotations)
            in_article += len(article_annotations)

    return annotations

#gold_std = gs.gold_standard()
#annotations = get_annotations(gold_std)

#annotations.to_csv('/home/abres/output/tagme.csv', chunksize=10000, encoding='utf-8', index=False)
