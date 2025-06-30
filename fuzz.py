# We will use thefuzz in this example, but the syntax for rapidfuzz is very similar.
from thefuzz import process

def find_best_file_matches(names, filenames):
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