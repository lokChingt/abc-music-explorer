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
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes")
    result = cursor.fetchall()
    return result


def get_tunes_by_book(book_num):
    """Get all tunes from a specific book"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE book = '{book_num}'")
    result = cursor.fetchall()
    return result


def get_tunes_by_type(tune_type):
    """Get all tunes of a specific type"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE tune_type = '{tune_type}'")
    result = cursor.fetchall()
    return result


def get_tunes_by_book_type(book_num, tune_type):
    """Get all tunes of a specific type"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE book = '{book_num}' and tune_type = '{tune_type}'")
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
                 text="ABC Music Explorer",
                 font=("Arial", 16, "bold"),
                 wraplength=350,
                 justify="center")
title.pack()


input_frame = tk.Frame(root)
input_frame.pack()

# search
def search(search_word):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE title LIKE '%{search_word}%'")
    result = cursor.fetchall()
    return result

def search_filter_bk_type(search_word, bk_num, tune_type):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE title LIKE '%{search_word}%' and book = '{bk_num}' and tune_type = '{tune_type}'")
    result = cursor.fetchall()
    return result

search_label = tk.Label(input_frame, text="Search Title:", justify="left")
search_label.grid(row=0, column=0)

search_bar = tk.Entry(input_frame)
search_bar.grid(row=0, column=1)

# filters
bk_filter = tk.Label(input_frame, text="Filter by Book:", justify="left")
bk_filter.grid(row=1, column=0)
type_filter = tk.Label(input_frame,  text="Filter by Type:", justify="left")
type_filter.grid(row=2, column=0)


# dropdown
bk_opt = []
for i in range(stats['books']):
    bk_opt.append(i+1)

type_opt = []
for key in stats['tune_types'].keys():
    type_opt.append(key)
type_opt = sorted(type_opt)

bk_combo = ttk.Combobox(input_frame, values=bk_opt, state="readonly")
bk_combo.grid(row=1, column=1)
type_combo = ttk.Combobox(input_frame, values=type_opt, state="readonly")
type_combo.grid(row=2, column=1)

def clear_tree():
    for item in tree.get_children():
        tree.delete(item)

def search_filter():
    search_word = search_bar.get()
    selected_bk = bk_combo.get()
    selected_type = type_combo.get()
    message.config(text=f"Entered: Search {search_word} Book {selected_bk}, Type {selected_type}")

    if search_word and selected_bk and selected_type:
        tunes = search_filter_bk_type(search_word, selected_bk, selected_type)
        pass
    elif selected_bk and selected_type:
        tunes = get_tunes_by_book_type(selected_bk, selected_type)
    elif search_word:
        tunes = search(search_word)
        pass
    elif selected_bk:
        tunes = get_tunes_by_book(selected_bk)
    elif selected_type:
        tunes = get_tunes_by_type(selected_type)
    else:
        tunes = get_all_tunes()

    clear_tree() #reset
    if tunes:
        for row in tunes:
            tree.insert('', tk.END, values=row)
    else:
        tree.insert('', tk.END, values=('No tunes found !'))
    tunes_num.config(text=f"Number of tunes: {len(tunes)}")


def clear():
    bk_combo.set('')
    type_combo.set('')
    search_bar.delete(0, "end")

clear = tk.Button(input_frame, text="Clear", command=clear)
clear.grid(row=1, column=2)

submit = tk.Button(input_frame, text="Search", command=search_filter)
submit.grid(row=2, column=2)

message = tk.Label(root)
message.pack()


# all tunes
cols = ("ID", "Book", "Title", "Tune")
tree = ttk.Treeview(root, columns=cols, show='headings', height=15)
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tunes = get_all_tunes()
for row in tunes:
        tree.insert('', tk.END, values=row)
tree.pack()

tunes_num = tk.Label(root, text=f"Number of tunes: {len(tunes)}")
tunes_num.pack()

clear_btn = tk.Button(root, text="Clear table", command=clear_tree)
clear_btn.pack()

root.mainloop()