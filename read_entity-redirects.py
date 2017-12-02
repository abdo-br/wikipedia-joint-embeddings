
import urllib
import pandas as pd

# read entity-redirects
path = "F:/Business Informatics/Thesis/Data/entity-redirects/unprocessed.train.cbor.redirects.tsv"
redirects = pd.read_csv(path, sep='\t', header=None, dtype='unicode')

redirects = redirects.rename(columns={0: 'mention', 1: 'entity'})


# get redirects of Hillary_Clinton
Hillary_Clinton = redirects[redirects.entity == 'Hillary%20Clinton']
Hillary_Clinton['mention'] = Hillary_Clinton['mention'].apply(lambda x: urllib.parse.unquote(str(x),encoding='utf-8', errors='replace'))
Hillary_Clinton['entity'] = Hillary_Clinton['entity'].apply(lambda x: urllib.parse.unquote(str(x),encoding='utf-8', errors='replace'))

