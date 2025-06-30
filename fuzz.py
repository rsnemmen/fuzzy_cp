#!/usr/bin/env python3

# Fuzzy name matching
from thefuzz import process
# Parsing command-line arguments
import argparse
# File search
import glob, os



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
        best_match = process.extractOne(name, filenames)
        
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
    p = argparse.ArgumentParser()

    # Positional argument
    p.add_argument("names",
                   help="path to file containing names to be matched")

    ''''
    # Optional flags
    p.add_argument("-v", "--verbose",
                   action="store_true",
                   help="enable verbose output")
    # Typed option with default
    p.add_argument("-n", "--number",
                   type=int,
                   default=1,
                   help="an integer repeat count")
    '''
    return p.parse_args()


# Get command-line arguments
args = get_args()

# Get the list of names to be matched against filenames
names = read_names(args.names)

# Get the list of all files in the current directory 
candidates = glob.glob('*') # non‐hidden
files = [f for f in candidates if os.path.isfile(f)]

names_list = read_names(file_path)


# Print the resulting list to verify
if list_of_names:
    print("Successfully read the following names from the file:")
    print(list_of_names)



# --- Example Usage ---

# List 1: The names you want to find files for.
names_to_match = [
    "John Smith",
    "Jane Doe",
    "Peter Jones PhD",
    "The Big Company Inc"
]

# List 2: The list of filenames in a directory.
file_list = [
    "jane_doe_resume_2023.pdf",
    "photo_of_john_smith.jpg",
    "the_big_co.txt",
    "dr_p_jones_cv.docx",
    "random_file.txt"
]

# Run the matching function
best_matches = find_best_file_matches(names_to_match, file_list)

# Print the results
for name, match_info in best_matches.items():
    filename, score = match_info
    print(f"The best match for '{name}' is '{filename}' with a score of {score}.")
'''