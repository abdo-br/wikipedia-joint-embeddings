# -*- coding: utf-8 -*-
"""
@author: Abdulrahman Bres
"""

import util
import pickle
import settings
import pandas as pd
import annotator

articles = pickle.load(open(settings.PATH_DATAOBJECTS + 'gs_articles.p', 'rb'))
gold_standard = pd.DataFrame(columns=['Article', 'Level', 'Mention', 'EntityID', 'Offset', 'Sentence', 'The_Sentence'], dtype='unicode', index=None)

for article in articles:
    print(article.page_name)
    gs, body = annotator.annotate(article, True)  # only linked entities

    with open(settings.PATH_GOLD_STANDARD +
              article.page_name.translate(util.valid_filename()) +
              '.txt', 'w', encoding='utf-8') as b:

        b.write(body)
        b.close()

    gold_standard = gold_standard.append(gs)

# save the gold standard as csv
gold_standard.to_csv(settings.PATH_GOLD_STANDARD +
                     settings.FILE_GOLD_STANDARD, encoding='utf-8', index=False)
