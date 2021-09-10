# -*- coding: utf-8 -*-
"""
Created on Fri May  1 19:34:42 2020

@author: CoilingDragon
"""
import datetime
import time
import sqlite3 as lite
import csv


# PythonDecorators/decorator_without_arguments.py
class decorator_without_arguments:
    """MORE ON DECORATORS - https://python-3-patterns-idioms-test.readthedocs.io/en/latest/PythonDecorators.html"""

    
    def __init__(self, f):
        """
        If there are no decorator arguments, the function
        to be decorated is passed to the constructor.
        """
        print("Inside __init__()")
        self.f = f



    def __call__(self, *args, **kwargs):
        """
        The __call__ method is not called until the
        decorated function is called.
        """
        print("Inside __call__()")
        start = datetime.datetime.now()
        
        print(self.testing())
        self.f(*args)
        
        print("After self.f(*args)")
        elapsed = datetime.datetime.now()                      
        print("Elapsed Time = {0}".format(elapsed-start)) 
        
        
    def testing(self):

        return "\ntest"




#print("Preparing to call sayHello()")
#sayHello("say", "hello", "aselfrgument", "list")
#print("After first sayHello() call")

#print("After second sayHello() call")


@decorator_without_arguments
def querry_set(*args):
    my_list = args
    print("my list is :",(my_list))

    con = lite.connect(my_list[0])
    #print(*args)
    
    time.sleep(2)
    cur = con.cursor()

    #cur.execute("""delete from 'items' where Row > 15946 and Row < 16284""")
    #cur.execute("""SELECT*FROM 'items' WHERE Row='2'""")
    cur.execute(my_list[1])
    
    
    try:
        db_data = cur.fetchone()
        print(db_data)
    except:
        pass
    con.commit()
    con.close()
    
    

print(datetime.datetime.now().strftime('%m/%d'))

def get_from_db(db_path):
    
    con = lite.connect(db_path)
    cur = con.cursor()
    cur.execute("""SELECT Row,ASIN,UPC,Store FROM items""")
    db_data = cur.fetchall()
    #con.commit()
    con.close()
    print(db_data)
    return db_data

def delete_funct(db_path):

    
    path = 'delete.csv'
    with open(path,newline='',encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader) #first line is header
        edit_data = [row for row in reader] #reads the remaining data

    con = lite.connect(db_path)
    cur = con.cursor()

    for x in edit_data:
        try:
            edit_Row = int(x[0].strip())#Row
            cur.execute(f"""delete from 'items' where Row = {edit_Row}""")
        
        except:
            pass

    con.commit()
    con.close()




db_path = 'D:\\Googledrive\\Inventory\\Clean Inventory v13\\tests\\TEST.db'

#querry_set(db_path,q)
#print((decorator_without_arguments))

delete_funct(db_path)
get_from_db(db_path)