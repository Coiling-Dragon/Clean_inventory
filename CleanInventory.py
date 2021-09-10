# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 17:57:26 2020

------
-If adding more stores,channels,statuses - more filter values:
    
    1 - need to add the value to the - save_dict,
    2 - add more variables - tkinter variables and set variables
    3 - add it to the FILTERS menu checkbutton - menu.add_checkbutton
    
    4 - add the .get() funtion, - get_filter_val()
    
    5 - add to the list in - search_func()          Store_list
                                                    SaleChan_list 
                                                    Status_list 

-------

file_name = os.path.basename(DB_path)

@author: CoilingDragon
"""

from tkinter import *
from PIL import ImageTk,Image
from tkinter import filedialog
import sqlite3 as lite
import json
import time
import shutil # for DB backup
#from csv import writer
import csv
import os


from extraPacks.Utils import *


def get_time_call():
    global time_str
    
    time_str = str(time.strftime('%Y-%m-%d %Hh%Mm%Ss', time.localtime(time.time()) ))
    return time_str

def update_logger(log_str):
    global time_str

    get_time_call()
    with open(logger_path, "a") as write_file:
        write_file.write(time_str +" | "+log_str + '\n')
        
    try:
        listNodes_logger.delete(0,END)
        
        with open(logger_path, 'r') as save_file:
            for line in save_file:
                listNodes_logger.insert(END,(line+" |"))
                listNodes_logger.insert(END,('_'))
                
                
                listNodes_logger.yview_moveto('1.0')
                listNodes_logger.config(yscrollcommand=scrollbar.set)
    except:
        listNodes_logger.insert(END,("Log.txt file path error"))
#--------------------------------------BUTTONS DEFINE-----------------------------------------#
def sqlite3_backup():
    """Create timestamped database copy"""
    global time_str
    global DB_path
    backupdir = 'Backups/'
    
    if not os.path.isdir(backupdir):
        raise Exception("Backup directory does not exist: {}".format(backupdir))

    
    backup_file = os.path.join(backupdir,get_time_call()+'_DB_BACKUP.db')

    connection = lite.connect(DB_path)
    cursor = connection.cursor()

    # Lock database before making a backup
    cursor.execute('begin immediate')
    # Make new backup file
    shutil.copyfile(DB_path, backup_file)
    # Unlock database
    connection.rollback()
    label_loading['text'] = ("{}".format(backup_file))


def upload_bycsv():
    global time_str

    sqlite3_backup()

    canvas.filename = filedialog.askopenfilename(initialdir = "c:/", title = "Select CSV", filetypes = (("csv files","*.csv"),("all files","*.*")))
    upl_csv_path = canvas.filename
    
    DB_path = DB_filepath_read(BASE_DIR)
    
    
    if upl_csv_path != '':
        
        con = lite.connect(DB_path)
        cur = con.cursor() 
        cur.execute("""CREATE TABLE IF NOT EXISTS items(Row INTEGER PRIMARY KEY AUTOINCREMENT,ASIN TEXT,SKU TEXT,UPC TEXT NOT NULL,Store TEXT,SaleChan TEXT,Status TEXT);""")
        
        path = upl_csv_path
        #csv_file = open(path,newline='',encoding='utf-8')
        with open(path,newline='',encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader) #first line is header
            data = [row for row in reader] #reads the remaining data
            cur.executemany("INSERT INTO items (ASIN,SKU,UPC,Store,SaleChan,Status) VALUES (?,?,?,?,?,?);", data)
            #print('uploading finished')
        con.commit()
        con.close()
        
        lable_ID_querry()
        
        log_str = f"CSV UPLOAD successfully - {path}"
        update_logger(log_str)


def upload_by_csv_smart():

    global time_str
    start_time = time.time()
    
    sqlite3_backup()
    canvas.filename = filedialog.askopenfilename(initialdir = "c:/", title = "Select CSV", filetypes = (("csv files","*.csv"),("all files","*.*")))
    upl_csv_path = canvas.filename
    
    DB_path = DB_filepath_read(BASE_DIR)
    path = upl_csv_path
    
    with open(path,newline='',encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader) #first line is header
        edit_data = [row for row in reader] #reads the remaining data
    
    len_each_errors = []
    i = 1
    try:
        con = lite.connect(DB_path)
        cur = con.cursor() 
        
        for each in edit_data:
            
            i += 1
            
            if i%150 == 0:
                elapsed_time = round((time.time() - start_time),2)
    
                hours_ = elapsed_time//3600
                min_ = (elapsed_time%3600)//60
                sec_ = (elapsed_time%60)
                
                label_loading['text'] = str(round((i/(len(edit_data))*100),2)) + f'% Loading -- Elapsed time: {int(hours_)}h,{int(min_)}m,{round(sec_,1)}s'
                root.update()
                
            if len(each)!=6:
                len_each_errors += each
                print('error on ----',each)
                continue
            #edit_Row = int(each[0].strip())#Row
            edit_ASIN = each[0].strip()#ASIN
            edit_SKU = each[1].strip()#SKU
            edit_UPC = each[2].strip()#UPC
            #assert ':::' not in edit_UPC
            edit_Store = each[3].strip()#Store
            #assert ':::' not in edit_Store
            edit_SaleChan = each[4].strip()#SaleChan
            edit_Status = each[5].strip()#Status
            assert edit_Status in save_dict.keys()#-------------------------------remove#
            
            cur.execute("SELECT * FROM items WHERE ASIN=?", (edit_ASIN,))
            db_data = cur.fetchone()
            
            #print(db_data)
            
            #FI found just eddit
            if db_data != None:
      
                edit_UPC = dict_cell_fixing(db_data[3],edit_UPC)#UPC
                edit_Store = dict_cell_fixing(db_data[4],edit_Store)#Store
    
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
        
        lable_ID_querry()
        log_str = f"MATCHED by csv {upl_csv_path}"#-------------------------------remove#
        update_logger(log_str)#-------------------------------remove#
        if len_each_errors:
            update_logger('\n'.join(len_each_errors))
        try:
            label_loading['text'] = f'100% Loaded -- Elapsed time: {int(hours_)}h,{int(min_)}m,{round(sec_,1)}s'
        except:
            pass
    except AssertionError as e:
        print(e)
        log_str = f"AssertionError ERROR IN CSV EDIT {i}, row:{edit_ASIN}---->{e}"
        print('ROW:', i)
        update_logger(log_str)#-------------------------------remove#

    except IndexError as e:
        print(e)
        log_str = f"IndexError ERROR IN CSV EDIT {i}, row:{edit_ASIN}---->{e}"
        print('ROW:', i)
        update_logger(log_str)#-------------------------------remove#

def cell_fixing(db_cell,input_cell):# edit_bycsv
    cell_fix = []
    cell_split = db_cell.split(':::')
    first_half = input_cell.split('?')[0]
    second_half = '?'.join(input_cell.split('?')[1:])
    
    for cell in cell_split:
        if first_half in cell:
            cell = first_half +'?'+ second_half
        cell_fix.append(cell)
    cell_fix = ':::'.join(cell_fix)
    return cell_fix

def dict_cell_fixing(db_cell,input_cell):
    my_dict = {}
    db_cell_split = filter(None, db_cell.split(':::'))

    
    for x in db_cell_split:#building the dict
        try:
            if x.split('?')[0] in my_dict:
                pass
            else:
                my_dict[x.split('?')[0]] = '?'.join(x.split('?')[1:])
        except:
            pass
    try:#now adding input_cell info to the mix
        db_cell_split = filter(None, input_cell.split(':::'))
        for x in db_cell_split:
            my_dict[x.split('?')[0]] = '?'.join(x.split('?')[1:])
    except:
        pass
    return ':::'.join([k+'?'+my_dict[k] for k in my_dict])


def edit_bycsv():
    global time_str
    sqlite3_backup()
    start_time = time.time()
    
    canvas.filename = filedialog.askopenfilename(initialdir = "c:/", title = "Select CSV", filetypes = (("csv files","*.csv"),("all files","*.*")))
    edit_csv_path = canvas.filename
    
    get_time_call()
    
    if edit_csv_path != '':
    
        con = lite.connect(DB_path)
        cur = con.cursor() 
        #cur.execute("""CREATE TABLE IF NOT EXISTS items(Row INTEGER PRIMARY KEY AUTOINCREMENT,ASIN TEXT,SKU TEXT,UPC TEXT NOT NULL,Store TEXT,SaleChan TEXT,Status TEXT);""")
        
        path = edit_csv_path
        #csv_file = open(path,newline='',encoding='utf-8')
        with open(path,newline='',encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader) #first line is header
            edit_data = [row for row in reader] #reads the remaining data
            
            try:
                con = lite.connect(DB_path)
                cur = con.cursor() 
                row_count = 0
                for each in edit_data:
                    row_count +=1

                    if row_count%150 == 0:
                        elapsed_time = round((time.time() - start_time),2)
            
                        hours_ = elapsed_time//3600
                        min_ = (elapsed_time%3600)//60
                        sec_ = (elapsed_time%60)
                        
                        label_loading['text'] = str(round((row_count/(len(edit_data))*100),2)) + f'% Loading -- Elapsed time: {int(hours_)}h,{int(min_)}m,{round(sec_,1)}s'
                        root.update()
                    
                    
                    if ':::' in each[3] or ':::' in each[4]:
                        item_key = int(each[0].strip())
                        item_asin = each[1].strip()
                        item_sku = each[2].strip()
                        item_upc = each[3].strip()
                        item_store = each[4].strip()
                        item_acc = each[5].strip()
                        item_status = each[6].strip()
                        assert item_status in save_dict.keys()
                        #cur.execute("SELECT * FROM items WHERE Row=?", (item_key,))
                        #db_data = cur.fetchone()
                        
                        #if db_data != None:
                        
                        #print(item_key)
                        querry = f"""UPDATE items SET ASIN = \"{item_asin}\", SKU = \"{item_sku}\", UPC = \"{item_upc}\", Store = \"{item_store}\", SaleChan = \"{item_acc}\", Status = \"{item_status}\" WHERE Row = {item_key}"""
                        cur.execute(querry)
                        #con.commit()
                        
                        
                    else:
                        edit_Row = int(each[0].strip())#Row
                        edit_ASIN = each[1].strip()#ASIN
                        edit_SKU = each[2].strip()#SKU
                        edit_UPC = each[3].strip()#UPC
                        edit_Store = each[4].strip()#Store
                        edit_SaleChan = each[5].strip()#SaleChan
                        edit_Status = each[6].strip()#Status
                        assert edit_Status in save_dict.keys()
                        
                        cur.execute("SELECT * FROM items WHERE Row=?", (edit_Row,))
                        db_data = cur.fetchone()
                        
                        #print(db_data)
                        
                        if db_data != None:
                            '''edit_Row = db_data[0]#Row
                            edit_ASIN = db_data[1]#ASIN
                            edit_SKU = db_data[2]#SKU'''
                            edit_UPC = dict_cell_fixing(db_data[3],edit_UPC)#UPC
                            edit_Store = dict_cell_fixing(db_data[4],edit_Store)#Store
                            '''edit_SaleChan = db_data[5]#SaleChan
                            edit_Status = db_data[6]#Status'''
                            
                            #print(edit_Row)
                            querry = f"""UPDATE items SET ASIN = \"{edit_ASIN}\", SKU = \"{edit_SKU}\", UPC = \"{edit_UPC}\", Store = \"{edit_Store}\", SaleChan = \"{edit_SaleChan}\", Status = \"{edit_Status}\" WHERE Row = {edit_Row}"""
                            cur.execute(querry)
                            
                
                con.commit()          
                con.close()
                
                log_str = f"EDITED BY CSV {edit_csv_path}"
                try:
                    label_loading['text'] = f'100% Loaded -- Elapsed time: {int(hours_)}h,{int(min_)}m,{round(sec_,1)}s'
                except:
                    pass
                update_logger(log_str)
                
                
            except Exception as e:
                print(e)
                log_str = f"ERROR IN CSV EDIT---->{e}"
                update_logger(log_str)


def upload_single():
    global top_asin_Entry
    global top_sku_Entry
    global top_upc_Entry
    global top_store_Entry
    global top_acc_Entry
    global top_status_Entry
    
    window_upload_single = Toplevel(root)
    window_upload_single.title('Clean Inventory')
    window_upload_single.configure(background="black")
    window_upload_single.resizable(False, False)
   # window_upload_single.geometry("400x400")
    
    
    top_asin_lable = Label(window_upload_single,text = 'ASIN', width = 10, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)
    top_sku_lable = Label(window_upload_single,text = 'SKU', width = 10, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)
    top_upc_lable = Label(window_upload_single,text = 'UPC', width = 10, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)
    top_store_lable = Label(window_upload_single,text = 'Store', width = 10, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)
    top_acc_lable = Label(window_upload_single,text = 'SaleChan', width = 10, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)
    top_status_lable = Label(window_upload_single,text = 'Status', width = 10, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)
    
    top_asin_Entry = Entry(window_upload_single,text = 'ASIN', width = 25, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14))
    top_sku_Entry = Entry(window_upload_single,text = 'SKU', width = 25, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14))
    top_upc_Entry = Entry(window_upload_single,text = 'UPC', width = 25, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14))
    top_store_Entry = Entry(window_upload_single,text = 'Store', width = 25, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14))
    top_acc_Entry = Entry(window_upload_single,text = 'SaleChan', width = 25, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14))
    top_status_Entry = Entry(window_upload_single,text = 'Status', width = 25, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14))
    
    top_button = Button(window_upload_single,text = 'SUBMIT', width = 35, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), command = upload_single_submit_bttn)
    
    top_asin_lable.grid(row=0, column=0 , sticky = S)
    top_sku_lable.grid(row=1, column=0 , sticky = S)
    top_upc_lable.grid(row=2, column=0 , sticky = S)
    top_store_lable.grid(row=3, column=0 , sticky = S)
    top_acc_lable.grid(row=4, column=0 , sticky = S)
    top_status_lable.grid(row=5, column=0 , sticky = S)
    
    top_asin_Entry.grid(row=0, column=1 , sticky = N)
    top_sku_Entry.grid(row=1, column=1 , sticky = N)
    top_upc_Entry.grid(row=2, column=1 , sticky = N)
    top_store_Entry.grid(row=3, column=1 , sticky = N)
    top_acc_Entry.grid(row=4, column=1 , sticky = N)
    top_status_Entry.grid(row=5, column=1 , sticky = N)
    
    top_button.grid(row=6, column=0 ,columnspan=2, sticky = N)


def upload_single_submit_bttn():
    
    data_us = []
    
    data_us.append(top_asin_Entry.get())
    data_us.append(top_sku_Entry.get())
    data_us.append(top_upc_Entry.get())
    data_us.append(top_store_Entry.get())
    data_us.append(top_acc_Entry.get())
    data_us.append(top_status_Entry.get())
    
    top_asin_Entry.delete(0,END)
    top_sku_Entry.delete(0,END)
    top_upc_Entry.delete(0,END)
    top_store_Entry.delete(0,END)
    top_acc_Entry.delete(0,END)
    top_status_Entry.delete(0,END)
    
    data_us = tuple(data_us)
    
    if data_us[0] != '' and data_us[1] != '' and data_us[2] != '' and data_us[3] != '' and data_us[4] != '' and data_us[5] != '':
        con = lite.connect(DB_path)
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS items(Row INTEGER PRIMARY KEY AUTOINCREMENT,ASIN TEXT,SKU TEXT,UPC TEXT NOT NULL,Store TEXT,SaleChan TEXT,Status TEXT);""")
        cur.executemany("""INSERT INTO items (ASIN,SKU,UPC,Store,SaleChan,Status) VALUES (?,?,?,?,?,?);""", [data_us])
        con.commit()
        con.close() 
        
        lable_ID_querry()
        
        log_str = f"Uploaded single item with UPC = {data_us[2]}"
        update_logger(log_str)
    
    lable_ID_querry()

def lable_ID_querry():
    global lable_ID
    try:
        con = lite.connect(DB_path)
        cur = con.cursor()
        con = lite.connect(DB_path)
        cur = con.cursor()
        cur.execute("SELECT Row FROM items")
        result = cur.fetchall()
        label_ID_inDB['text'] = len(result)
    except:
        DB_path_btn_color = 'red'
        rows_label_text = "0"
        label_ID_inDB['text'] = 'err'
    con.close()


def DB_path_funct():
    global DB_path
    #global upl_csv_path
    canvas.filename = filedialog.askopenfilename(initialdir = "c:/", title = "Select CSV", filetypes = (("csv files","*.csv"),("all files","*.*")))
    DB_path = canvas.filename
    root.destroy()
    #canvas.destroy()


def get_filter_val():

    global save_dict
    
    # Store
    save_dict["MF?"] = MF.get()
    save_dict["M123?"] = M123.get()
    save_dict["WW?"] = WW.get()
    save_dict["GC?"] = GC.get()
    save_dict["PBA?"] = PBA.get()
    save_dict["PAS?"] = PAS.get()
    save_dict["MSL?"] = MSL.get()
    save_dict["PC?"] = PC.get()
    save_dict["SW?"] = SW.get()
    save_dict["ZOR?"] = ZOR.get()
    save_dict["VIP?"] = VIP.get()
    save_dict["SAM?"] = SAM.get()
    save_dict["FORZ?"] = FORZ.get()
    save_dict["CPO?"] = CPO.get()
    save_dict["ABN?"] = ABN.get()
    save_dict["PNM?"] = PNM.get()
    
    # SaleChan
    save_dict["AmD"] = AmD.get()
    save_dict["AmM"] = AmM.get()
    save_dict["AmS"] = AmS.get()
    
    #Status
    save_dict["redBrands"] = redBrands.get()
    save_dict["other"] = other.get()
    save_dict["active"] = active.get()
    save_dict["actNoRep"] = actNoRep.get()
    save_dict["notComp"] = notComp.get()
    save_dict["closed"] = closed.get()
    save_dict["deleted"] = deleted.get()
    save_dict["ToBList"] = ToBList.get()
    save_dict["ToBCheckd"] = ToBCheckd.get()


def search_func():
    global querry
    global count_searches
    global result
    
    #------SEARCH BARS
    
    item_asin = entry_ASIN.get()
    item_sku = entry_SKU.get()
    item_upc = entry_UPC.get()
    
    get_filter_val()
    
    #-----FILTERS
    Store_list_querry = ''
    SaleChan_list_querry = ''
    Status_list_querry = ''
    
    
    Store_list = ["MF?","WW?","M123?","GC?","PBA?","PAS?","MSL?",
                  "PC?","SW?","ZOR?","VIP?","SAM?","FORZ?","CPO?","ABN?","PNM?"]
    SaleChan_list  = ["AmD","AmM","AmS"]
    Status_list = ["redBrands","other","active","actNoRep","notComp","closed",
                   "deleted","ToBList","ToBCheckd"]

    
    c = 0
    m = 0
    for x in Store_list:
        if save_dict[x] == 1:
            if c == 0:
                Store_list_querry = '('
            #print('add to querry')
            Store_list_querry = Store_list_querry + f"Store LIKE '%{x}%' OR "
            c+=1
        if m == (len(Store_list)-1) and c!=0:
            Store_list_querry = Store_list_querry[0:(len(Store_list_querry)-4)] +')'
        m+=1
    
    
    c = 0
    m = 0
    for x in SaleChan_list:
        save_dict[x]
        if save_dict[x] == 1:
            if c == 0:
                SaleChan_list_querry = '('
            #print('add to querry')
            SaleChan_list_querry = SaleChan_list_querry + f"SaleChan LIKE '%{x}%' OR "
            c+=1
        if m == (len(SaleChan_list)-1) and c!=0:
            SaleChan_list_querry = SaleChan_list_querry[0:(len(SaleChan_list_querry)-4)] +')'
        m+=1
    
    
    c = 0
    m = 0
    for x in Status_list:
        save_dict[x]
        if save_dict[x] == 1:
            if c == 0:
                Status_list_querry = '('
            #print('add to querry')
            Status_list_querry = Status_list_querry + f"Status = '{x}' OR "
            c+=1
        if m == (len(Status_list)-1) and c!=0:
            Status_list_querry = Status_list_querry[0:(len(Status_list_querry)-4)] +')'
        m+=1
    
    #print(Store_list_querry+'\n')
    #print(SaleChan_list_querry+'\n')
    #print(Status_list_querry+'\n')
    #print(save_dict)
    
    #------FILTERS
    
    querry = "SELECT * FROM 'items'"
    
    if item_asin != '' or item_sku != '' or item_upc != '':
    
        if item_asin != '':
            item_asin_querry = f"(ASIN = '{item_asin}')"
            if 'WHERE (' not in querry:
                querry = querry +' WHERE ('+ item_asin_querry
            else:
                querry = " OR".join([querry , item_asin_querry])
            
        if item_sku != '':
            item_sku_querry = f"(SKU = '{item_sku}')"
            if 'WHERE (' not in querry:
                querry = querry +' WHERE ('+ item_sku_querry
            else:
                querry = " OR".join([querry , item_sku_querry])
                
        if item_upc != '':
            item_upc_querry = f"(UPC LIKE '%{item_upc}%')"
            if 'WHERE (' not in querry:
                querry = querry +' WHERE ('+ item_upc_querry
            else:
                querry = " OR".join([querry , item_upc_querry])
        
        querry = querry + ")"

            
    if Store_list_querry != '':
        if 'WHERE' not in querry:
            querry = querry +' WHERE '+ Store_list_querry
        else:
            querry = " AND".join([querry , Store_list_querry])
    
    if SaleChan_list_querry != '':
        if 'WHERE' not in querry:
            querry = querry +' WHERE '+ SaleChan_list_querry
        else:
            querry = " AND".join([querry , SaleChan_list_querry])
    
    if Status_list_querry != '':
        if 'WHERE' not in querry:
            querry = querry +' WHERE '+ Status_list_querry
        else:
            querry = " AND".join([querry , Status_list_querry])
    
    '''print(Store_list_querry+'\n')
    print(SaleChan_list_querry+'\n')
    print(Status_list_querry+'\n')
    print(querry)'''
    
    listNodes.delete(0, END)
    
    con = lite.connect(DB_path)
    cur = con.cursor() 
    cur.execute(querry)
    result = cur.fetchall()
    #print(result)
    
    con.close()
    count_searches = 0
    
    for each in result:
        listNodes.insert(END,(str(each[0]),'|',each[1],'|',each[2],'|',each[3],'|',each[4],'|',each[5],'|',each[6]))
        listNodes.insert(END,('_'))
        
        if count_searches%10000 == 0:#update root windol on every 10k
            root.update()
        count_searches += 1

        label_loading['text'] = str(round((count_searches/len(result)*100),2)) + '% Loading'
    
    if len(result) != 0:
        label_loading['text'] = str(round((count_searches/len(result)*100),2)) + '% Loaded'
    lable_ID['text'] = count_searches
    canvas.delete('canvas_text_6')
    canvas.create_text(50,460, anchor = 'nw', text = "|Row_|___ASIN___|____SKU____|__________UPC__________|__Store__|__SLC__|__Status__|",font=("Courier", 18,"underline bold"),fill = 'white', tags=('canvas_text_6',))


def asin_duplicates_funct():
    global result
    listNodes.delete(0,END)
    
    con = lite.connect(DB_path)
    cur = con.cursor() 
    
    query = 'SELECT *,COUNT(ASIN) as c FROM items GROUP BY ASIN HAVING ( COUNT(ASIN) > 1 ) ORDER BY c DESC;'
    cur.execute(query)
    result = cur.fetchall()
    
    con.close()
    
    listNodes.delete(0,END)
    count_searches = 0
    
    for each in result:
        listNodes.insert(END,(str(each[0]),'|',each[1],'|',each[2],'|',each[3],'|',each[4],'|',each[5],'|',each[6],'|',str(each[7])))
        listNodes.insert(END,('_'))
        count_searches += 1
    
    lable_ID['text'] = count_searches
    canvas.delete('canvas_text_6')
    canvas.create_text(50,460, anchor = 'nw', text = "|Row_|___ASIN___|____SKU____|__________UPC__________|__Store__|__SLC__|__Status__|_ASIN_DUPL_|",font=("Courier", 18,"underline bold"),fill = 'white', tags=('canvas_text_6',))


def sku_duplicates_funct():
    global result
    listNodes.delete(0,END)
    
    con = lite.connect(DB_path)
    cur = con.cursor() 
    
    query = 'SELECT *,COUNT(SKU) as c FROM items GROUP BY SKU HAVING ( COUNT(SKU) > 1 ) ORDER BY c DESC;'
    cur.execute(query)
    result = cur.fetchall()
    
    con.close()
    
    listNodes.delete(0,END)
    count_searches = 0
    
    for each in result:
        listNodes.insert(END,(str(each[0]),'|',each[1],'|',each[2],'|',each[3],'|',each[4],'|',each[5],'|',each[6],'|',str(each[7])))
        listNodes.insert(END,('_'))
        count_searches += 1
    
    lable_ID['text'] = count_searches
    canvas.delete('canvas_text_6')
    canvas.create_text(50,460, anchor = 'nw', text = "|Row_|___ASIN___|____SKU____|__________UPC__________|__Store__|__SLC__|__Status__|_SKU_DUPL__|",font=("Courier", 18,"underline bold"),fill = 'white', tags=('canvas_text_6',))


def csv_search_func():
    global querry
    global time_str

    csv_search_result = []
    csv_notfound_result = []
    #------SEARCH BARS
    start_time = time.time()

    canvas.filename = filedialog.askopenfilename(initialdir = "c:/", title = "Select CSV", filetypes = (("csv files","*.csv"),("all files","*.*")))
    path = canvas.filename

    line_count = sum(1 for line in open(path))-1
    
    with open(path,'r',newline='',encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
    
        row_count = 0

        header = next(reader) #first line is header
        for row in reader: #reads the remaining data
            
            
            item_asin = row[0]
            item_sku = row[1]
            item_upc = row[2]
            
            #------FILTERS
            
            querry = "SELECT * FROM 'items'"
            
            con = lite.connect(DB_path)
            cur = con.cursor() 
            
            if item_asin != '' or item_sku != '' or item_upc != '':
            
                if item_asin != '':
                    item_asin_querry = f"(ASIN = '{item_asin}')"
                    if 'WHERE (' not in querry:
                        querry = querry +' WHERE ('+ item_asin_querry
                    else:
                        querry = " OR".join([querry , item_asin_querry])
                    
                if item_sku != '':
                    item_sku_querry = f"(SKU = '{item_sku}')"
                    if 'WHERE (' not in querry:
                        querry = querry +' WHERE ('+ item_sku_querry
                    else:
                        querry = " OR".join([querry , item_sku_querry])
                        
                if item_upc != '':
                    item_upc_querry = f"(UPC LIKE '%{item_upc}%')"
                    if 'WHERE (' not in querry:
                        querry = querry +' WHERE ('+ item_upc_querry
                    else:
                        querry = " OR".join([querry , item_upc_querry])
                
                querry = querry + ")"
            
            cur.execute(querry)
            result = cur.fetchall()
            if row_count%15 == 0:
                root.update()
                
                elapsed_time = round((time.time() - start_time),2)
    
                hours_ = elapsed_time//3600
                min_ = (elapsed_time%3600)//60
                sec_ = (elapsed_time%60)
                
                label_loading['text'] = str(round((row_count/(line_count)*100),2)) + f'% Loading -- Elapsed time: {int(hours_)}h,{int(min_)}m,{round(sec_,1)}s'
                #print("\n",int(hours_),'Hours,',int(min_),'min,',round(sec_,1),'sec.')
    
                
            row_count +=1
            if result == []:
                csv_notfound_result = csv_notfound_result + [(item_asin,item_sku,item_upc)]
                
            else:
                csv_search_result = csv_search_result + result

    if line_count !=0:
        label_loading['text'] = str(round((row_count/(line_count)*100),2)) + f'% Loaded -- Elapsed time: {int(hours_)}h,{int(min_)}m,{round(sec_,1)}s'
    csv_search_result = list( dict.fromkeys(csv_search_result))
    con.close()
    
    get_time_call()
    
    file_name = time_str +" CSV SEARCH.csv"
    csv_export = DB_filepath_strip(DB_path,file_name)
    
    with open(csv_export,'w',newline='',encoding='utf-8') as csv_file:
    	csv_writer = csv.writer(csv_file, delimiter=',')
    	headers = ['Row', 'ASIN', 'SKU','UPC', 'Store', 'SaleChan', 'Status']
    	csv_writer.writerow(headers)
        
    	for each in csv_search_result:
            str_0 = each[0]#Row
            str_1 = each[1]#ASIN
            str_2 = each[2]#SKU
            str_3 = each[3]#UPC
            str_4 = each[4]#Store
            str_5 = each[5]#SaleChan
            str_6 = each[6]#Status
            csv_writer.writerow([str_0, str_1, str_2,str_3,str_4,str_5,str_6])
            
    file_name = time_str +" CSV SEARCH NOT FOUND.csv"
    csv_export = DB_filepath_strip(DB_path,file_name)
    
    with open(csv_export,'w',newline='',encoding='utf-8') as csv_file:
    	csv_writer = csv.writer(csv_file, delimiter=',')
    	headers = ['ASIN', 'SKU','UPC']
    	csv_writer.writerow(headers)
        
    	for each in csv_notfound_result:
            str_0 = each[0]
            str_1 = each[1]
            str_2 = each[2]
            csv_writer.writerow([str_0, str_1, str_2])


def export_csv_func():
    global time_str
    get_time_call()
    
    print (time_str)
    file_name = str(time_str) +" CSV export.csv"
    csv_export = DB_filepath_strip(DB_path,file_name)
    print(csv_export,"<----------")
    
    
    with open(csv_export,'w',newline='',encoding='utf-8') as csv_file:
    	csv_writer = csv.writer(csv_file, delimiter=',')
    	headers = ['Row', 'ASIN', 'SKU','UPC', 'Store', 'SaleChan', 'Status']
    	csv_writer.writerow(headers)
        
    	for each in result:

            str_0 = each[0]#Row
            str_1 = each[1]#ASIN
            str_2 = each[2]#SKU
            str_3 = each[3]#UPC
            str_4 = each[4]#Store
            str_5 = each[5]#SaleChan
            str_6 = each[6]#Status
            csv_writer.writerow([str_0, str_1, str_2,str_3,str_4,str_5,str_6])
    
    listNodes.delete(0,END)

def edit_single():
    entry_var = entry_edit.get()
    entry_edit.delete(0,END)
    edit_single_inner(entry_var)
    #print('edit single')


def edit_single_inner(x):
    #item_key,item_asin,item_sku,item_upc,item_store,item_acc,item_status
    global entry_edit
    try:
        #x = x.replace(" ","")
        x = x.split(" | ")
        item_key = int(x[0])
        if item_key =='':
            raise Exception()
        item_asin = x[1].strip()
        item_sku = x[2].strip()
        item_upc = x[3].strip()
        item_store = x[4].strip()
        item_acc = x[5].strip()
        item_status = x[6].strip()
        assert item_status in save_dict.keys()

        # ADD all querry for editing hire
        
        con = lite.connect(DB_path)
        cur = con.cursor() 
        
        querry = f"""UPDATE items SET ASIN = \"{item_asin}\", SKU = \"{item_sku}\", UPC = \"{item_upc}\", Store = \"{item_store}\", SaleChan = \"{item_acc}\", Status = \"{item_status}\" WHERE Row = {item_key}"""
        cur.execute(querry)
        con.commit()
        con.close()
        
        log_str = f"""EDITED single SKU = {item_sku}, ASIN = {item_asin}"""
        update_logger(log_str)
    except:
        entry_edit.insert(0,"""Row | ASIN | SKU | UPC | Store | SLC | Status -= Row or Status may have typos =-""")
    

def list_doubleclick_handler(event):
    global ACTIVE_handle
    ACTIVE_handle = listNodes.get(ACTIVE)
    entry_edit.delete(0,END)
    item_str = ' '.join(ACTIVE_handle)
    entry_edit.insert(0,item_str)

#--------------------------------------BUTTONS DEFINE-----------------------------------------#
    
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
save_dict = load_json_file(BASE_DIR)
DB_path = DB_filepath_read(BASE_DIR)
global time_str
time_str = get_time_call()

root = Tk()
root.title('Clean Inventory')
root.configure(background="black")
root.resizable(False, False)
#root.geometry("400x400")

try: #conn test
    con = lite.connect(DB_path)
    cur = con.cursor()
    cur.execute("SELECT Row FROM items")
    result = cur.fetchall()
    rows_label_text = len(result)
    con.close()
    DB_path_btn_color = 'silver'
    del result
except:
    DB_path_btn_color = 'red'
    rows_label_text = "0"


#--------------------------------------CANVAS-----------------------------------------#
back_ground = ImageTk.PhotoImage(Image.open('Images/1600_935_bg.jpg'))

canvas = Canvas(root, width=1600, height=935)
canvas.pack(side=LEFT, fill=BOTH, expand=True)
canvas.configure(background="black")
canvas.create_image(0, 0, image = back_ground, anchor=N+W)


#--------------------------------------CANVAS-----------------------------------------#


#--------------------------------------LOGGER-----------------------------------------#

logg_frame = Frame(canvas)
canvas.create_window(900,100, anchor = 'nw',window=logg_frame)
canvas.create_text(900,60, anchor = 'nw', text = "|___DATE-TIME___|______LOGGER______|",font=("Courier", 18,"underline bold"),fill = 'white', tags=('canvas_text_7',))


file_name = "Log.txt"
logger_path = DB_filepath_strip(DB_path,file_name)

#logger_path = DB_path.split("/")
#logger_path = logger_path[0:(len(logger_path)-1)] + ["Log.txt"]
#logger_path =  "/".join(logger_path)

listNodes_logger = Listbox(logg_frame, width=65, height=10, font=("Courier", 12 , "underline bold"),bg = 'black',fg= "white", selectforeground= "black" ,selectbackground='white')
listNodes_logger.pack(side="left", fill="y")

try:
    with open(logger_path, 'r') as save_file:
        for line in save_file:
            listNodes_logger.insert(END,(line+" |"))
            listNodes_logger.insert(END,('_'))
except:
    listNodes_logger.insert(END,("Log.txt file path error"))

#for x in range(30):
#    listNodes.insert(END,(str(x),'|','date-time','|','EVENT-TO-BE-LOGGED','|'))
#    listNodes.insert(END,('_'))

#Listbox.delete(0, END)
#Listbox.insert(END, newitem)

scrollbar = Scrollbar(logg_frame, orient="vertical")
scrollbar.config(command=listNodes_logger.yview)
scrollbar.pack(side="right", fill="y")

listNodes_logger.yview_moveto('1.0')
listNodes_logger.config(yscrollcommand=scrollbar.set)


#--------------------------------------LOGGER-----------------------------------------#


#--------------------------------------MAIN PREVEW------------------------------------#


frame = Frame(canvas)
canvas.create_window(50,500, anchor = 'nw',window=frame)
canvas.create_text(50,460, anchor = 'nw', text = "|Row_|___ASIN___|____SKU____|__________UPC__________|__Store__|__SLC__|__Status__|",font=("Courier", 18,"underline bold"),fill = 'white', tags=('canvas_text_6',))


listNodes = Listbox(frame, width=115, height=15, font=("Courier", 16 , "underline bold"),bg = 'black',fg= "white", selectforeground= "black" ,selectbackground='white')
listNodes.pack(side="left", fill="y")

listNodes.bind('<Double-Button-1>', list_doubleclick_handler)

scrollbar = Scrollbar(frame, orient="vertical")
scrollbar.config(command=listNodes.yview)
scrollbar.pack(side="right", fill="y")

listNodes.config(yscrollcommand=scrollbar.set)

#--------------------------------------MAIN PREVEW------------------------------------#


#--------------------------------------FILTERS menu checkbutton-----------------------#
filter_frame = Frame(canvas)
canvas.create_window(350,60, anchor = 'nw',window=filter_frame)
#canvas_text = canvas.create_text(830,70, anchor = 'nw', text = ">>DATA BASE FILTERS<<",font=("Helvetica", 14),fill = 'white', tags=('canvas_text_2',))

# tk checkbox values-----------

# Store -- tkinter variables
MF = IntVar()   #0
WW = IntVar()   #1
M123 = IntVar() #2
GC = IntVar()   #3
PBA = IntVar()  #4
PAS = IntVar()  #5
MSL = IntVar()  #6
PC = IntVar()   #7
SW = IntVar()   #8
ZOR = IntVar()  #9
VIP = IntVar()  #10
SAM = IntVar()  #11
FORZ = IntVar()  #12
CPO = IntVar()  #13
ABN = IntVar()  #14
PNM = IntVar()  #15

# Store -- set variables
MF.set(int(save_dict["MF?"]))   #0
WW.set(int(save_dict["WW?"]))   #1
M123.set(int(save_dict["M123?"])) #2
GC.set(int(save_dict["GC?"]))    #3
PBA.set(int(save_dict["PBA?"]))  #4
PAS.set(int(save_dict["PAS?"]))  #5
MSL.set(int(save_dict["MSL?"]))  #6
PC.set(int(save_dict["PC?"]))    #7
SW.set(int(save_dict["SW?"]))    #8
ZOR.set(int(save_dict["ZOR?"]))  #9
VIP.set(int(save_dict["VIP?"]))  #10
SAM.set(int(save_dict["SAM?"]))  #11
FORZ.set(int(save_dict["FORZ?"]))  #12
CPO.set(int(save_dict["CPO?"]))  #13
ABN.set(int(save_dict["ABN?"]))  #14
PNM.set(int(save_dict["PNM?"]))  #14

# SaleChan
AmD = IntVar()
AmM = IntVar()
AmS = IntVar()

AmD.set(int(save_dict["AmD"]))
AmM.set(int(save_dict["AmM"]))
AmS.set(int(save_dict["AmS"]))

#Status

active = IntVar()
active.set(int(save_dict["active"]))

actNoRep = IntVar()
actNoRep.set(int(save_dict["actNoRep"]))

notComp = IntVar()
notComp.set(int(save_dict["notComp"]))

closed = IntVar()
closed.set(int(save_dict["closed"]))

redBrands = IntVar()
redBrands.set(int(save_dict["redBrands"]))

other =IntVar()
other.set(int(save_dict["other"]))

deleted = IntVar()
deleted.set(int(save_dict["deleted"]))

ToBList = IntVar()
ToBList.set(int(save_dict["ToBList"]))

ToBCheckd = IntVar()
ToBCheckd.set(int(save_dict["ToBCheckd"]))

# menue define----------

# Store
Store_menue =  Menubutton ( filter_frame, text="Store Filter",padx = 22,bg = 'silver',activebackground='white', borderwidth=5,font=("Helvetica", 14), relief=RAISED )
Store_menue.menu  =  Menu ( Store_menue, tearoff = 1, bg = 'white',activebackground='black')
Store_menue["menu"]  =  Store_menue.menu
Store_menue.pack(side="left", fill="y")

Store_menue.menu.add_checkbutton ( label="GC                            ", variable = GC)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="MF", variable = MF)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="WW", variable = WW)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="M123", variable = M123)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="PBA", variable = PBA)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="PAS", variable = PAS)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="MSL", variable = MSL)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="PC", variable = PC)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="SW", variable = SW)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="ZOR", variable = ZOR)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="VIP", variable = VIP)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="SAM", variable = SAM)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="FORZ", variable = FORZ)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="CPO", variable = CPO)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="ABN", variable = ABN)
Store_menue.menu.add_separator()
Store_menue.menu.add_checkbutton ( label="PNM", variable = PNM)

#SaleChan
SaleChan_menue =  Menubutton ( filter_frame, text="SaleChan Filter",padx = 22,bg = 'silver',activebackground='white',borderwidth=5,font=("Helvetica", 14), relief=RAISED )
SaleChan_menue.menu  =  Menu ( SaleChan_menue, tearoff = 1, bg = 'white',activebackground='black')
SaleChan_menue["menu"]  =  SaleChan_menue.menu
SaleChan_menue.pack(side="left", fill="y")

SaleChan_menue.menu.add_checkbutton ( label="AmD                                    ", variable = AmD)
SaleChan_menue.menu.add_separator()
SaleChan_menue.menu.add_checkbutton ( label="AmM", variable = AmM)
SaleChan_menue.menu.add_separator()
SaleChan_menue.menu.add_checkbutton ( label="AmS", variable = AmS)


#Status
Status_menue =  Menubutton ( filter_frame, text="Status Filter",padx = 22, bg = 'silver',activebackground='white', borderwidth=5,font=("Helvetica", 14), relief=RAISED )
Status_menue.menu  =  Menu ( Status_menue, tearoff = 1, bg = 'white',activebackground='black')
Status_menue["menu"]  =  Status_menue.menu
Status_menue.pack(side="left", fill="y")

Status_menue.menu.add_checkbutton ( label="active                         ", variable = active)
Status_menue.menu.add_separator()
Status_menue.menu.add_checkbutton ( label="actNoRep", variable = actNoRep)
Status_menue.menu.add_separator()
Status_menue.menu.add_checkbutton ( label="notComp", variable = notComp)
Status_menue.menu.add_separator()
Status_menue.menu.add_checkbutton ( label="closed", variable = closed)
Status_menue.menu.add_separator()
Status_menue.menu.add_checkbutton ( label="redBrands", variable = redBrands)
Status_menue.menu.add_separator()
Status_menue.menu.add_checkbutton ( label="deleted", variable = deleted)
Status_menue.menu.add_separator()
Status_menue.menu.add_checkbutton ( label="other", variable = other)
Status_menue.menu.add_separator()
Status_menue.menu.add_checkbutton ( label="ToBList", variable = ToBList)
Status_menue.menu.add_separator()
Status_menue.menu.add_checkbutton ( label="ToBCheckd", variable = ToBCheckd)

#--------------------------------------FILTERS menu checkbutton-----------------------#


#--------------------------------------Buttons------------------------------------#

btn_img = ImageTk.PhotoImage(Image.open('Images/60_60_buttn.jpg'))
csv_upl_img = ImageTk.PhotoImage(Image.open('Images/60x60upl_csv.jpg'))
csv_edit_img = ImageTk.PhotoImage(Image.open('Images/60x60edit_btn.png'))


upload_bysingle_btn = Button(canvas,image=btn_img, bg = 'black',activebackground='silver', command=upload_single)
upload_bycsv_btn = Button(canvas,image=csv_upl_img, bg = 'black',activebackground='silver', command=upload_by_csv_smart)
edit_bycsv_btn = Button(canvas,image=csv_edit_img, bg = 'black',activebackground='silver', command=edit_bycsv)


edit_one_btn = Button(canvas, text = "EDIT", bg = DB_path_btn_color ,activebackground='white',width = 15, borderwidth=5,font=("Helvetica", 11, "bold"), command=edit_single)
DB_path_btn = Button(canvas, text = "SET DB", bg = DB_path_btn_color ,activebackground='white',width = 15,height=2, borderwidth=5,font=("Helvetica", 11, "bold"), command=DB_path_funct)
DB_backup_btn = Button(canvas, text = "BACKUP DB", bg = DB_path_btn_color ,activebackground='white',width = 11,height=2, borderwidth=5,font=("Helvetica", 11, "bold"), command=sqlite3_backup)


search_btns_frame = Frame(canvas)
search_btn = Button(search_btns_frame, text = "SEARCH", bg = DB_path_btn_color ,activebackground='white',width = 10, borderwidth=5,font=("Helvetica", 11, "bold"), command=search_func)
search_csv_btn = Button(search_btns_frame, text = "CSV SEARCH", bg = DB_path_btn_color ,activebackground='white',width = 11, borderwidth=5,font=("Helvetica", 11, "bold"), command=csv_search_func)
export_csv_btn = Button(search_btns_frame, text = "EXPORT SEARCH", bg = 'silver',activebackground='white',width = 16, borderwidth=5,font=("Helvetica", 11, "bold"), command=export_csv_func)
search_btn.pack(side="left", fill="y")
search_csv_btn.pack(side="left", fill="y")
export_csv_btn.pack(side="left", fill="y")


duplicate_btns_frame = Frame(canvas)
asin_dupl_btn = Button(duplicate_btns_frame, text = "ASIN", bg = DB_path_btn_color ,activebackground='white',width = 4, borderwidth=5,font=("Helvetica", 11, "bold"), command=asin_duplicates_funct)
upc_dupl_btn = Button(duplicate_btns_frame, text = "SKU", bg = DB_path_btn_color ,activebackground='white',width = 4, borderwidth=5,font=("Helvetica", 11, "bold"), command=sku_duplicates_funct)
asin_dupl_btn.pack(side="left", fill="y")
upc_dupl_btn.pack(side="left", fill="y")


canvas.create_window(50,350, anchor = 'nw',window = duplicate_btns_frame)
canvas.create_window(818,425, anchor = 'nw',window = search_btns_frame)

canvas.create_window(50,60, anchor = 'nw',window = upload_bysingle_btn)
canvas.create_window(50,160, anchor = 'nw',window = upload_bycsv_btn)
canvas.create_window(50,260, anchor = 'nw',window = edit_bycsv_btn)
canvas.create_window(1400,880, anchor = 'nw',window = edit_one_btn)
canvas.create_window(1400,425, anchor = 'nw',window = DB_path_btn)
canvas.create_window(1260,425, anchor = 'nw',window = DB_backup_btn)

canvas.create_text(100,80, anchor = 'nw', text = ">>>UPLOAD ONE",font=("Helvetica", 14),fill = 'white', tags=('canvas_text_1',))
#canvas.create_text(100,180, anchor = 'nw', text = ">>>UPLOAD by CSV",font=("Helvetica", 14),fill = 'white', tags=('canvas_text_2',))
#canvas.create_text(100,280, anchor = 'nw', text = ">>>EDIT by CSV",font=("Helvetica", 14),fill = 'white', tags=('canvas_text_3',))

#--------------------------------------Buttons------------------------------------#

#--------------------------------------Entry,labels-------------------------------#

search_frame = Frame(canvas)

lable_ID = Label(search_frame,text= "0", width = 6, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)
entry_ASIN = Entry(search_frame, width = 13, borderwidth=5, bg = 'silver',font=("Helvetica", 14))
entry_SKU = Entry(search_frame, width = 14, borderwidth=5, bg = 'silver',font=("Helvetica", 14))
entry_UPC = Entry(search_frame, width = 30, borderwidth=5, bg = 'silver',font=("Helvetica", 14))

lable_ID.pack(side="left", fill="y")
entry_ASIN.pack(side="left", fill="y")
entry_SKU.pack(side="left", fill="y")
entry_UPC.pack(side="left", fill="y")


entry_edit = Entry(canvas, width = 120, borderwidth=5, bg = 'silver',font=("Helvetica", 14))
entry_edit.insert(0,'ID | ASIN | SKU | UPC | Store | SLC | Status')
label_ID_inDB = Label(canvas,text=rows_label_text, width = 6, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)
label_loading = Label(canvas,text='loading label', width = 43, borderwidth=4, bg = 'white',fg = 'black',font=("Helvetica", 14), relief=RAISED)


canvas.create_window(50,390, anchor = 'nw',window = label_ID_inDB)
canvas.create_text(150,355, anchor = 'nw', text = ">>SHOW DUPLICATES",font=("Helvetica", 14),fill = 'white', tags=('canvas_text_8',))
canvas.create_text(130,393, anchor = 'nw', text = ">>>>RECORDS IN DB",font=("Helvetica", 14),fill = 'white', tags=('canvas_text_8',))
canvas.create_window(50,425, anchor = 'nw',window=search_frame)
canvas.create_window(50,880, anchor = 'nw',window = entry_edit)
canvas.create_window(350,110, anchor = 'nw',window = label_loading)
#--------------------------------------Entry,labels-----------------------------------#

mainloop()

#--------------------------------------End of program--------------------------------#

#get the filter values befor closeing the app
get_filter_val()
save_json_file(BASE_DIR)
DB_filepath_write(BASE_DIR,DB_path)

try:
    sqlite3_backup()
    if con:
        con.close()
except:
    pass
    #"""
