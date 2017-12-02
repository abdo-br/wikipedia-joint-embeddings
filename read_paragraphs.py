
import read_data as data
import settings

i = 1

with open(settings.PATH_PARAGRAPHS, 'rb') as p:
    for paragraph in data.iter_paragraphs(p):
        i+=1
        print('\nparagraph id ', paragraph.para_id, '\n')
        
        # Print the linked entities
        # entities = [elem.page for elem in paragraph.bodies if isinstance(elem, data.ParaLink)]
        # print(entities, '\n')

        # Print the text
        # texts = [elem.text if isinstance(elem, data.ParaText) else elem.anchor_text for elem in paragraph.bodies]
        # print(' '.join(texts))
        
        if(i>9): break