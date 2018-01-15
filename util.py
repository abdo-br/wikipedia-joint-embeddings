
import urllib
import settings
import read_data as data
import pandas as pd
from enum import Enum


class Level(Enum):
    Linked_Entity = 1
    Mentions = 2  # mentions of article & mentions of article entities
    Invalid = 3

# return a valid file name dictionary
def valid_filename():
    return str.maketrans('', '', r'<>:"/\|?*')


def sorted_dataframe(dataframe, key, ASC=True):
    # sort dataframe
    dataframe.index = key
    dataframe = dataframe.sort_index(ascending=ASC).reset_index(drop=True)
    return dataframe


def get_article(title):

    pages = data.AnnotationsFile(settings.PATH_ARTICLES)
    page = pages.get(str.encode(title.replace(' ', '%20'), encoding='utf-8'))
    return page


def get_entities(chunks=False):  # we need to clean redirects
    """
    Get all linked entities
    """
    if chunks:
        entities = pd.DataFrame()
        for chunk in pd.read_csv(settings.PATH_ENTITIES_ARTICLES, sep=' ',
                                 header=None, index_col=False, dtype='unicode',
                                 chunksize=5000000):
            entities = entities.append(chunk)

        entities = entities.drop(entities.columns[[1, 3]], axis=1)
        entities = entities.rename(columns={0: 'article', 2: 'entity'})
        entities['entity'] = entities['entity'].apply(lambda x: urllib.parse.unquote(str(x), encoding='utf-8', errors='replace'))

        return entities

    else:
        return None


def get_paragraphs():
    """
    Get all paragraphs
    """
    paragraphs = pd.read_csv(settings.PATH_PARAGRAPHS_ARTICLES, sep=' ',
                             header=None, index_col=False, dtype='unicode')
    paragraphs = paragraphs.drop(paragraphs.columns[[1, 3]], axis=1)
    paragraphs.rename(columns={0: 'article', 2: 'paragraph'}, inplace=True)

    return paragraphs
