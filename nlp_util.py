
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
    p = re.escape(entity)
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

def invalid_entity(entity):

    if entity.startswith(':'): return True
    if entity.startswith('List of'): return True
    if entity.startswith('Wikipedia:'): return True
    if entity.startswith('Category:'): return True
    if entity.startswith('Wikisource:'): return True
    if entity.startswith('MediaWiki:'): return True
    if entity.startswith('Wiktionary:'): return True
    if entity.startswith('Wikt:'): return True
    if entity.startswith('Wikiasite:'): return True
    if entity.startswith('Help:'): return True
    if entity.startswith(':wiktionary'): return True
    if entity.startswith(':wikt'): return True
    if entity.startswith('Commons:'): return True
    if entity.startswith('File:'): return True
    if entity.startswith('Image:'): return True
    if entity.startswith('Template:'): return True
    if entity.startswith('Portal:'): return True
    if entity.startswith('Module:'): return True
    if entity.startswith('Special:'): return True
    if entity.startswith('User:'): return True
    if entity.startswith('Project:'): return True
    if entity.startswith('Book:'): return True
    if entity.startswith('WP:'): return True

    return False


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


def get_clean_article(article_body):

    # remove sections titles and refs
    article_body = re.sub(r'[=]+\s.+\s[=]+', '', article_body)
    article_body = re.sub(r'<ref.*>', ' ', article_body)
    # clean the bold or italic words
    article_body = article_body.replace('\'\'', '')
    article_body = zip_emptylines(article_body)  # zip empty lines
    article_body = zip_whitespaces(article_body)
    article_body = article_body.strip('\n')

    return article_body


def trained_punkt_tokenizer(corpus):  # list
    tokenizer = PunktSentenceTokenizer()
    for a in iter(corpus):
        tokenizer.train(a)

    return tokenizer


def get_sentences(text, tokenizer=None):
    if tokenizer is None:
        return sent_tokenize(text, language='english')
    else:
        return tokenizer.tokenize(text)


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
