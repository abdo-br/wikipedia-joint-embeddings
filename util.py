
#import numba
import urllib
import pickle
import settings
import read_data as data
import numpy as np
import pandas as pd
import multiprocessing
from functools import partial
from threading import Thread
from enum import Enum


class Level(Enum):
    Linked_Entity = 1
    Mentions = 2  # mentions of article & mentions of article entities
    Invalid = 3


# return a valid file name dictionary
def valid_filename():
    return str.maketrans('', '', r'<>:"/\|?*')


# split dataframe into chunks saved in dict
def split_dataframe(df, col='hash'):
    d = dict(tuple(df.groupby(col)))
    return d


def sorted_dataframe(dataframe, key, ASC=True):
    # sort dataframe or series
    dataframe.index = key
    # sort then reset index and drop the sort one
    dataframe = dataframe.sort_index(ascending=ASC).reset_index(drop=True)
    return dataframe


def get_article(title):
    pages = data.AnnotationsFile(settings.PATH_ARTICLES)
    page = pages.get(str.encode(title.replace(' ', '%20'), encoding='utf-8'))
    return page


#@numba.jit
#def test_numba(col_a):
#   n = len(col_a)
#   result = np.empty(n, dtype=str)
#   for i in range(n):
#      result[i] = urllib.parse.unquote(str(col_a[i]), encoding='utf-8', errors='replace')
#
#   return result


#def decode_entity(df):
#
#    def f():
#        decode = lambda x: urllib.parse.unquote(str(x), encoding='utf-8', errors='replace')
#        df[2] = df[2].apply(decode)
#
#    t = Thread(target=f)
#    return (t, df)


def get_hash(value, n_buckets=11):
    h = str(ord(str(value)[0]) % n_buckets)
    return h


# decode percent-encoding
def decode_percent(value):
    decode = lambda x: urllib.parse.unquote(str(x), encoding='utf-8', errors='replace')
    return decode(value)


#def modify(df):
#    df['hash'] = df['article'].apply(get_hash)
#    df['valid'] = df['entity'].apply(lambda x: not invalid_entity(x))
#    return df

def get_most_freq_entities():
    return pickle.load(open(settings.PATH_BEST_ENTITIES, 'rb'))
#    chunks = pd.read_table(settings.PATH_BEST_ENTITIES, sep=',',
#                           header=0, index_col=False, dtype='unicode',
#                           chunksize=500000, low_memory=False, engine='c')
#
#    best_entities = pd.concat([chunk for chunk in chunks], ignore_index=True)
#
#    return best_entities


def get_mentions():
    return pickle.load(open(settings.PATH_MENTIONS, 'rb'))
#    chunks = pd.read_table(settings.PATH_MENTIONS, sep=',',
#                       header=0, index_col=False, dtype='unicode',
#                       chunksize=500000, low_memory=False, engine='c')
#
#    mentions = pd.concat([chunk for chunk in chunks], ignore_index=True)
#
#    return mentions[['mention', 'entity']]


def get_entities():  # we need to clean redirects
    """
    Get linked entities
    """
    chunks = pd.read_table(settings.PATH_ENTITIES_ARTICLES, sep=',',
                           header=0, index_col=False, dtype='unicode',
                           chunksize=500000, low_memory=False, engine='c')

# using threads
#    threads = [decode_entity(chunk) for chunk in chunks]
#
#    for t in threads:
#        t[0].start()
#
#    for t in threads:
#        t[0].join()
#        entities = entities.append(t[1])

# using pool
#    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 3)
#    entities = pd.concat(pool.map(modify, chunks))
#    pool.close()
#    pool.join()

    entities = pd.concat([chunk for chunk in chunks], ignore_index=True)
    #entities = entities.drop(entities.columns[[1, 3]], axis=1)
    #entities = entities.rename(columns={0: 'article', 2: 'entity'})

    return entities


def get_paragraphs():
    """
    Get paragraphs
    """
    paragraphs = pd.read_csv(settings.PATH_PARAGRAPHS_ARTICLES, sep=' ',
                             header=None, index_col=False, dtype='unicode')
    paragraphs = paragraphs.drop(paragraphs.columns[[1, 3]], axis=1)
    paragraphs.rename(columns={0: 'article', 2: 'paragraph'}, inplace=True)

    return paragraphs


def invalid_entity(entity):

    entity = str(entity).strip()
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
