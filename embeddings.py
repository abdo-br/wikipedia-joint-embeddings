
import util
import time
import settings
import read_data as data
import logging
import gensim
import pandas as pd
import nlp_util as nlp
import annotator
import cProfile

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class Sentences():

    def __iter__(self):

        i = 0

        dectionary = pd.DataFrame(columns=['Entity', 'EntityID'], dtype='unicode', index=None)

        with open(settings.PATH_ARTICLES, 'rb') as a:

            for article in data.iter_annotations(a):

                i += 1
                #outPath = settings.PATH_OUTPUT + article.page_name.translate(util.valid_filename())

                annotations, article_body = annotator.annotate(article, search=False)
                dectionary = dectionary.append(annotations[['Entity', 'EntityID']])

                # tokenize and yield sentences
                sentences = nlp.get_sentences(article_body)
                for sentence in sentences:
                    sentence = nlp.remove_punctuation(sentence)
                    yield sentence.split()

                # save the article
#                with open(outPath, 'w', encoding='utf-8') as b:
#                    b.write(article_body)

                #if settings.NUM_ARTICLES != -1 and i > settings.NUM_ARTICLES:
                if settings.NUM_ARTICLES != -1 and i > 1000000:
                    break

        # save dictionary of entities IDs
        dectionary.to_pickle(settings.PATH_DATAOBJECTS+'w2v/entities_dectionary.pickle', compression='gzip')


def build(min_frequency, dimensions, num_workers):
    corpus = Sentences()
    #bigram_transformer = gensim.models.Phrases(corpus)
    #bigram_transformer[corpus]
    model = gensim.models.Word2Vec(sentences=corpus,
                                   size=dimensions, min_count=min_frequency,
                                   workers=num_workers)
    return model


tic = time.time()

w2v_model = build(2, 50, 12)
w2v_model.save(settings.PATH_DATAOBJECTS + 'w2v/model_%s__%s' % (50, time.strftime('%d-%m-%Y')))


def ptest():
    i = 0
    for item in Sentences():
        i += 1
    return i

#r = cProfile.run('ptest()')

toc = time.time()
print('Done!')
print((toc-tic) % 60)

#w2v_model.wv.index2word
#len(w2v_model.wv.vocab)
#w2v_model.most_similar(['help'])
