
import re
import uuid
import json
import string
import requests
from nltk import sent_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer


ENTITY_PATTERN = r'\[[^\[\]]*?\](?=\([^\[]+?\))\(.*?((?=\()\(.+?\).*?|[^\(\)]+?)\)'


def get_entity_pattern(entity):
    # [mention](entity)
    p = re.escape(str(entity))
    return ''.join([r'\[[^\[\]]*?\](?=\(', p, r'\))\(', p, r'\)'])


def resolve_redirect(entity):

    query = requests.get(r'https://en.wikipedia.org/w/api.php?action=query&titles={}&&redirects&format=json'.format(entity))
    data = json.loads(query.text)

    try:
        for item in data['query']['redirects']:
            return item['to']

    except Exception as e:
        if e.args[0] == 'redirects':
            return ''
        else:
            return '~ERROR'


def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))


def remove_part_from_text(text, start, length):
    return text[:start] + text[start+length:]


def replace_part_of_text(text, new_part, start, length):
    return text[:start] + new_part + text[start+length:]


def zip_whitespaces(text):
    return re.sub(' +', ' ', text)


def zip_emptylines(text):
    return re.sub(r'\n+(?=\n)', '\n', text)


def clean_article(article_body):

    # remove sections titles and refs and qutations
    article_body = re.sub(r'(<ref.+?>)|([\']+[\s\.,;])|([\s][\']+)|(\")', ' ', article_body)
    article_body = re.sub(r'[=]+\s.+\s[=]+', '', article_body)

    # separate sentences
    article_body = re.sub(r'(?<=[0-9a-z\"])\.(?=[A-Z])|\.(?=[0-9a-z]{32})', '. ', article_body)

    # zip text
    article_body = zip_whitespaces(article_body)
    article_body = zip_emptylines(article_body)
    article_body = article_body.strip('\n')

    return article_body


def get_sentences(text):
    return sent_tokenize(text, language='english')


def get_paragraphs(text):
    return text.split('\n\n')


# get sentences with their offsets
def get_sentences_spans(text, sentences):
    offset = 0
    for s in sentences:
        offset = text.find(s, offset)
        yield s, offset, offset+len(s)
        offset += len(s)


# map mention offset to sentence number
def get_sentence_number(sentences_spans, offset):
    i = 1
    for sp in sentences_spans:
        if offset >= sp[1] and offset <= sp[2]:
            return i, sp[0]
        i += 1


def get_entity_id(entity):
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, entity)).replace('-', '')
