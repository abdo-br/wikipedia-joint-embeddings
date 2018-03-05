
import os
import sys
import time
import getopt
import settings
import logging
import gensim
import nlp_util as nlp


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Sentences():

    def __iter__(self):

        for file in os.scandir(settings.PATH_OUTPUT):
            if file.name.endswith('.txt'):
                with open(file.path, 'r') as a:
                    paragraphs = nlp.get_paragraphs(a.read())
                    for p in paragraphs:
                        sentences = nlp.get_sentences(p)
                        for s in sentences:
                            sentence = nlp.remove_punctuation(s)
                            yield sentence.lower().split()


def build(dimensions, num_workers):
    model = gensim.models.Word2Vec(sentences=Sentences(), size=dimensions,
                                   window=5, min_count=5, sg=0,
                                   workers=num_workers)
    return model


if __name__ == '__main__':

    __spec__ = None

    size = 50
    cores = 3

    opts, args = getopt.getopt(sys.argv[1:], 's:c:')
    for opt, arg in opts:
        if opt == '-s':
            size = int(arg)
        if opt == '-c':
            cores = int(arg)

    w2v_model = build(size, cores)
    w2v_model.save(settings.PATH_DATAOBJECTS + 'w2v/model_%s__%s' % (size, time.strftime('%d-%m-%Y')))

    print('Done!')


#w2v_model.wv.index2word
#len(w2v_model.wv.vocab)
#w2v_model.most_similar(['help'])
