
import os
import json
import nlp_util as nlp
import pandas as pd


def get_annotations(article, confidence):

    annotations = pd.DataFrame(columns=['Mention', 'EntityID', 'Offset', 'Sentence'], dtype='unicode', index=None)

    sentences_spans = []
    tokenized_sents = nlp.get_sentences(article)
    for sentence in nlp.get_sentences_spans(article, tokenized_sents):
        sentences_spans.append(sentence)

    query = r'curl http://model.dbpedia-spotlight.org/en/annotate --data-urlencode "text={}" --data "confidence={}" -H "Accept: application/json"'.format(article, confidence)

    data = json.loads(os.popen(query).read())

    for entity in data['Resources']:
        annotations.loc[len(annotations.index)] = [entity['@surfaceForm'],
                  entity['@URI'][28:],
                  entity['@offset'],
                  nlp.get_sentence_number(sentences_spans, int(entity['@offset']))]

    return annotations


# test
txt = 'President Obama called Wednesday on Congress to extend the tax break. Afterwards he met his wife Michelle'

G = get_annotations(txt, 0.35)

