import os,sys,inspect
sys.path.insert(1, os.path.realpath(os.path.pardir))


from extraPacks.Utils import *

c = get_time_call()
print(c)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
my_dict = (load_json_file(BASE_DIR))
print(list(my_dict.keys()))

try:
    assert "M123?" in my_dict.keys()
    if "M123?" in list(my_dict.keys()):
        print('yey')
        
    else:
        print("no")
        
except:
    print("no")
    