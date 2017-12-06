
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import read_data as data
import settings
import util

# counters
articles_count = 0
paragraphs_count = 0

# get all entities from Wikipedia into a DataFrame
entities = util.get_entities(True)

# get all paragraphs of Wikipedia into a DataFrame
paragraphs = util.get_paragraphs()

# data structures for output
Articles_Paragraphs_Entities = pd.DataFrame(columns=['Article', 'Paragraph', 'Paragraph Linked Entities', 'Found Entities'], index=None)
Articles_Recall_Values = pd.DataFrame(columns=['Article', 'Macro Recall', 'Micro Recall'], index=None)

Macro_Recall_st_errors = []
Micro_Recall_st_errors = []

s = 0
# cutoffs for calculating the standard error values
articles_counts = range(5,105,1)

# iterate over all articles and paragraphs (Until a desired number of articles)

with open(settings.PATH_ARTICLES, 'rb') as a:
    for article in data.iter_annotations(a):
        articles_count+=1

        # get entities within the article
        article_entities = entities.loc[entities['article'] == article.page_id, 'entity']

        # get paragraphs within the article
        article_paragraphs = paragraphs[paragraphs['article'] == article.page_id, 'paragraph']

        # get article textual content
        article_content = article.to_string()

        with open(settings.PATH_PARAGRAPHS, 'rb') as p:
            for paragraph in data.iter_paragraphs(p):

                # skip the other irrelavant articles
                if(not any(article_paragraphs == paragraph.para_id)): continue

                paragraphs_count+=1

                # get the linked entities within paragraph
                paragraph_entities = [elem.page for elem in paragraph.bodies if isinstance(elem, data.ParaLink)]
                print(paragraph_entities, '\n')

                # get the paragraph text
                paragraph_text = [elem.text if isinstance(elem, data.ParaText) else elem.anchor_text for elem in paragraph.bodies]
                print(' '.join(paragraph_text))

                # find the article entities within paragraph
                found_entities_count = 0
                for ae in article_entities:
                    if(ae in ' '.join(paragraph_text)):
                        found_entities_count += 1

                paragraph_entities_count = len(paragraph_entities)

                # store entities counts
                new_row = {'Article': article.page_name,'Paragraph': paragraph.para_id,'Paragraph Linked Entities': paragraph_entities_count,'Found Entities': found_entities_count}
                Articles_Paragraphs_Entities = Articles_Paragraphs_Entities.append(pd.DataFrame(data=new_row, index=[0]), ignore_index=True)

        # calculate Recall values for articles
        # AFTER ignoring paragraphs which include no linked entities

        # calculate Macro Recall
        Article_Paragraphs_Entities = Articles_Paragraphs_Entities[(Articles_Paragraphs_Entities['Article'] == article.page_name) & (Articles_Paragraphs_Entities['Paragraph Linked Entities'] != 0)]
        Article_Paragraphs_Entities['Paragraph Recall'] = Article_Paragraphs_Entities['Found Entities'] / Article_Paragraphs_Entities['Paragraph Linked Entities']
        Macro_Recall = Article_Paragraphs_Entities['Paragraph Recall'].mean()

        # calculate Micro Recall
        Recall_Numerator = Articles_Paragraphs_Entities['Found Entities'][(Articles_Paragraphs_Entities['Article'] == article.page_name) & (Articles_Paragraphs_Entities['Paragraph Linked Entities'] != 0)].sum()
        Recall_Denominator = Articles_Paragraphs_Entities['Paragraph Linked Entities'][(Articles_Paragraphs_Entities['Article'] == article.page_name) & (Articles_Paragraphs_Entities['Paragraph Linked Entities'] != 0)].sum()
        Micro_Recall = Recall_Numerator / Recall_Denominator

        # store Recall values
        new_row = {'Article':article.page_name, 'Macro Recall': Macro_Recall, 'Micro Recall': Micro_Recall}
        Articles_Recall_Values = Articles_Recall_Values.append(pd.DataFrame(data=new_row, index=[0]), ignore_index=True)

        # print paragraphs count
        print('\nparagraphs count: ', paragraphs_count, '\n')


        if((s < len(articles_counts)) and (articles_count == articles_counts[s])):
                    s+=1
                    # calculate Recall values mean
                    Macro_Recall_Values_std_error = Articles_Recall_Values['Macro Recall'].std() / np.sqrt(articles_count)
                    Micro_Recall_Values_std_error = Articles_Recall_Values['Micro Recall'].std() / np.sqrt(articles_count)

                    Macro_Recall_st_errors.append({'Number of articles':articles_count ,'Recall std error':Macro_Recall_Values_std_error})
                    Micro_Recall_st_errors.append({'Number of articles':articles_count ,'Recall std error':Micro_Recall_Values_std_error})

        # stop after certain number of articles
        if settings.NUM_ARTICLES != -1 and articles_count > settings.NUM_ARTICLES: break


# visualize Recall values
Articles_Recall_Values.boxplot()

# visualize standard errors values
Recall_std_errors = pd.DataFrame(Macro_Recall_st_errors)
Recall_std_errors['Recall Type'] = 'Macro Recall'

temp_df = pd.DataFrame(Micro_Recall_st_errors)
temp_df['Recall Type'] = 'Micro Recall'

Recall_std_errors = Recall_std_errors.append(temp_df)

plt.figure(figsize=(15, 6))
fig = sns.pointplot(x='Number of articles', y='Recall std error', hue='Recall Type', data=Recall_std_errors, col='Recall Type')

fig.set(xlabel="Number of Articles")
fig.set(ylabel="Recall Standard Error")
