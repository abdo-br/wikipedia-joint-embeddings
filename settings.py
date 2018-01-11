
# number of articles to process (-1 = ALL)
NUM_ARTICLES = -1


# dataset train folds
PATH_DATA = 'F:/Business Informatics/Thesis/Data/train/'
PATH_ARTICLES = PATH_DATA + 'train.fold1.cbor'
PATH_PARAGRAPHS = PATH_DATA + 'train.fold1.cbor.paragraphs'
PATH_PARAGRAPHS_ARTICLES = PATH_DATA + 'train.fold1.cbor.article.qrels'
PATH_ENTITIES_ARTICLES = PATH_DATA + 'train.fold1.cbor.article.entity.qrels'

# the big file
# PATH_ENTITIES_ARTICLES = 'F:/Business Informatics/Thesis/Data/all/articles.cbor.article.entity.qrels'

# output folder path
PATH_OUTPUT = 'F:/Business Informatics/Thesis/Python/Wikipedia_EE/output/'

# DataObjects path
PATH_DATAOBJECTS = 'F:/Business Informatics/Thesis/Python/Wikipedia_EE/dataObjects/'

# gold standard path
FILE_GOLD_STANDARD = 'annotations.csv'
PATH_GOLD_STANDARD = 'F:/Business Informatics/Thesis/Python/Wikipedia_EE/gold_standard/'

FILE_GOLD_STANDARD_ARTICLES = 'gs_articles.pickle'
FILE_TOKENIZER = 'gs_tokenizer.pickle'

# dbpedia spotlight
PATH_DBPEDIA_SPOTLIGHT_OUTPUT = 'F:/Business Informatics/Thesis/Python/DBpedia Spotlight/output/'
