
import os
import json
import nlp_util as nlp
import pandas as pd
import gold_standard as gs


def annotate(text, confidence, support):

    annotations = pd.DataFrame(columns=['mention', 'entity', 'entity_id',
                                        'offset', 'sentence', 'the_sentence'],
                               dtype='unicode', index=None)

    sentences_spans = []
    tokenized_sents = nlp.get_sentences(text)
    for sentence in nlp.get_sentences_spans(text, tokenized_sents):
        sentences_spans.append(sentence)

    query = r'curl http://model.dbpedia-spotlight.org/en/annotate --data-urlencode "text={}" --data "confidence={}&support={}" -H "Accept: application/json"'.format(text, confidence, support)

    data = json.loads(os.popen(query).read())

    if 'Resources' not in data:
        return annotations

    for annotation in data['Resources']:
        sentence_num, sentence_txt = nlp.get_sentence_number(
                sentences_spans, int(annotation['@offset']))

        entity = annotation['@URI'][28:].replace('_', ' ')

        annotations.loc[len(annotations.index)] = [annotation['@surfaceForm'],
                                                   entity,
                                                   nlp.get_entity_id(entity),
                                                   annotation['@offset'],
                                                   sentence_num,
                                                   sentence_txt]
    return annotations


def get_annotations(gold_standard):

    annotations = pd.DataFrame(columns=['article', 'mention', 'entity', 'entity_id',
                                        'offset', 'sentence', 'the_sentence'],
                               dtype='unicode', index=None)

    for article in gold_standard.articles:
        print(article.title)
        in_article = 0
        article_paragraphs = nlp.get_paragraphs(article.text)
        for paragraph in article_paragraphs:
            article_annotations = annotate(paragraph, 0.6, 1)
            article_annotations['article'] = article.title
            article_annotations['sentence'] = article_annotations['sentence'].map(lambda x: x + in_article)
            annotations = annotations.append(article_annotations)
            in_article += len(article_annotations)

    return annotations

# test
#txt = r'''President Obama called Wednesday on Congress to extend the tax break. \n Afterwards he met his wife Michelle'''

#G = annotate(txt, 0.35, 0)

#gold_std = gs.gold_standard()
#annotations = get_annotations(gold_std)
