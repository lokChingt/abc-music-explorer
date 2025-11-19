"""
Data Centric Programming Assignment 2025
Name: Lok Ching Tam
Student Number: C24385243
Course: TU850/2
"""

import pandas as pd
import mysql.connector
from pathlib import Path
import json

def load_abc_file(file_path):
    """Load ABC file into list of lines"""
    with open(file_path, 'r', encoding='latin-1') as f:
        lines = f.readlines()
        
    return lines


def parse_tune(book, tune_lines):
    """Parse a single tune from lines"""
    tune = {
        'book': book,
        'tune_id': None,
        'title': None,
        'tune_type': None,
        'key_signature': None,
        'notation': ''.join(tune_lines)
    }

    tune_alt_title = {
        'alt_title': []
    }

    primary_title = False
    
    """add values into tune & tune_alt_title dict"""
    for line in tune_lines:
        start_i = 2
        if line.startswith('X:'):
            tune['tune_id'] = line[start_i:].strip()

        elif line.startswith('T:'):
            if primary_title == False: # first title
                tune['title'] = line[start_i:].strip()
                primary_title = True
            else:                      # alt title
                tune_alt_title['alt_title'].append(line[start_i:].strip())

        elif line.startswith('R:'):
            tune['tune_type'] = line[start_i:].strip()

        elif line.startswith('K:'):
            tune['key_signature'] = line[start_i:].strip()
            return tune, tune_alt_title

    return tune, tune_alt_title


def parse_all_tunes(book, lines):
    """Parse all tunes from lines"""
    current_tune_lines = []
    in_tune = False
    
    for line in lines:
        """Implement tune boundary detection"""
        if line.startswith("X:") or in_tune == True: # tune starts
            if line.strip() == "":                   # tune ends
                in_tune = False
                """Call parse_tune() for each complete tune"""
                tune, alt_title = parse_tune(book, current_tune_lines)
                tunes.append(tune)
                tune_alt_title.append(alt_title)
                current_tune_lines = [] # reset for each tune
            else:
                current_tune_lines += [line]
                in_tune = True
    
    # parse the last tune in the each file
    if current_tune_lines:
        tune, alt_title = parse_tune(book, current_tune_lines)
        tunes.append(tune)
        tune_alt_title.append(alt_title)


def connect_mysql():
    """connect to MySQL"""
    config_path = Path(__file__).parent.parent / "config.json"

    with open(config_path) as f:
        config = json.load(f)

    conn = mysql.connector.connect(
        host="localhost",
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )
    return conn


def db_insert_tunes():
    """insert data into tunes"""
    cols = tunes[0].keys() 

    placeholders = ",".join(["%s"] * len(cols))
    cols_str = ",".join(cols)

    query = f"INSERT INTO tunes ({cols_str}) VALUES ({placeholders})"

    # convert list of dicts to list of tuples
    vals = [tuple(tune.values()) for tune in tunes]

    # insert data
    cursor.executemany(query, vals)
    conn.commit()


def db_insert_alt_titles():
    """insert data into tune_alt_titles"""
    vals = []

    for tune_id, row in enumerate(tune_alt_title, 1):
        alt_titles = row['alt_title']
        if alt_titles:
            for alt_title in alt_titles:
                vals.append((tune_id, alt_title))
        else:  # no alt_titles
            vals.append((tune_id, None))

    query = "INSERT INTO tune_alt_titles (tune_id, alt_title) VALUES (%s, %s)"
    cursor.executemany(query, vals)
    conn.commit()



# find all abc files
folder_path = Path("abc_books/")
files = [f for f in folder_path.rglob("*.abc") if f.is_file()]
files = sorted(files) # Sort alphabetically

# parse all tunes and alt_titles
tunes = []
tune_alt_title = []
for file in files:
    lines = load_abc_file(file)
    book = file.parent.name
    parse_all_tunes(book, lines)

# connect to database
conn = connect_mysql()
cursor = conn.cursor()

# insert data into db
db_insert_tunes()
db_insert_alt_titles()

# close db connection
conn.close()