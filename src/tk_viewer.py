import pandas as pd
import mysql.connector
import tkinter as tk
from tkinter import ttk

def connect_mysql():
    """connect to MySQL"""
    conn = mysql.connector.connect(host="localhost", user="root", database="abc_music")
    return conn


def load_tunes_from_db(table_name):
    """Load all tunes from MySQL into DataFrame"""
    conn = connect_mysql()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    
    conn.close()
    return df


def get_statistics(df):
    """Return summary statistics"""
    stats = {
        'total_tunes': len(df),
        'books': df['book'].nunique(),
        'tune_types': df['tune_type'].value_counts().to_dict(),
        'keys': df['key_signature'].value_counts().to_dict()
    }
    return stats

def get_all_tunes():
    """Get all tunes"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT book, title, tune_type, key_signature FROM tunes")
    result = cursor.fetchall()
    return result


def get_tunes_by_book(book_num):
    """Get all tunes from a specific book"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT book, title, tune_type, key_signature FROM tunes WHERE book = '{book_num}'")
    result = cursor.fetchall()
    return result


def get_tunes_by_type(tune_type):
    """Get all tunes of a specific type"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT book, title, tune_type, key_signature FROM tunes WHERE tune = '{tune_type}'")
    result = cursor.fetchall()
    return result


def get_tunes_by_book_type(book_num, tune_type):
    """Get all tunes of a specific type"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT book, title, tune_type, key_signature FROM tunes WHERE book = '{book_num}' and tune_type = '{tune_type}'")
    result = cursor.fetchall()
    return result


def search_tunes(df, search_term):
    """Search tunes by title (case insensitive)"""
    return df[df['title'].str.contains(search_term, case=False)]


def selected_tune_info(id):
    pass


# load table
conn = connect_mysql()
df = load_tunes_from_db('tunes')
stats = get_statistics(df)

root = tk.Tk()
root.title('ABC Music Explorer')
root.geometry("500x500")


title = tk.Label(root, 
                 text="Welcome",
                 font=("Arial", 16, "bold"),
                 wraplength=350,
                 justify="center")
title.pack()

filter_frame = tk.Frame(root, bg='grey', height=100, width=325)
filter_frame.pack()

# filters
bk_filter = tk.Label(filter_frame, 
                     text="Filter by Book:").grid(row=0, column=0)
type_filter = tk.Label(filter_frame, 
                     text="Filter by Type:").grid(row=1, column=0)


# dropdown
bk_opt = []
for i in range(stats['books']):
    bk_opt.append(i+1)

type_opt = []
for key in stats['tune_types'].keys():
    type_opt.append(key)

bk_combo = ttk.Combobox(filter_frame, values=bk_opt, state="readonly")
bk_combo.grid(row=0, column=1)
type_combo = ttk.Combobox(filter_frame, values=type_opt, state="readonly")
type_combo.grid(row=1, column=1)

def clear_tree():
    for item in tree.get_children():
        tree.delete(item)

def on_filter():
    selected_bk = bk_combo.get()
    selected_type = type_combo.get()
    label.config(text=f"Entered: Book {selected_bk}, Type {selected_type}")

    if selected_bk and selected_type:
        tunes = get_tunes_by_book_type(selected_bk, selected_type)
    elif selected_bk:
        tunes = get_tunes_by_book(selected_bk)
    else:
        tunes = get_tunes_by_type(selected_type)
    clear_tree() #reset
    if tunes:
        for row in tunes:
            tree.insert('', tk.END, values=row)
    else:
        tree.insert('', tk.END, values=('No tunes found !'))
    tunes_num.config(text=f"Number of tunes: {len(tunes)}")


submit = tk.Button(root, text="Search", command=on_filter)
submit.pack()
label = tk.Label(root)
label.pack()


# all tunes
cols = ("Book", "Title", "Tune", "Key")
tree = ttk.Treeview(root, columns=cols, show='headings', height=15)
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tunes = get_all_tunes()
for row in tunes:
        tree.insert('', tk.END, values=row)
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack()
scrollbar.pack()

tunes_num = tk.Label(root, text=f"Number of tunes: {len(tunes)}")
tunes_num.pack()

clear_btn = tk.Button(root, text="Clear table", command=clear_tree)
clear_btn.pack()

root.mainloop()