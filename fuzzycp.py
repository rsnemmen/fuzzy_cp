#!/usr/bin/env python3

# Fuzzy name matching
from rapidfuzz import process, fuzz
# Parsing command-line arguments
import argparse
# File search, regex
import glob, os
import re
from pathlib import Path
# Terminal colors
from termcolor import colored
# Human-readable file sizes
import humanize
# Progress bar
from tqdm.auto import tqdm

import sys, shutil




def file_matching(names, filenames):
    """
    Finds the best matching filename for each name using fuzzy string matching.

    Args:
        names (list): A list of names to match.
        filenames (list): A list of filenames to be matched against.

    Returns:
        dict: A dictionary where keys are the original names and values are 
              tuples of (best_matching_filename, similarity_score).
    """
    matches = {}
    for name in names:
        # The extractOne method finds the best match for 'name' from the 'filenames' list.
        # It returns a tuple containing the match, the score, and the index.
        # We are interested in the match and the score.
        best_match = process.extractOne(name, filenames, scorer=fuzz.QRatio)
        
        # The result can be None if the list of choices is empty.
        if best_match:
            matches[name] = (best_match[0], best_match[1])
            
    return matches



def read_names(filepath):
    """
    Reads names from a text file, with one name per line.

    Args:
        filepath (str): The path to the text file.

    Returns:
        list: A list of names with leading/trailing whitespace removed.
              Returns an empty list if the file cannot be found.
    """
    try:
        with open(filepath, 'r') as file:
            # Use a list comprehension for a concise and readable solution.
            # line.strip() removes leading/trailing whitespace, including the newline character.
            names = [line.strip() for line in file]
        return names
    except FileNotFoundError:
        print(f"Error: The file at {filepath} was not found.")
        return []


def get_args():
    '''
    Get command-line arguments
    '''
    p = argparse.ArgumentParser(prog="fuzzycp",
        description="File operations with fuzzy name matching.")

    # Positional argument
    p.add_argument("names",
                   help="path to file containing names to be matched")

    # Optional flags
    p.add_argument("-s", "--space",
                   action="store_true",
                   help="displays disk space occupied by matching files"
                   )
    p.add_argument("-c", "--copy",               
        metavar="PATH",             
        type=Path,                  
        help="copy the file(s) to this destination path"
        )
    p.add_argument("-m", "--move",               
        metavar="PATH",             
        type=Path,                  
        help="move matching files to a given dir (not implemented yet"
        )
    p.add_argument("-o", "--output",               
        metavar="PATH",             
        nargs="?",
        const="-",              
        help="write list of matching files to file, or stdout if no file is provided"
        )

    return p.parse_args()


def preprocessing(files):
    BRACKETED = re.compile(r"\s*[\[\(\{][^\]\)\}]*[\]\)\}]\s*")
    cleanedup=[]

    for f in files:
        s = Path(f).stem          # remove extension
        # turn _ into spaces
        s = s.replace("_", " ").replace("-", " ")
        without = BRACKETED.sub(" ", s)        # yank the bracketed bits
        s=" ".join(without.split())          # normalise whitespace

        cleanedup.append(s.strip())

    return cleanedup





# Parsing and preprocessing
# --------------------------------------------------------------------------------
# Get command-line arguments
args = get_args()
# Where to write list of matching files if '-o' was specified
if args.output == "-":
    out = sys.stdout
elif args.output is not None:
    out = open(Path(args.output), "w")

# Interrupts execution if non-implemented options are provided
#if args.move:
#    print("This option is not yet implemented. Aborting.", file=sys.stderr)
#    sys.exit(1)

# Get the list of names to be matched against filenames
names = read_names(args.names)

# Get the list of all files in the current directory 
candidates = glob.glob('*') # non‐hidden
files = [f for f in candidates if os.path.isfile(f)]
# Preprocess filenames
files_cleaned=preprocessing(files)
# Build a map from cleaned up filenames ➜ original file name
map_orig = dict(zip(files_cleaned, files))

# Fuzzy matching function
# --------------------------------------------------------------------------------
best_matches = file_matching(names, files_cleaned)

# Print best-matches and other info
# --------------------------------------------------------------------------------
# Total file size
total=0

# Process the best-matches, first pass
if not args.output: 
    print(colored("Name","green")+"                 "+colored("Best-match","blue")+"                 "+colored("Score","red"))
for name, (cleaned_fn, score) in best_matches.items():
    original_fn = map_orig[cleaned_fn] # lookup
    if args.output:
        print(original_fn, file=out)        
    else:
        print(colored(name,"green"),"|", colored(original_fn,"blue"),colored(round(score), "red"))
    
    if args.space:
        total += os.path.getsize(original_fn)  # bytes

if args.space and not args.output:
    print()
    print("Disk space =", humanize.naturalsize(total, binary=True))     # e.g. 358.6 MB

if args.output:
    if out is not sys.stdout:
        out.close()

# File operations (disk writing)
# --------------------------------------------------------------------------------
# Asks for user confirmation before writing to disk
if args.copy and args.move:
    print("Please specify move or copy, not both.")
    sys.exit(1)
elif args.copy:
    user_input = input("\n Proceed copying the files marked in blue? (Y/N): ")
    print()
    description="Copying files"
    # Destination dir
    dst=Path(args.copy)
elif args.move:
    user_input = input("\n Proceed moving the files marked in blue? (Y/N): ")
    print()
    description="Moving files"
    dst=Path(args.move)

if args.copy or args.move:
    # Convert the input to lowercase for case-insensitive comparison
    if user_input.lower() == 'y':
        # Process the best-matches, second pass
        for name, (cleaned_fn, score) in tqdm( # progress bar
            best_matches.items(),
            total=len(best_matches),
            desc=description
            ):
            original_fn = map_orig[cleaned_fn] # lookup

            # Create if missing
            dst.mkdir(parents=True, exist_ok=True)
            # Source
            src=Path(original_fn)
            target=dst/src.name
            if args.copy: shutil.copy2(src, target) # Copy operation
            if args.move: shutil.move(src,target) # move operation
    else:
        print("Operation cancelled.")


