import json
import time
import sqlite3 as lite
import os


def save_json_file(BASE_DIR):
    # Serialize data into file:
    global save_dict
    file_path = "\\".join([BASE_DIR,'data','save_options.json'])
    
    json.dump( save_dict, open(file_path, 'w' ) )


def load_json_file(BASE_DIR):
    # Read data from file:
    global save_dict
    file_path = "\\".join([BASE_DIR,'data','save_options.json'])
    
    save_dict = json.load( open(file_path, "r" ) )
    return save_dict
    
def DB_filepath_read(BASE_DIR):
    global DB_path
    file_path = "\\".join([BASE_DIR,'data','DB_path.txt'])
    
    with open(file_path, 'r') as save_file:
        DB_path = save_file.readline()
        print(DB_path)
        if DB_path == '':
            DB_path = 'inventory.db'
            try:
                
                con = lite.connect(DB_path)
                print(lite.version)
                cur = con.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS items(Row INTEGER PRIMARY KEY AUTOINCREMENT,ASIN TEXT,SKU TEXT,UPC TEXT NOT NULL,Store TEXT,SaleChan TEXT,Status TEXT);""")
                con.commit()
            except Exception as e:
                print(e)
                
            finally:
                if con:
                    con.close()
            
    return DB_path


def DB_filepath_write(BASE_DIR,DB_path):
    file_path = "\\".join([BASE_DIR,'data','DB_path.txt'])
    
    with open(file_path, 'w') as save_file:
        save_file.write(DB_path)
        #print(DB_path)
        

def DB_filepath_strip(DB_path,file_name):
    #Path to other files in DB folder plus FILE NAME
    
    striper = (DB_path).split("/")[:-1]
    striper =  "\\".join(striper+[file_name,])
    return striper


if __name__ == "__main__":
    #soem tests
    
    
    DB_path = 'C:/Users/Sekirata/Google Drive/Inventory/2020-04-14 17h10m_DB_BACKUP OS.db'
    file_name = 'dated.csv'
    
    print(DB_filepath_strip(DB_path,file_name))