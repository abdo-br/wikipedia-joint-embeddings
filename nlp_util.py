
import re
import uuid
import string
from nltk import sent_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer


ENTITY_PATTERN = r'\[[^\[\]]*?\](?=\([^\[]+?\))\(.*?((?=\()\(.+?\).*?|[^\(\)]+?)\)'


def get_entity_pattern(entity):
    return r'\[[^\[\]]*?\](?=\(' + re.escape(entity) + r'\))\(' + re.escape(entity) + r'\)'


def invalid_entity(entity):

    if entity.startswith('Wikt:'): return True
    if entity.startswith('Category:'): return True
    if entity.startswith('List of'): return True
    if entity.startswith(':v:'): return True
    if r'<!--Is this correct?-->' in entity: return True

    return False


def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))


# delete a slice from text
def remove_part_from_text(text, start, length):
    return text[:start] + text[start+length:]


# replace a slice in text
def replace_part_of_text(text, new_part, start, length):
    return text[:start] + new_part + text[start+length:]


def get_clean_article(article_body):

    # remove sections titles and refs
    article_body = re.sub(r'[=]+\s.+\s[=]+', '', article_body)  # remove sections titles
    article_body = re.sub(r'<ref.*>', ' ', article_body)  # remove refs
    # separate paragraphs with a space
    article_body = re.sub(r'\.(?=[\[A-Z])', '. ', article_body)
    # clean the bold or italic words
    article_body = article_body.replace('\'\'', '')
    article_body = re.sub(r'\n+(?=\n)', '\n', article_body)  # zip empty lines
    article_body = article_body.strip('\n')

    return article_body


def trained_punkt_tokenizer(text):
    tokenizer = PunktSentenceTokenizer()
    tokenizer.train(get_clean_article(text))

    return tokenizer


def get_sentences(text, tokenizer=None):
    if tokenizer is None:
        return sent_tokenize(text, language='english')
    else:
        return tokenizer.tokenize(text)


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
