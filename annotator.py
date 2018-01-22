
import re
import util
import pickle
import nlp_util as nlp
import read_data as data
import pandas as pd
import settings

Middle = ''
Original = ''
Final = ''


def initialize_knowledgebase():
    global entities, graph, stats
    entities = util.get_entities(chunks=True)

#graph = pd.read_hdf(settings.PATH_DATAOBJECTS+'6456.hdf5', key='')
#stats = graph.groupby(by=['entity', 'mention'], sort=False).count()
#stats = stats.rename(columns={'article':'freq'})

#stats = pd.read_pickle(settings.PATH_DATAOBJECTS+'entities_mentions_graph.gzip', compression='gzip')
#stats.reset_index(level=0, inplace=True)
#stats.reset_index(inplace=True)

# temporary fix  !!!!!!!!!!!!!!!!!!!
#stats = stats.rename(columns={'Article':'freq', 'Mention':'mention', 'Entity':'entity'})
#graph = graph.rename(columns={'Article':'article', 'Mention':'mention', 'Entity':'entity'})


# for evaluation
def get_annotations(gold_standard):

    tokenizer = pickle.load(open(settings.PATH_DATAOBJECTS + settings.FILE_TOKENIZER, 'rb'))
    annotations = pd.DataFrame(columns=['Article', 'Mention', 'Entity',
                                        'EntityID', 'Offset', 'Sentence',
                                        'The_Sentence'], dtype='unicode', index=None)

    for article in gold_standard.articles:

        # search for mentions of the article
        # and for mentions of the article entities

        # article rows
        rows = graph.loc[graph.article == article.title]
        # mentions of article
        #article_mentions = rows['mention']
        # entities of article
        #article_entities = rows['entity']

        mentions = stats.loc[stats.entity.isin(rows['entity']), 'mention']

        mentions = mentions.append(rows['mention'])
        mentions.drop_duplicates(inplace=True)
        mentions = util.sorted_dataframe(mentions, mentions.str.len(), False)

        # TODO
        # stem the mentions

        for mention in mentions:
            for match in re.finditer(re.escape(mention), article.text):
                entity = disambiguate(None, match.group())
                annotations.loc[len(annotations.index)] = [article.title, match.group(), entity, nlp.get_entity_id(entity), match.start(), -1, None]

        # map offsets to sentences
        sentences_spans = []
        tokenized_sents = nlp.get_sentences(article.text, tokenizer)
        for sentence in nlp.get_sentences_spans(article.text, tokenized_sents):
            sentences_spans.append(sentence)

        annotations = util.sorted_dataframe(annotations, annotations.Offset, True)
        annotations[['Sentence', 'The_Sentence']] = pd.DataFrame(list(annotations['Offset'].map(lambda x: nlp.get_sentence_number(sentences_spans, x))))

        return annotations


def disambiguate(text, mention):
    # naive approach
    # most_frequent_entity
    entity = stats.at[stats.loc[stats.mention == mention, 'freq'].idxmax(axis=0), 'entity']

    return entity

def search(article_name, text):  # expect clean text

    annotations = pd.DataFrame(columns=['Article', 'Level', 'Mention',
                                        'Used_Entity', 'Entity', 'EntityID',
                                        'Offset'], dtype='unicode', index=None)

    # cleaned article
    article_body = text

    global Middle
    Middle = article_body

    # search for mentions of the article
    # and for mentions of the article entities

    # article rows
    rows = graph.loc[graph.article == article.page_name]
    # mentions of article
    #article_mentions = rows['mention']
    # entities of article
    #article_entities = rows['entity']

    mentions = stats.loc[stats.entity.isin(rows['entity']), 'mention']

    mentions = mentions.append(rows['mention'])
    mentions.drop_duplicates(inplace=True)
    mentions = util.sorted_dataframe(mentions, mentions.str.len(), False)

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


def annotate(article, search=False):

    annotations = pd.DataFrame(columns=['Article', 'Level', 'Mention',
                                        'Used_Entity', 'Entity', 'EntityID',
                                        'Offset'], dtype='unicode', index=None)

    # clean on the content
    article_body = nlp.get_clean_article(article.to_string())

    #global Original
    #Original = article_body

    # find linked entities
    # get linked entities within the article
    article_entities = entities.loc[entities.article == article.page_id]

    article_entities['valid'] = None
    article_entities['valid'] = article_entities['entity'].map(lambda x: not nlp.invalid_entity(x))

    # process invalid entities
    regex_input = article_body
    for entity in article_entities.loc[article_entities.valid == False, 'entity']:
        for pair in re.finditer(nlp.get_entity_pattern(entity), regex_input):
            mention, target = pair.group()[1:].split(']')
            article_body = article_body.replace(pair.group(), mention)

    # valid entities
    regex_input = article_body
    for entity in article_entities.loc[article_entities.valid == True, 'entity']:
        for pair in re.finditer(nlp.get_entity_pattern(entity), regex_input):
            mention, entity = pair.group()[1:].split(']')
            entity = entity[1:-1]
            #erd = nlp.resolve_redirect(entity)  !!!!!!!!!!!!!!!!!!!!!!!!!
            entity_id = nlp.get_entity_id(entity)
            annotations.loc[len(annotations.index)] = [article.page_name, util.Level(1).name, mention, entity, entity, entity_id, pair.start()]
            article_body = article_body.replace(pair.group(), entity_id)

    if search:
        # search for more entities
        search_annotations, article_body = search(article.page_name, article_body)
        annotations = annotations.append(search_annotations)

    #global Final
    #Final = article_body

    return annotations, article_body
