
import pandas as pd
import ijson

#f = open('E:/Wikipedia_entities_JSON/test.txt', 'r')

#objs = ijson.items(f, 'earth.europe.item')
#cities = (o for o in objs if o['type'] == 'city')
#
#for city in cities:
#    print(city)

# MentionList-JSON.txt
# All-JSON.txt

entities_json = ijson.parse(open('E:/Wikipedia_entities_JSON/MentionList-JSON.json', 'r'))

p = ijson.parse(open('E:/Wikipedia_entities_JSON/test.txt', 'r'))

continent = ''

#for prefix, event, value in p:
#    if (prefix, event) == ('earth', 'map_key'):
#        print('continent ', value)
#        continent = value
#    elif prefix.endswith('.name'):
#        print('city ',value)
#    elif (prefix, event) == ('earth.%s' % continent, 'end_map'):
#        print('continent',continent)

#for prefix, event, value in p:
#    print(prefix,' ',event,' ',value)

i = 0

main_entity = ''
entities = pd.DataFrame({'Entity ID':[], 'Alias':[]})

for prefix, event, value in entities_json:
    if i == 50: break
    if event == 'map_key':
        main_entity = prefix
        i+= 1
    elif event == 'number':
        new_row = {'Entity ID':'[' + main_entity + ']', 'Alias':prefix[len(main_entity)+1:]}
        entities = entities.append(pd.DataFrame(data=new_row, index=[0]), ignore_index=True)
    else: continue
entities = entities [['Entity ID','Alias']]
