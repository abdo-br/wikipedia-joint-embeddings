# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 14:52:00 2018

@author: Abdulrahman Bres
"""

import sys, getopt
import annotator
import settings
import read_data as data
import pandas as pd
from multiprocessing import Pool


def main():

    s = 0
    p = 0
    i = 1
    size = 0
    part = 0
    cores = 3

    opts, args = getopt.getopt(sys.argv[1:], 's:p:c:')
    for opt, arg in opts:
        if opt == '-s':
            size = int(arg)
        if opt == '-p':
            part = int(arg)
        if opt == '-c':
            cores = int(arg)

    dictionary = pd.DataFrame(columns=['Entity', 'EntityID'], dtype='unicode', index=None)

    jobs = Pool(processes=cores, initializer=annotator.initialize_knowledgebase, initargs=(), maxtasksperchild=250)

    with open(settings.PATH_ARTICLES, 'rb') as a:

        try:

            for work in jobs.imap(annotator.annotate, data.iter_annotations(a), chunksize=10):

                s += 1
                p += 1

                if s > size:
                    break

                if p > part:
                    p = 0
                    i += 1

                annotations, article_body = work
                dictionary = dictionary.append(annotations[['Entity', 'EntityID']])
                with open(settings.PATH_OUTPUT+'part '+str(i)+'.txt', 'a', encoding='utf-8') as b:
                    b.write(article_body)
                    b.write('\n\n')

        except Exception as e:

            with open('ERRORS.txt', 'a') as err:
                err.write(a.page_id)

    print('\n')
    print('JOINING NOW')

    jobs.close()

    dictionary.to_csv(settings.PATH_OUTPUT+'entities_dictionary.csv', encoding='utf-8', index=False)

    print('\n')
    print('DONE')


if __name__ == '__main__':

    main()
