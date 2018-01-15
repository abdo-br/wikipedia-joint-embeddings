# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 15:58:43 2017

@author: Abdulrahman Bres
"""

import settings
import pandas as pd


annotations = pd.DataFrame(columns=['Article', 'Level', 'Mention',
                                    'Used_Entity', 'Entity', 'EntityID',
                                    'Offset', 'Sentence', 'The_Sentence'],
                           dtype='unicode', index=None)

# the expected golds standard has one entity per sentence at most
gold_standard = pd.read_csv(settings.PATH_GOLD_STANDARD +
                            settings.FILE_GOLD_STANDARD, encoding='utf-8')


def evaluate(annotations):

    counts = pd.DataFrame(columns=['EntityID', 'Given', 'Correct', 'Actual'],
                          dtype='unicode', index=None)

    metrics = pd.DataFrame(columns=['coverage', 'micro_recall',
                                    'micro_precision', 'micro_f1',
                                    'macro_recall', 'macro_precision',
                                    'macro_f1'], index=None)

    for entity in gold_standard['EntityID'].unique():
        gs = gold_standard.loc[gold_standard['EntityID'] == entity]
        actual = gs.shape[0]
        result = pd.merge(gs, annotations, how='inner',
                          on=['Article', 'Sentence'], suffixes=('_gs', ''))
        given = result.shape[0]
        correct = result.loc[result['EntityID'] == entity].shape[0]
        counts.loc[len(counts.index)] = [entity, given, correct, actual]

    # aggregate entities
    counts = counts.groupby('EntityID').sum()

    # calculate metrics
    coverage = counts['Given'].sum() / counts['Actual'].sum()
    micro_recall = counts['Correct'].sum() / counts['Actual'].sum()
    micro_precision = counts['Correct'].sum() / counts['Given'].sum()
    micro_f1 = (2 * micro_recall * micro_precision) / (micro_recall + micro_precision)

    macro_recall = (counts['Correct'] / counts['Actual']).mean()
    macro_precision = (counts['Correct'] / counts['Given']).mean()
    macro_f1 = (2 * macro_recall * macro_precision) / (macro_recall + macro_precision)

    metrics.loc[len(counts.index)] = [coverage, micro_recall, micro_precision,
                                      micro_f1, macro_recall, macro_precision, macro_f1]

    return metrics
