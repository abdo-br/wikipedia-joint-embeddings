# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 07:27:53 2018

@author: Abdulrahman Bres
"""

import requests
import json


def resolve_redirect(title):

    query = requests.get(r'https://en.wikipedia.org/w/api.php?action=query&titles={}&&redirects&format=json'.format(title))
    data = json.loads(query.text)

    try:
        for item in data['query']['redirects']:
            return item['to']

    except Exception as e:
        if e.args[0] == 'redirects':
            return ''
        else:
            return 'ERROR'



X = resolve_redirect('Hillary Klinton')

