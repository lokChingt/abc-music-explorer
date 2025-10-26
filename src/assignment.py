import pandas as pd
import mysql.connector
from pathlib import Path


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
        'alt_title': None,
        'tune_type': None,
        'key_signature': None,
        'notation': ''.join(tune_lines)
    }

    primary_title = False
    alt_title = False
    
    for line in tune_lines:
        line = line.strip()
        start_i = 2
        if line.startswith('X:'):
            tune['tune_id'] = line[start_i:]

        elif line.startswith('T:'):
            if primary_title == False: # first title
                tune['title'] = line[start_i:]
                primary_title = True
            elif alt_title == False:   # alt title
                tune['alt_title'] = (line[start_i:])
                alt_title = True

        elif line.startswith('R:'):
            tune['tune_type'] = line[start_i:]

        elif line.startswith('K:'):
            tune['key_signature'] = line[start_i:]

    return tune


def parse_all_tunes(book, lines):
    """Parse all tunes from lines"""
    current_tune_lines = []
    in_tune = False
    
    for line in lines:
        """Implement tune boundary detection"""
        if line.startswith("X:") or in_tune == True: # tune starts
            if line.strip() == "": # tune ends
                in_tune = False
                """Call parse_tune() for each complete tune"""
                tunes.append(parse_tune(book, current_tune_lines))
                current_tune_lines = [] # reset for each tune
            else:
                current_tune_lines += [line]
                in_tune = True
            
    return



# Find all ABC files
folder_path = Path("abc_books/")
files = [f for f in folder_path.rglob("*.abc") if f.is_file()]
files = sorted(files) # Sort alphaalphabetically


# Add tune dicts into tunes list
tunes = []
for file in files:
    lines = load_abc_file(file)
    book = file.parent.name
    parse_all_tunes(book, lines)


# Create DataFrame
df = pd.DataFrame(tunes)

# Export to csv
df.to_csv('src/parsed_tunes.csv', index=False)
