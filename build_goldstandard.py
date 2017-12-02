# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 23:34:38 2017

@author: Abdurrahman
"""

import util
import read_data as data
import settings
import annotator

# get an article
article = 'some article'
i = 0
with open(settings.PATH_ARTICLES, 'rb') as d:
    for a in data.iter_annotations(d):
        i += 1
        if i == 10:
            print(a.page_name)
            article = a
            break

gs, body = annotator.annotate(article, True) # only linked entities

# save the gold standard as csv & txt
gs.to_csv(settings.PATH_GOLD_STANDARD + article.page_name.translate(util.valid_filename()) + '.csv', encoding='utf-8')

with open(settings.PATH_GOLD_STANDARD + article.page_name.translate(util.valid_filename()) + '.txt', 'w', encoding='utf-8') as b:
    b.write(body)
    b.close()
