import pandas as pd
import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def db_connect():
    """connect to MySQL"""
    conn = mysql.connector.connect(host="localhost", user="root", database="abc_music")
    return conn


def load_table_from_db(table_name):
    """Load all tunes from MySQL into DataFrame"""
    conn = db_connect()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    
    conn.close()
    return df

def join_tables():
    """Join two tables"""
    conn = db_connect()
    query = f"SELECT * FROM tunes JOIN tune_alt_titles ON tunes.id = tune_alt_titles.tune_id"
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
    cursor.execute("SELECT id, book, title, tune_type FROM tunes")
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
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE tune_type LIKE'%{tune_type}%'")
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


# load table
conn = db_connect()
df = load_table_from_db('tunes')
df2 = load_table_from_db('tune_alt_titles')
joined_df = join_tables()
stats = get_statistics(df)

# gui
root = tk.Tk()
root.title('ABC Music Explorer')
root.geometry("500x600")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# tabs
tab1 = tk.Frame(notebook)
tab2 = tk.Frame(notebook)
tab3 = tk.Frame(notebook)

notebook.add(tab1, text="Home")
notebook.add(tab2, text="Playlist")
notebook.add(tab3, text="Statistics")

title = tk.Label(tab1,
                 text="ABC Music Explorer",
                 font=("Arial", 16, "bold"),
                 wraplength=350,
                 justify="center")
title.pack()

exit_btn = tk.Button(tab1, text="Exit", command=root.destroy)
exit_btn.pack()

input_frame = tk.Frame(tab1)
input_frame.pack()

# search
def search(search_word):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE title LIKE '%{search_word}%'")
    result = cursor.fetchall()
    return result

def search_filter_bk_type(search_word, bk_num, tune_type):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE title LIKE '%{search_word}%' and book = '{bk_num}' and tune_type LIKE '%{tune_type}%'")
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


# search dropdown
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

def clear_tree(tree_name):
    """Clear all tunes in Treeview"""
    for item in tree_name.get_children():
        tree_name.delete(item)

def search_filter():
    search_word = search_bar.get()
    selected_bk = bk_combo.get()
    selected_type = type_combo.get()
    query_msg.config(text=f"Entered: Search: {search_word}, Book: {selected_bk}, Type: {selected_type}")

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

    clear_tree(tree) #reset
    if tunes:
        for row in tunes:
            tree.insert('', tk.END, values=row)
    else:
        tree.insert('', tk.END, values=('No tunes found !'))
    tunes_num.config(text=f"Number of tunes: {len(tunes)}")


def clear_q():
    bk_combo.set('')
    type_combo.set('')
    search_bar.delete(0, "end")

def reset_msg(msg):
    msg.config(text="")

def deselect_home_tune(event):
    if event.widget not in (tree, add_btn):
        selections = tree.selection()
        for row in selections:
            tree.selection_remove(row)

def deselect_playlist_tune(event):
    if event.widget not in (playlist, remove_btn):
        selections = playlist.selection()
        for row in selections:
            playlist.selection_remove(row)

tab1.bind("<Button-1>", deselect_home_tune)
tab2.bind("<Button-1>", deselect_playlist_tune)

cols = ("ID", "Book", "Title", "Type")

# playlist
playlist_title = tk.Label(tab2, 
                          text="Tune Playlist",
                          font=("Arial", 16, "bold"),
                          wraplength=350,
                          justify="center")
playlist_title.pack()

playlist = ttk.Treeview(tab2, columns=cols, show='headings', height=20, selectmode="extended")
for col in cols:
    playlist.heading(col, text=col)
    # have diff col width for diff col
    if col == "Title":
        col_width = 220
    elif col == "Type": 
        col_width = 80
    else:
        col_width = 50
    playlist.column(col, width=col_width)
playlist.pack()

def add_tune():
    selections = tree.selection()
    if not selections:
        messagebox.showwarning("Warning!", "Please select a tune")
        return
    else:
        for row in selections:
            vals = tree.item(row, "values")
            id = vals[0]

            # get all tune_id in playlist
            playlist_id = {playlist.item(r, "values")[0] for r in playlist.get_children()}

            # check if tune already added
            if id not in playlist_id:
                cursor = conn.cursor()
                cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE id = {id}")
            else:
                messagebox.showwarning("Warning!", "Tune already added")
                return

            result = cursor.fetchall()
            for tune in result:
                playlist.insert("", tk.END, values=tune)

        add_msg.config(text="Added successfully")
        root.after(1000, lambda: reset_msg(add_msg))

def remove_tune():
    selections = playlist.selection()
    if not selections:
        messagebox.showwarning("Warning!", "Please select a tune")
    else:
        for row in selections:
            playlist.delete(row)

        remove_msg.config(text="Removed successfully")
        root.after(1000, lambda: reset_msg(remove_msg))

def save_playlist():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=(("Text files", "*.csv"), ("All files", "*.*"))
    )
    if file_path:
        with open(file_path, 'w') as file:
            csvwriter = csv.writer(file, delimiter=',')
            csvwriter.writerow(cols)
            for row_id in playlist.get_children():
                row = tree.item(row_id, "values")
                csvwriter.writerow(row)
            


remove_msg = tk.Label(tab2)
remove_msg.pack()

remove_btn = tk.Button(tab2, text="Remove", command=remove_tune)
remove_btn.pack()

clear_btn = tk.Button(tab2, text="Clear", command=lambda: clear_tree(playlist))
clear_btn.pack()

save_btn = tk.Button(tab2, text="Save as CSV", command=save_playlist)
save_btn.pack()

clear_q_btn = tk.Button(input_frame, text="Clear", command=clear_q)
clear_q_btn.grid(row=1, column=2)

submit = tk.Button(input_frame, text="Search", command=search_filter)
submit.grid(row=2, column=2)

query_msg = tk.Label(tab1)
query_msg.pack()


# all tunes
tunes = get_all_tunes()

tree = ttk.Treeview(tab1, columns=cols, show='headings', height=15, selectmode="extended")
for col in cols:
    tree.heading(col, text=col)
    # have diff col width for diff col
    if col == "Title":
        col_width = 220
    elif col == "Type": 
        col_width = 80
    else:
        col_width = 50
    tree.column(col, width=col_width)

for row in tunes:
        tree.insert('', tk.END, values=row)
tree.pack()

add_msg = tk.Label(tab1)
add_msg.pack()

add_btn = tk.Button(tab1, text="Add to Playlist", command=add_tune)
add_btn.pack()

tunes_num = tk.Label(tab1, text=f"Number of tunes: {len(tunes)}")
tunes_num.pack()


# plots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 5))

# top 5 most tune_type [pie chart]
type_counts = df['tune_type'].value_counts().head(5)
sorted_type = type_counts.sort_values()

ax1.pie(sorted_type.values, labels=sorted_type.index, textprops={'fontsize': 5}, autopct='%1.1f%%')
ax1.set_title('Tune Type Distribution', fontsize=7)


# tune with the most tune_alt_titles [bar chart]
alt_title_count = joined_df.groupby('title')['alt_title'].count()
sorted_alt_title = alt_title_count.sort_values(ascending=False).head(5)

ax2.bar(sorted_alt_title.index, sorted_alt_title.values)
ax2.set_title('Top 5 Tune with the Most Alternative Titles', fontsize=7)
ax2.set_xlabel('Tune', fontsize=5)
ax2.set_ylabel('Number of Alternative Titles', fontsize=5)
ax2.tick_params(axis='x', rotation=15, labelsize=5)
ax2.tick_params(axis='y', labelsize=5)

# embed into tkinter
fig.tight_layout()
canvas = FigureCanvasTkAgg(fig, tab3)
canvas.draw()
canvas.get_tk_widget().pack()

root.mainloop()