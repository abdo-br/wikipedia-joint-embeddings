# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 09:07:34 2018

@author: Abdulrahman Bres
"""

import os
import settings


class gold_standard():

    class article:

        def __init__(self, title, text):

            self.title = title
            self.text = text

    def __init__(self):
        import pandas as pd
        self.annotations = pd.read_csv(settings.PATH_GOLD_STANDARD +
                                       settings.FILE_GOLD_STANDARD,
                                       encoding='utf-8')
        self.articles = []
        for file in os.scandir(settings.PATH_GOLD_STANDARD + 'corpus/'):
            with open(file.path, 'r') as a:
                self.articles.append(self.article(file.name[:-4], a.read()))


# test

gs = gold_standard()
