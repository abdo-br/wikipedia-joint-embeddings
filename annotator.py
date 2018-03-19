
import re
import util
import nlp_util as nlp
import pandas as pd
from functools import reduce

Middle = ''
Original = ''
Final = ''

error_articles = []

def initialize_knowledgebase():
    # entities is a dict
    global entities, all_mentions, most_freq
    entities = util.get_entities()
    print('Entities Loading!')
    entities = util.split_dataframe(entities, col='article')
    print('Entities Dictionary Built!')
    all_mentions = util.get_mentions()
    print('Mentions Dictionary Loaded!')
    most_freq = util.get_most_freq_entities()
    #most_freq.set_index('mention', inplace=True)
    print('Most Frequent Entities Dictionary Loaded!')


# for evaluation
def get_annotations(gold_standard):

    entities = util.get_entities()
    all_mentions = util.get_mentions()
    global most_freq
    most_freq = util.get_most_freq_entities()

    annotations = pd.DataFrame(columns=['article', 'mention', 'entity',
                                        'entity_id', 'offset', 'sentence',
                                        'the_sentence'], dtype='unicode', index=None)

    for article in gold_standard.articles:

        print(article.title)

        anno = pd.DataFrame(columns=['article', 'mention', 'entity',
                                            'entity_id', 'offset', 'sentence',
                                            'the_sentence'], dtype='unicode', index=None)

        # search for mentions of the article entities

        article_entities = entities.loc[entities.article == article.title.replace(' ', '%20'), 'entity']

        mentions = []

        try:
            mentions.extend(map(all_mentions.get, article_entities))
            mentions = filter(None, mentions)
            mentions = reduce(lambda x,y: x+y, mentions)
        except:
            pass

        mentions = sorted(mentions, key=len)[::-1]

        for mention in mentions:
            for match in re.finditer(r'\b{}\b'.format(re.escape(mention)), article.text):
                entity = disambiguate(None, match.group())
                anno.loc[len(anno.index)] = [article.title, match.group(), entity, nlp.get_entity_id(entity), match.start(), -1, None]

        # map offsets to sentences
        sentences_spans = []
        tokenized_sents = nlp.get_sentences(article.text)
        for sentence in nlp.get_sentences_spans(article.text, tokenized_sents):
            sentences_spans.append(sentence)

        anno = util.sorted_dataframe(anno, anno.offset, True)
        anno[['sentence', 'the_sentence']] = pd.DataFrame(list(anno['offset'].map(lambda x: nlp.get_sentence_number(sentences_spans, x))))

        annotations = annotations.append(anno)

    return annotations


def disambiguate(text, mention):
    # naive approach
    # most frequent entity given mention
    try:
        #entity = most_freq.loc[mention, 'entity']
        entity = most_freq[mention]
        return entity
    except:
        return mention


def advanced_search(article_name, text, article_entities):  # expect clean text

    annotations = pd.DataFrame(columns=['article', 'level', 'mention',
                                        'used_entity', 'entity', 'entity_id',
                                        'offset'], dtype='unicode', index=None)

    # clean article
    article_body = text

    #global Middle
    #Middle = article_body

    # search for mentions of the article entities

    mentions = pd.merge(article_entities.to_frame(), all_mentions, how='inner', on='entity')['mention']
    mentions = util.sorted_dataframe(mentions, mentions.str.len(), ASC=False)

    ''' old approach
    mentions = []
    for entity in article_entities:
        try:
            mentions.extend(all_mentions[entity])
        except:
            continue

    #mentions.extend(annotations['mention'].values)

    #mentions = list(set(mentions))
    mentions = sorted(mentions, key=len)[::-1]
    '''

    regex_input = article_body
    for mention in mentions:
        for match in re.finditer(re.escape(mention), regex_input):
            entity = disambiguate(None, match.group())
            entity_id = nlp.get_entity_id(entity)
            annotations.loc[len(annotations.index)] = [article_name, util.Level(2).name, match.group(), entity, entity, entity_id, match.start()]

    # fix other mentions offsets
    # work on copy of annotations
    rows = annotations[['mention', 'offset']].copy(deep=True)
    annotations['ori_offset'] = annotations['offset']

    for index, annotation in annotations.iterrows():
        for i, row in rows.iterrows():
            if row['offset'] < annotation['ori_offset']:
                annotations.loc[index, 'offset'] += 32 - len(row['mention'])

    # sort by offset
    annotations = util.sorted_dataframe(annotations, annotations['offset'], True)

    # reconstruct the article
    for row in annotations.itertuples():
        article_body = nlp.replace_part_of_text(article_body, row.entity_id, row.offset, len(row.mention))

    return annotations, article_body


def search(article_name, text, article_entities):

    article_body = text

    #mentions = all_mentions.loc[all_mentions.entity.isin(article_entities), 'mention']
    #mentions = all_mentions.query('entity in @article_entities')['mention']

    #mentions = pd.merge(article_entities.to_frame(), all_mentions, how='inner', on=['entity'])['mention']
    #mentions = util.sorted_dataframe(mentions, mentions.str.len(), ASC=False)

    mentions = []

    try:
        mentions.extend(map(all_mentions.get, article_entities))
        mentions = filter(None, mentions)
        mentions = reduce(lambda x,y: x+y, mentions)
    except:
        pass

    #mentions = list(set(mentions))
    mentions = sorted(mentions, key=len)[::-1]

    for mention in mentions:
        entity = disambiguate(None, mention)
        entity_id = nlp.get_entity_id(entity)
        article_body = re.sub(r'\b{}\b'.format(re.escape(mention)), ' '+entity_id+' ', article_body)

    return article_body


def annotate(article, and_search=True):

    annotations = pd.DataFrame(columns=['article', 'level', 'mention',
                                        'used_entity', 'entity', 'entity_id',
                                        'offset'], dtype='unicode', index=None)

    #global Original
    #Original = article.to_string()

    # find linked entities
    # get linked entities within the article
    try:

        article_entities = entities[article.page_id]

        article_body = article.to_string()

    except:

        #error_articles.append(article)
        return None, None

    # invalid entities
    regex_input = article_body
    for entity in article_entities.loc[article_entities.valid == 'False', 'used_entity']:
        for pair in re.finditer(nlp.get_entity_pattern(entity), regex_input):

            try:
                mention, target = pair.group()[1:].split(']')
                article_body = article_body.replace(pair.group(), mention)

            except Exception as e:
                pass

    # valid entities
    regex_input = article_body
    for entity in article_entities.loc[article_entities.valid == 'True', 'used_entity']:
        for pair in re.finditer(nlp.get_entity_pattern(entity), regex_input):

            try:
                values = pair.group()[1:].split(']')
                mention = values[0]
                entity = values[1][1:-1]
                # resolve redirect
                resolved = article_entities.loc[article_entities.used_entity == entity, 'entity'].values[0]
                entity_id = nlp.get_entity_id(resolved)
                annotations.loc[len(annotations.index)] = [article.page_name, util.Level(1).name, mention, entity, resolved, entity_id, pair.start()]
                article_body = article_body.replace(pair.group(), entity_id)

            except Exception as e:
                pass

    if and_search:
        # search for more entities
        article_body = search(article.page_name, article_body, annotations['entity'].drop_duplicates())
        #annotations = annotations.append(search_annotations)

    #global Final
    #Final = article_body

    article_body = nlp.clean_article(article_body)

    try:
        print(article.page_name)
    except:
        pass

    # to build the IDs dict
    return annotations[['entity', 'entity_id']], article_body
