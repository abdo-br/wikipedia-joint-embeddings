
import re
import util
import nlp_util as nlp
import read_data as data
import numpy as np
import pandas as pd
import settings
from enum import Enum

ofs = {}

txt = '''
A B C D E F G H I J K L
'''

for c in txt.split():
    ofs[c] = txt.find(c)
    
    
i = 0

for k, v in ofs.items():
    if v % 5 == 0:
        txt = nlp.replace_part_of_text(txt, 'OO', v+i, 1)
        i += 1

class Page(object):

    def __init__(self, page_name, page_id, body):
        self.page_name = page_name
        self.page_id = page_id
        self.body = body

    def __str__(self):
        return "Page(%s)" % self.page_name

    def to_string(self):
        return self.body

X = '''
An ambitious campus expansion plan was proposed by [Gallagher](Joseph Strub) in 1952. Assumption Hall, the first student dormitory, was opened in 1954.
Rockwell Hall was dedicated in November 1958 for [Gallagher](Joseph Strub), housing the schools of business and law. It was in [France](New France) during the tenure of F. Henry J. McAnulty that Fr. Gallagher's ambitious plans were put to action.

Between 1959 and 1980, the university in [France](New France) renovated or constructed various buildings to form the academic infrastructure of the campus. Among these are College Hall, the music school and the library, as well as a new Student Union and Mellon Hall named for [Gally](Joseph Strub), along with four more dormitories. Although F. McAnulty's years as president saw tremendous expansion, a financial crisis in 1970 nearly forced the closure of the university.

An ambitious campus expansion plan was proposed by [Gallagher](Joseph Strub) in 1952. Assumption Hall, the first student dormitory, was opened in 1954.
Rockwell Hall was dedicated in November 1958 for [Gallagher](Joseph Strub), housing the schools of business and law. It was in [France](New France) during the tenure of F. Henry J. McAnulty that Fr. Gallagher's ambitious plans were put to action.

Between 1959 and 1980, the university in [France](New France) renovated or constructed various buildings to form the academic infrastructure of the campus. Among these are College Hall, the music school and the library, as well as a new Student Union and Mellon Hall named for [Gally](Joseph Strub), along with four more dormitories. Although F. McAnulty's years as president saw tremendous expansion, a financial crisis in 1970 nearly forced the closure of the university.

An ambitious campus expansion plan was proposed by Joe in 1952. Assumption Hall, the first student dormitory, was opened in 1954.
Rockwell Hall was dedicated in November 1958 for [Gallagher](Joseph Strub), housing the schools of business and law. It was in THE [Gallagher](Joseph Strub) during the tenure of F. Henry J. McAnulty that Fr. Gallagher's ambitious plans were put to action.

An ambitious campus expansion plan was proposed by [Gallagher](Joseph Strub) in 1952. Assumption Hall, the first student dormitory, was opened in 1954.
Rockwell Hall was dedicated in November 1958 for [Gallagher](Joseph Strub), housing the schools of business and law. It was in [France](New France) during the tenure of F. Henry J. McAnulty that Fr. Gallagher's ambitious plans were put to action.

Between 1959 and 1980, the university in [France](New France) renovated or constructed various buildings to form the academic infrastructure of the campus. Among these are College Hall, the music school and the library, as well as a new Student Union and Mellon Hall named for [Gally](Joseph Strub), along with four more dormitories. Although F. McAnulty's years as president saw tremendous expansion, a financial crisis in 1970 nearly forced the closure of the university.

'''
X = Page('Duquesne University', 'Duquesne%20University', X)