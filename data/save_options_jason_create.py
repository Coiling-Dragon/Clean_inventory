import json


save_dict = {}
with open("save_options.txt", 'r') as save_file:
    for line in save_file:
       (key, val) = line.split()
       save_dict[str(key)] = val
       
print (save_dict)  
json.dump( save_dict, open( "save_options.json", 'w' ) )