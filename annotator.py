
import re
import util
import nlp_util as nlp
import pandas as pd

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
    most_freq.set_index('mention', inplace=True)
    print('Most Frequent Entities Loaded!')


# for evaluation
def get_annotations(gold_standard):

    annotations = pd.DataFrame(columns=['Article', 'Mention', 'Entity',
                                        'EntityID', 'Offset', 'Sentence',
                                        'The_Sentence'], dtype='unicode', index=None)

    for article in gold_standard.articles:

        # search for mentions of the article
        # and for mentions of the article entities

        article_entities = entities[article.page_id]

        mentions = []
        for entity in article_entities['entity']:
            try:
                mentions.extend(all_mentions[entity])
            except:
                continue

        mentions = sorted(mentions, key=len)[::-1]

        for mention in mentions:
            for match in re.finditer(re.escape(mention), article.text):
                entity = disambiguate(None, match.group())
                annotations.loc[len(annotations.index)] = [article.title, match.group(), entity, nlp.get_entity_id(entity), match.start(), -1, None]

        # map offsets to sentences
        sentences_spans = []
        tokenized_sents = nlp.get_sentences(article.text)
        for sentence in nlp.get_sentences_spans(article.text, tokenized_sents):
            sentences_spans.append(sentence)

        annotations = util.sorted_dataframe(annotations, annotations.Offset, True)
        annotations[['Sentence', 'The_Sentence']] = pd.DataFrame(list(annotations['Offset'].map(lambda x: nlp.get_sentence_number(sentences_spans, x))))

        return annotations


def disambiguate(text, mention):
    # naive approach
    # most frequent entity given mention
    try:
        entity = most_freq.loc[(mention,)].values[0]
        return entity
    except:
        return mention


def search(article_name, text):  # expect clean text

    annotations = pd.DataFrame(columns=['Article', 'Level', 'Mention',
                                        'Used_Entity', 'Entity', 'EntityID',
                                        'Offset'], dtype='unicode', index=None)

    # clean article
    article_body = text

    #global Middle
    #Middle = article_body

    # search for mentions of the article
    # and mentions of the article entities

    mentions = []
    for entity in annotations['Entity']:
        try:
            mentions.extend(all_mentions[entity])
        except:
            continue

    #mentions.extend(annotations['Mention'].values)

    #mentions = list(set(mentions))
    mentions = sorted(mentions, key=len)[::-1]

    # TODO
    # stem the mentions

    regex_input = article_body
    for mention in mentions:
        for match in re.finditer(re.escape(mention), regex_input):
            entity = disambiguate(None, match.group())
            entity_id = nlp.get_entity_id(entity)
            annotations.loc[len(annotations.index)] = [article_name, util.Level(2).name, match.group(), entity, entity, entity_id, match.start()]

    # fix other mentions offsets
    # work on copy of annotations
    rows = annotations[['Mention', 'Offset']].copy(deep=True)
    annotations['Ori_Offset'] = annotations['Offset']

    for index, annotation in annotations.iterrows():
        for i, row in rows.iterrows():
            if row['Offset'] < annotation['Ori_Offset']:
                annotations.loc[index, 'Offset'] += 32 - len(row['Mention'])

    # sort by offset
    annotations = util.sorted_dataframe(annotations, annotations['Offset'], True)

    # reconstruct the article
    for row in annotations.itertuples():
        article_body = nlp.replace_part_of_text(article_body, row.EntityID, row.Offset, len(row.Mention))

    return annotations, article_body


def annotate(article, and_search=True):

    annotations = pd.DataFrame(columns=['Article', 'Level', 'Mention',
                                        'Used_Entity', 'Entity', 'EntityID',
                                        'Offset'], dtype='unicode', index=None)

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

    # process invalid entities
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
        search_annotations, article_body = search(article.page_name, article_body)
        annotations = annotations.append(search_annotations)

    #global Final
    #Final = article_body

    article_body = nlp.clean_article(article_body)

    # to build the IDs dict
    return annotations[['Entity', 'EntityID']], article_body
