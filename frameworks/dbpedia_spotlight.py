
import os
import json
import nlp_util as nlp
import pandas as pd


def annotate(text, confidence):

    annotations = pd.DataFrame(columns=['Mention', 'EntityID',
                                        'Offset', 'Sentence', 'The_Sentence'],
                               dtype='unicode', index=None)

    sentences_spans = []
    tokenized_sents = nlp.get_sentences(text)
    for sentence in nlp.get_sentences_spans(text, tokenized_sents):
        sentences_spans.append(sentence)

    query = r'curl http://model.dbpedia-spotlight.org/en/annotate --data-urlencode "text={}" --data "confidence={}" -H "Accept: application/json"'.format(text, confidence)

    data = json.loads(os.popen(query).read())

    for entity in data['Resources']:
        sentence_num, sentence_txt = nlp.get_sentence_number(
                sentences_spans, int(entity['@offset']))

        annotations.loc[len(annotations.index)] = [entity['@surfaceForm'],
                                                   entity['@URI'][28:],
                                                   entity['@offset'],
                                                   sentence_num,
                                                   sentence_txt]
    return annotations


def get_annotations(gold_standard):

    # Check entity ID

    annotations = pd.DataFrame(columns=['Article', 'Mention', 'EntityID',
                                        'Offset', 'Sentence', 'The_Sentence'],
                               dtype='unicode', index=None)

    for article in gold_standard:
        print(article.title)
        in_article = 0
        article_paragraphs = nlp.get_paragraphs(article.text)
        for paragraph in article_paragraphs:
            article_annotations = annotate(paragraph, 0.35)
            article_annotations['Article'] = article.title
            article_annotations['Sentence'] = article_annotations['Sentence'].map(lambda x: x + in_article)
            annotations = annotations.append(article_annotations)
            in_article += len(article_annotations)

        return annotations

# test

# iteate and query per paragrtaph
# TODO

txt = r'''President Obama called Wednesday on Congress to extend the tax break. \n Afterwards he met his wife Michelle'''

G = annotate('title', txt, 0.35)
