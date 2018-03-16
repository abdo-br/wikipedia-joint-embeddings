
# number of articles to process (-1 = ALL)  57129
NUM_ARTICLES = 5000

# KEY = thesis

# small data
#PATH_DATA = 'F:/Business Informatics/Thesis/Data/Y1/'
#PATH_ARTICLES = PATH_DATA + 'train.benchmarkY1train.fold1.cbor'
#PATH_PARAGRAPHS = PATH_DATA + 'train.benchmarkY1train.fold1.cbor.paragraphs'
#PATH_PARAGRAPHS_ARTICLES = PATH_DATA + 'train.benchmarkY1train.fold1.cbor.article.qrels'
#PATH_ENTITIES_ARTICLES = PATH_DATA + 'train.benchmarkY1train.fold1.cbor.article.entity.qrels'

# dataset train folds
PATH_DATA = 'F:/Business Informatics/Thesis/Data/train/'
PATH_ARTICLES = PATH_DATA + 'train.fold3.cbor'
PATH_PARAGRAPHS = PATH_DATA + 'train.fold3.cbor.paragraphs'
PATH_PARAGRAPHS_ARTICLES = PATH_DATA + 'train.fold3.cbor.article.qrels'
#PATH_ENTITIES_ARTICLES = PATH_DATA + 'entities.csv'

# temp
PATH_DATA2 = 'F:/Business Informatics/Thesis/Data/train/'
PATH_ENTITIES_ARTICLES = PATH_DATA2 + 'es2.csv'

# output folder
PATH_OUTPUT = 'F:/Business Informatics/Thesis/Python/Wikipedia_EE/output/'

# KB
PATH_KB = 'F:/Business Informatics/Thesis/Python/Wikipedia_EE/KB/'
PATH_MENTIONS = PATH_KB + 'all/' +  'mentions.pickle'
#PATH_MENTIONS = PATH_KB + 'all/' +  'all_mentions.csv'
#PATH_BEST_ENTITIES = PATH_KB + 'all/' + 'best_entities.csv'
PATH_BEST_ENTITIES = PATH_KB + 'all/' + 'most_freq.pickle'

# gold standard
PATH_GOLD_STANDARD = 'F:/Business Informatics/Thesis/Python/Wikipedia_EE/gold_standard/'

PATH_REDIRECTS = 'F:/Business Informatics/Thesis/Python/Wikipedia_EE/KB/all/redirects.csv'

# dbpedia spotlight
PATH_DBPEDIA_SPOTLIGHT_OUTPUT = 'F:/Business Informatics/Thesis/Python/DBpedia Spotlight/output/'
