# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 07:55:33 2017

@author: Abdulrahman Bres
"""

import os
import settings
import pickle
import nlp_util as nlp

articles = []

for file in os.scandir(settings.PATH_GOLD_STANDARD + 'corpus/'):
    with open(file.path, 'r') as a:
        articles.append(a.read())

tokenizer = nlp.trained_punkt_tokenizer(articles)

pickle.dump(tokenizer, open(settings.PATH_DATAOBJECTS + 'gs_tokenizer.pickle', 'wb'))
