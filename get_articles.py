# -*- coding: utf-8 -*-
"""
@author: Abdulrahman Bres
"""

import util
import settings
import pickle

titles = [
        'Ludwig van Beethoven',
        'Angela Merkel',
        'Jeff Bezos',
        'Johnny Depp',
        'Madonna (entertainer)',
        'Syria',
        'Indonesia',
        'History of Spain',
        'Harvard University',
        'Daimler Company',
        'Google',
        'Apple Inc.',
        'Fiorucci',
        'Futurama',
        'RMS Titanic',
        'Lost (TV series)',
        'Tom and Jerry',
        'Basketball',
        'Deus Ex (video game)',
        'Grand Theft Auto',
        'Hatsune Miku',
        'Apple',
        'Hamburger',
        'Neptune',
        'Red',
        'Woman',
        'World War II',
        'Bitcoin',
        'Ubuntu (operating system)',
        'United States presidential election, 2012']

articles = []

for title in titles:
    articles.append(util.get_article(title))

pickle.dump(articles, open(settings.PATH_DATAOBJECTS + 'gs_articles.pickle', 'wb'))
