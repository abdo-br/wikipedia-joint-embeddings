# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 14:52:00 2018

@author: Abdulrahman Bres
"""

import os
import sys
import getopt
import pickle
import annotator
import settings
import read_data as data
import pandas as pd
from itertools import islice
from multiprocessing import Pool


def main():

    s = 0
    p = 0
    i = 1
    store = 1000 #500
    part = 50 #100000
    cores = 2

    # 1 - 500000 + loop
    start = 100
    end = 600 #0

    opts, args = getopt.getopt(sys.argv[1:], 'c:p:s:e:')
    for opt, arg in opts:
        if opt == '-c':
            cores = int(arg)
        if opt == '-p':
            part = int(arg)
        if opt == '-s':
            start = int(arg)
        if opt == '-e':
            end = int(arg)

    print('workers: ' + str(cores))
    print('articles: ' + str(start)+' - '+str(end))

    dictionary = pd.DataFrame(columns=['entity', 'entity_id'], dtype='unicode', index=None)
    jobs = None

    if os.name == 'nt':

        jobs = Pool(processes=cores, initializer=annotator.initialize_knowledgebase, initargs=(), maxtasksperchild=250)

    else:

        annotator.initialize_knowledgebase()
        jobs = Pool(processes=cores, initargs=(), maxtasksperchild=250)

    with open(settings.PATH_ARTICLES, 'rb') as a:

        corpus = ''
        iterable = iter(data.iter_annotations(a))
        for work in jobs.imap_unordered(annotator.annotate, islice(iterable, start, end), chunksize=2000):

            if p > part:
                p = 0
                i += 1

            annotations, article_body = work
            if article_body is not None:
                s += 1
                p += 1

                dictionary = dictionary.append(annotations)
                corpus += article_body
                corpus += '\n\n'

            if s % store == 0:
                with open(settings.PATH_OUTPUT+str(start)+' part '+str(i)+'.txt', 'a', encoding='utf-8') as b:
                    b.write(corpus)
                    corpus = ''

    print('\n')
    print('JOINING NOW')

    jobs.close()
    jobs.join()

    dictionary.drop_duplicates(inplace=True)
    dictionary.to_csv(settings.PATH_OUTPUT+str(start)+' entities_dictionary.csv', chunksize=10000, encoding='utf-8', index=False)

    #pickle.dump(annotator.error_articles, open(settings.PATH_OUTPUT + 'error_articles.pickle', 'wb'))

    print('\n')
    print('DONE')

    print('Total number of articles: ' + str(s))


if __name__ == '__main__':

    __spec__ = None

    main()
