

import settings
import pickle
import nlp_util as nlp
from nltk.tokenize.punkt import PunktSentenceTokenizer

articles = pickle.load(open(settings.PATH_DATAOBJECTS + 'gs_articles.pickle', 'rb'))

tokenizer = PunktSentenceTokenizer()

for article in articles:
    tokenizer.train(nlp.get_clean_article(article.to_string()))

# pickle.dump(articles, open(settings.PATH_DATAOBJECTS + 'gs_tokenizer.pickle', 'wb'))

X = []
for article in articles:
    X.append(tokenizer.tokenize(nlp.get_clean_article(article.to_string())))
