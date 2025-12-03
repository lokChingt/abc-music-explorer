import pandas as pd
import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# All functions
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


# filter
def get_tunes_by_book(book_num):
    """Get all tunes from a specific book"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE book = '{book_num}'")
    result = cursor.fetchall()
    return result


def get_tunes_by_type(tune_type):
    """Get all tunes of a specific type"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE tune_type ='{tune_type}'")
    result = cursor.fetchall()
    return result


def get_tunes_by_book_type(book_num, tune_type):
    """Get all tunes of a specific type"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE book = '{book_num}' and tune_type = '{tune_type}'")
    result = cursor.fetchall()
    return result


# search
def search(search_word):
    """Search tunes with search word"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE title LIKE '%{search_word}%'")
    result = cursor.fetchall()
    return result

def search_filter_bk_type(search_word, bk_num, tune_type):
    """Search tunes with search word & by book number and tune_type"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE title LIKE '%{search_word}%' and book = '{bk_num}' and tune_type = '{tune_type}'")
    result = cursor.fetchall()
    return result

def search_filter_bk(search_word, bk_num):
    """Search tunes with search word & by book number"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE title LIKE '%{search_word}%' and book = '{bk_num}'")
    result = cursor.fetchall()
    return result

def search_filter_type(search_word, tune_type):
    """Search tunes with search word & by tune_type"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE title LIKE '%{search_word}%' and tune_type = '{tune_type}'")
    result = cursor.fetchall()
    return result


def clear_tree(tree_name):
    """Clear all tunes in Treeview"""
    for item in tree_name.get_children():
        tree_name.delete(item)

def search_filter():
    """Search by the user input"""
    # get input
    search_word = search_bar.get()
    selected_bk = bk_combo.get()
    selected_type = type_combo.get()
    query_msg.config(text=f"Entered: Search: {search_word}, Book: {selected_bk}, Type: {selected_type}")

    # get the search results
    if search_word:
        if selected_bk and selected_type:
            tunes = search_filter_bk_type(search_word, selected_bk, selected_type)
        elif selected_bk:
            tunes = search_filter_bk(search_word, selected_bk)
        elif selected_type:
            tunes = search_filter_type(search_word, selected_type)
        else:
            tunes = search(search_word)
    else: # no search word
        if selected_bk and selected_type:
            tunes = get_tunes_by_book_type(selected_bk, selected_type)
        elif selected_bk:
            tunes = get_tunes_by_book(selected_bk)
        elif selected_type:
            tunes = get_tunes_by_type(selected_type)
        else: # no input
            # show all tunes
            tunes = get_all_tunes()

    clear_tree(tree) #reset

    # check if tune found
    if tunes:
        # display tunes
        for row in tunes:
            tree.insert('', tk.END, values=row)
    else:
        # show tune not found
        tree.insert('', tk.END, values=('No tunes found !'))
    tunes_num.config(text=f"Number of tunes: {len(tunes)}")


def clear_q():
    """Clear all search inputs"""
    bk_combo.set('')
    type_combo.set('')
    search_bar.delete(0, "end")


def reset_msg(msg):
    """Clear message label"""
    msg.config(text="")


def deselect_tree(event, tree):
    """Remove selected row in home treeview"""
    if event.widget not in (tree,):
        selections = tree.selection()
        for row in selections:
            tree.selection_remove(row)


def add_tune():
    """Add selected tune(s) into playlist"""
    selections = tree.selection()

    # check if any tune selected
    if not selections:
        messagebox.showwarning("Warning!", "Please select a tune")
        return
    else:
        # list of added tune id
        added_tune_id = []

        # get all tune_id in playlist
        playlist_id = {playlist.item(r, "values")[0] for r in playlist.get_children()}

        # iterate over selected tune
        for row in selections:
            # get id of selected tune
            vals = tree.item(row, "values")
            id = vals[0]

            # check if tune already added
            if id in playlist_id:
                added_tune_id.append(id)
            else:
                # insert tune into playlist if not added
                cursor = conn.cursor()
                cursor.execute(f"SELECT id, book, title, tune_type FROM tunes WHERE id = {id}")
                result = cursor.fetchall()
                playlist.insert("", tk.END, values=result[0])

        # check if any added tune
        if added_tune_id:
            messagebox.showwarning("Warning!", f"Tune ID {added_tune_id} already added. Others are added.")
            return
            
        # added message
        add_msg.config(text="Added successfully")
        root.after(1000, lambda: reset_msg(add_msg))


def remove_tune():
    """Remove selected tune(s) from playlist"""
    selections = playlist.selection()

    # check if tune selected
    if not selections:
        messagebox.showwarning("Warning!", "Please select a tune")
    else:
        # remove selected tune(s)
        for row in selections:
            playlist.delete(row)

        # removed message
        remove_msg.config(text="Removed successfully")
        root.after(1000, lambda: reset_msg(remove_msg))


def save_playlist():
    """Save playlist as CSV file"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=(("Text files", "*.csv"), ("All files", "*.*"))
    )

    # check if file path chose
    if file_path:
        with open(file_path, 'w') as file:
            csvwriter = csv.writer(file, delimiter=',')

            # write column headers
            csvwriter.writerow(cols)

            # write playlist tunes into CSV file
            for row_id in playlist.get_children():
                row = tree.item(row_id, "values")
                csvwriter.writerow(row)


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
notebook.pack(fill="both", expand=True)

# tabs
tab1 = tk.Frame(notebook)
tab2 = tk.Frame(notebook)
tab3 = tk.Frame(notebook)

notebook.add(tab1, text="Home")
notebook.add(tab2, text="Playlist")
notebook.add(tab3, text="Statistics")


# === tab1: home page ===
# home title
title = tk.Label(tab1,
                 text="ABC Music Explorer",
                 font=("Arial", 16, "bold"),
                 wraplength=350,
                 justify="center")
title.pack()

# button to end program
exit_btn = tk.Button(tab1, text="Exit", command=root.destroy)
exit_btn.pack()

# frame to store inputs in grid
input_frame = tk.Frame(tab1)
input_frame.pack()

# search label
search_label = tk.Label(input_frame, text="Search Title:", justify="left")
search_label.grid(row=0, column=0)

# input search word
search_bar = tk.Entry(input_frame)
search_bar.grid(row=0, column=1)


# filters
# by book number
bk_filter = tk.Label(input_frame, text="Filter by Book:", justify="left")
bk_filter.grid(row=1, column=0)

# by tune type
type_filter = tk.Label(input_frame,  text="Filter by Type:", justify="left")
type_filter.grid(row=2, column=0)


# search dropdown
# book dropdown
bk_opt = []
for i in range(stats['books']):
    bk_opt.append(i+1)

bk_combo = ttk.Combobox(input_frame, values=bk_opt, state="readonly")
bk_combo.grid(row=1, column=1)

# tune type dropdown
type_opt = []
for key in stats['tune_types'].keys():
    type_opt.append(key)
type_opt = sorted(type_opt) # sort alphabetically

type_combo = ttk.Combobox(input_frame, values=type_opt, state="readonly")
type_combo.grid(row=2, column=1)


# button to clear search queries
clear_q_btn = tk.Button(input_frame, text="Clear", command=clear_q)
clear_q_btn.grid(row=1, column=2)

# button to search tunes
search_btn = tk.Button(input_frame, text="Search", command=search_filter)
search_btn.grid(row=2, column=2)

# display user input
query_msg = tk.Label(tab1)
query_msg.pack()


# home treeview
tunes = get_all_tunes()
cols = ("ID", "Book", "Title", "Type")

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

# insert tunes into treeview
for row in tunes:
        tree.insert('', tk.END, values=row)
tree.pack()

# message when tune added to playlist
add_msg = tk.Label(tab1)
add_msg.pack()

# button to add tune to playlist
add_btn = tk.Button(tab1, text="Add to Playlist", command=add_tune)
add_btn.pack()

# display the number of tunes
tunes_num = tk.Label(tab1, text=f"Number of tunes: {len(tunes)}")
tunes_num.pack()

# deselect tune when click outside the treeview
tab1.bind("<Button-1>", lambda event: deselect_tree(event, tree))



# === tab2: playlist page ===
# playlist title
playlist_title = tk.Label(tab2, 
                          text="Tune Playlist",
                          font=("Arial", 16, "bold"),
                          wraplength=350,
                          justify="center")
playlist_title.pack()

# playlist treeview
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


# playlist tab labels & buttons
remove_msg = tk.Label(tab2)
remove_msg.pack()

remove_btn = tk.Button(tab2, text="Remove", command=remove_tune)
remove_btn.pack()

clear_btn = tk.Button(tab2, text="Clear", command=lambda: clear_tree(playlist))
clear_btn.pack()

save_btn = tk.Button(tab2, text="Save as CSV", command=save_playlist)
save_btn.pack()

# deselect tune when click outside the playlist
tab2.bind("<Button-1>", lambda event: deselect_tree(event, playlist))



# === tab3: statistics page ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 5))

# top 5 most tune_type [pie chart]
type_counts = df['tune_type'].value_counts().head(5)
sorted_type = type_counts.sort_values()

ax1.pie(sorted_type.values, labels=sorted_type.index, textprops={'fontsize': 5}, autopct='%1.1f%%')
ax1.set_title('Tune Type Distribution', fontsize=7)


# tune with the most tune_alt_titles [bar chart]
alt_title_count = joined_df.groupby('title')['alt_title'].count()
sorted_alt_title = alt_title_count.sort_values(ascending=False).head(5)

bar_chart = ax2.bar(sorted_alt_title.index, sorted_alt_title.values)
ax2.bar_label(bar_chart, fontsize=5, padding=3)
ax2.set_title('Top 5 Tune with the Most Alternative Titles', fontsize=7)
ax2.set_xlabel('Tune', fontsize=5)
ax2.set_ylabel('Number of Alternative Titles', fontsize=5)
ax2.tick_params(axis='x', rotation=15, labelsize=5)
ax2.tick_params(axis='y', labelsize=5)


# embed plots into tkinter
fig.tight_layout()
canvas = FigureCanvasTkAgg(fig, tab3)
canvas.draw()
canvas.get_tk_widget().pack()


root.mainloop()