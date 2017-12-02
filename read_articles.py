
import read_data as data
import settings

i = 1

articles = []

with open(settings.PATH_ARTICLES, 'rb') as a:
    for article in data.iter_annotations(a):
        i += 1
        outPath = settings.PATH_OUTPUT + article.page_name

        # print page name
        print(article.page_name, '\n')
        # print page main sections
        print([(section.heading, len(children)) for (section, children) in article.deep_headings_list()], '\n')
        # print page all sections
        print(["/".join([section.heading for section in sectionpath]) for sectionpath in article.flat_headings_list()], '\n')

        # save the article
        with open(outPath, 'w', encoding='utf-8') as processed_article:
            processed_article.write(article.to_string())

        if settings.NUM_ARTICLES != -1 and i > settings.NUM_ARTICLES: break
