
import settings
import json
import pandas as pd


def get_annotations(article):

    Graph = pd.DataFrame(columns=['Mention', 'EntityID'], index=None)
    
    with open(settings.PATH_DBPEDIA_SPOTLIGHT_OUTPUT+article+'.json') as annotations:
        data = json.load(annotations)

    for entity in data['Resources']:
        Graph.loc[len(Graph.index)] = [entity['@surfaceForm'], entity['@URI']]
        
    return Graph

