import sqlite3 as lite
import csv

DB_path = 'C:/Users/CoilingDragon/Desktop/Clean Inventory v12/TEST.db'

def get_asin_sku_fromdb(DB_path):
    
    con = lite.connect(DB_path)
    cur = con.cursor()
    cur.execute("""SELECT Row,ASIN,UPC,Store FROM items""")
    db_data = cur.fetchall()
    #con.commit()
    con.close()
    print(db_data)
    return db_data
    

'''
ASIN	SKU	UPC	Store	SaleChan	Status
B01G8XC762	TF-6AGD-18O8	ZOR?717905253225	ZOR?BUNTING BEARINGS?EF162016	AmD	3
'''

def cell_fixing(db_cell,input_cell):# edit_bycsv
    cell_fix = []
    db_cell_split = db_cell.split(':::')
    first_half = input_cell.split('?')[0]
    second_half = '?'.join(input_cell.split('?')[1:])
    
    for cell in db_cell_split:
        if first_half in cell:
            cell = first_half +'?'+ second_half
        cell_fix.append(cell)

    
    cell_fix = ':::'.join(cell_fix)
    print(cell_fix,'---returned')
    return cell_fix


def dict_cell_fixing(db_cell,input_cell):
    my_dict = {}
    db_cell_split = filter(None, db_cell.split(':::'))

    for x in db_cell_split:
        if x.split('?')[0] in my_dict:
            pass
        else:
            my_dict[x.split('?')[0]] = x.split('?')[1]
    
    try:
        db_cell_split = filter(None, input_cell.split(':::'))

        for x in db_cell_split:
            my_dict[x.split('?')[0]] = x.split('?')[1]
    except:
        pass
    
    return ':::'.join([k+'?'+my_dict[k] for k in my_dict])
    


def upload_by_csv_smart():

    global time_str
    sqlite3_backup()
    canvas.filename = filedialog.askopenfilename(initialdir = "c:/", title = "Select CSV", filetypes = (("csv files","*.csv"),("all files","*.*")))
    upl_csv_path = canvas.filename
    DB_path = DB_filepath_read(BASE_DIR)

    
    #path = 'C:/Users/CoilingDragon/Desktop/Clean Inventory v12/test.csv'
    with open(path,newline='',encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader) #first line is header
        edit_data = [row for row in reader] #reads the remaining data
    
    try:
        con = lite.connect(DB_path)
        cur = con.cursor() 
        
        for each in edit_data:
            #edit_Row = int(each[0].strip())#Row
            edit_ASIN = each[0].strip()#ASIN
            edit_SKU = each[1].strip()#SKU
            edit_UPC = each[2].strip()#UPC
            assert ':::' not in edit_UPC
            edit_Store = each[3].strip()#Store
            assert ':::' not in edit_Store
            edit_SaleChan = each[4].strip()#SaleChan
            edit_Status = each[5].strip()#Status
            #assert edit_Status in save_dict.keys()#-------------------------------remove#
            
            cur.execute("SELECT * FROM items WHERE ASIN=?", (edit_ASIN,))
            db_data = cur.fetchone()
            
            print(db_data)
            
            #FI found just eddit
            if db_data != None:
  
                edit_UPC = dict_cell_fixing(db_data[3],edit_UPC)#UPC
                edit_Store = dict_cell_fixing(db_data[4],edit_Store)#Store

                
                print(edit_ASIN)
                querry = f"""UPDATE items SET 
                
                SKU = "{edit_SKU}", 
                UPC = "{edit_UPC}", 
                Store = "{edit_Store}", 
                SaleChan = "{edit_SaleChan}", 
                Status = "{edit_Status}" 
                
                WHERE ASIN = "{edit_ASIN}";"""
                
                cur.execute(querry)
            
            #FI not found  UPLOAD
            else:
                cur.execute("INSERT INTO items (ASIN,SKU,UPC,Store,SaleChan,Status) VALUES (?,?,?,?,?,?);", [edit_ASIN,edit_SKU,edit_UPC,edit_Store,edit_SaleChan,edit_Status])
   
        con.commit()          
        con.close()
        
        log_str = f"MATCHED by csv {edit_csv_path}"#-------------------------------remove#
        update_logger(log_str)#-------------------------------remove#
        
    except Exception as e:
        log_str = f"ERROR IN CSV EDIT---->{e}"
        print(log_str)
        update_logger(log_str)#-------------------------------remove#




#print(get_asin_sku_fromdb(DB_path))
#print(select_all(DB_path))
        

#upload_by_csv_smart(DB_path)
#get_asin_sku_fromdb(DB_path)
        
        
db_cell = 'PBA?7164085423232328609:::PAS?:::MSL?123:::PBA?716408:::'
input_cell ='MSL?1234567:::PBA?test'

print('db cell:',db_cell)
print('input:',input_cell)
print('new cell:',dict_cell_fixing(db_cell,input_cell))