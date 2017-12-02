# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 01:00:10 2017

@author: Abdurrahman
"""

import gensim
import logging
import settings
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


model_name = 'model_50__26-11-2017'

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


w2v_model = gensim.models.Word2Vec.load(settings.PATH_DATAOBJECTS + model_name)
words = w2v_model.wv.index2word

#vocab = list(w2v_model.wv.vocab)
#X = w2v_model[vocab]
#
#tsne = TSNE(n_components=2)
#X_tsne = tsne.fit_transform(X)
#
#df = pd.concat([pd.DataFrame(X_tsne), pd.Series(vocab)], axis=1)
#df.columns = ['x', 'y', 'word']
#
#fig = plt.figure()
#ax = fig.add_subplot(1, 1, 1)
#
#ax.scatter(df['x'], df['y'])
#
#for i, txt in enumerate(df['word']):
#    ax.annotate(txt, (df['x'].iloc[i], df['y'].iloc[i]))

#len(w2v_model.wv.vocab)
#w2v_model.most_similar(['help'])
#w2v_model.score(["I am perfect".split()])
#w2v_model.wv.similarity('woman', 'man')
