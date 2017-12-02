
import pandas as pd
import ijson

entities_json = ijson.parse(open('/data/program/Output/en20161001/MentionList-JSON.txt', 'r'))

i = 0

main_entity = ''
entities = pd.DataFrame({'Entity ID':[],'Alias':[]})

for prefix, event, value in entities_json:
    #if(i == 10): break
    if(event == 'map_key'):
        main_entity = prefix
        #i+=1
    elif(event == 'number'):
        new_row = {'Entity ID':'[' + main_entity + ']', 'Alias':prefix[len(main_entity)+1:]}
        entities = entities.append(pd.DataFrame(data=new_row, index=[0]), ignore_index=True)
    else: continue
entities = entities [['Entity ID','Alias']]

entities.to_pickle('/home/abres/entities.gzip', compression='gzip')

# Done
f = open('/home/abres/EntitiesDONE.txt','w+')
f.write('DONE')
f.close()
