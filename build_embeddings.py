
import time
import settings
import logging
import gensim
import process_articles as Wikipedia

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

t0 = time.time()


def build_embeddings(min_frequency, dimensions, num_workers):
    corpus = Wikipedia.Sentences()
    bigram_transformer = gensim.models.Phrases(corpus)
    model = gensim.models.Word2Vec(sentences=bigram_transformer[corpus],
                                   size=dimensions, min_count=min_frequency, workers=num_workers)
    return model



w2v_model = build_embeddings(2, 50, 10)
w2v_model.save(settings.PATH_DATAOBJECTS + 'model_%s__%s' % (50, time.strftime('%d-%m-%Y')))


t1 = time.time()
t = t1-t0
print(t)

#w2v_model.wv.index2word
#len(w2v_model.wv.vocab)
#w2v_model.most_similar(['help'])
