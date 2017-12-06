# -*- coding: utf-8 -*-
"""
@author: Abdulrahman Bres
"""

import util
import pandas as pd
import read_data as data
import settings
import annotator

gold_standard = pd.DataFrame(columns=['Article', 'Level', 'Mention', 'EntityID', 'Offset', 'Sentence', 'The_Sentence'], dtype='unicode', index=None)

# get an articles

# get the wanted articles
# iterate over them
# add them to GS

article = 'some article'
i = 0
with open(settings.PATH_ARTICLES, 'rb') as d:
    for a in data.iter_annotations(d):
        i += 1
        if i == 10:
            print(a.page_name)
            article = a
            break

gs, body = annotator.annotate(article, True)  # only linked entities

with open(settings.PATH_GOLD_STANDARD +
          article.page_name.translate(util.valid_filename()) +
          '.txt', 'w', encoding='utf-8') as b:

    b.write(body)
    b.close()

gold_standard.append(gs)

# save the gold standard as csv
gold_standard.to_csv(settings.PATH_GOLD_STANDARD +
                     settings.FILE_GOLD_STANDARD, encoding='utf-8', index=False)
