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
        'tune_type': None,
        'key_signature': None,
        'notation': ''.join(tune_lines)
    }

    primary_title = False

    tune_alt_title = {
        'book': book,
        'tune_id': None,
        'alt_title': []
    }
    
    for line in tune_lines:
        start_i = 2
        if line.startswith('X:'):
            value = line[start_i:].strip()
            tune['tune_id'] = value
            tune_alt_title['tune_id'] = value

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
                alt_titles.append(alt_title)
                current_tune_lines = [] # reset for each tune
            else:
                current_tune_lines += [line]
                in_tune = True
    
    # parse the last tune in the each file
    tune_result = parse_tune(book, current_tune_lines)
    tunes.append(tune_result[0])
    alt_titles.append(tune_result[1])
    
    return



# Find all ABC files
folder_path = Path("abc_books/")
files = [f for f in folder_path.rglob("*.abc") if f.is_file()]
files = sorted(files) # Sort alphabetically


# Add tune dicts into tunes list
tunes = []
alt_titles = []
for file in files:
    lines = load_abc_file(file)
    book = file.parent.name
    parse_all_tunes(book, lines)


# Create DataFrame
df = pd.DataFrame(tunes)
df2 = pd.DataFrame(alt_titles)

# Export to csv
df.to_csv('src/parsed_tunes.csv', index=False)
df2.to_csv('src/parsed_alt_titles.csv', index=False)
