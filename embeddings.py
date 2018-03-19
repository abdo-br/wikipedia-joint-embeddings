
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

    def __init__(self, directory):
        self.directory = directory

    def __iter__(self):

        for file in os.scandir(self.directory):
            if file.name.endswith('.txt'):
                with open(file.path, 'r', encoding='utf-8') as a:
                    paragraphs = nlp.get_paragraphs(a.read())
                    for p in paragraphs:
                        sentences = nlp.get_sentences(p)
                        for s in sentences:
                            sentence = nlp.remove_punctuation(s)
                            yield sentence.lower().split()


def build(corpus, dimensions, window, num_workers):
    model = gensim.models.Word2Vec(sentences=Sentences(corpus), size=dimensions,
                                   window=window, min_count=5, sg=0,
                                   workers=num_workers)
    return model


if __name__ == '__main__':

    __spec__ = None

    corpus = ''
    size = 50
    window = 5
    cores = 2

    opts, args = getopt.getopt(sys.argv[1:], 'd:s:c:')
    for opt, arg in opts:
        if opt == '-d':
            corpus = arg
        if opt == '-s':
            size = int(arg)
        if opt == '-c':
            cores = int(arg)

    print('workers: ' + str(cores))
    print('corpus: ' + corpus)

    w2v_model = build(settings.PATH_OUTPUT+corpus, size, window, cores)
    w2v_model.save(settings.PATH_OUTPUT + 'w2v/skipgram_%s_%s_%s__%s' % (corpus, size, window, time.strftime('%d-%m-%Y')))

    print('Done!')


#w2v_model.wv.index2word
#len(w2v_model.wv.vocab)
#w2v_model.most_similar(['help'])
