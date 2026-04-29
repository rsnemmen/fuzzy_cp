from rapidfuzz import process, fuzz
import re
from pathlib import Path


def file_matching(names, filenames):
    """
    Finds the best matching filename for each name using fuzzy string matching.

    Args:
        names (list): A list of names to match.
        filenames (list): Cleaned filenames to match against (use preprocessing() first).

    Returns:
        dict: Keys are the original names; values are (best_matching_cleaned_filename, score).
    """
    matches = {}
    for name in names:
        best_match = process.extractOne(name, filenames, scorer=fuzz.WRatio)
        if best_match:
            matches[name] = (best_match[0], best_match[1])
    return matches


def read_names(filepath):
    """
    Reads names from a text file, one name per line.

    Returns:
        list: Names with leading/trailing whitespace removed.
              Returns an empty list if the file cannot be found.
    """
    try:
        with open(filepath, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file at {filepath} was not found.")
        return []


def preprocessing(files):
    """
    Cleans a list of filenames for fuzzy matching.

    Strips extension, replaces _ and - with spaces, removes bracketed content
    (e.g. (U), [!], {extra}), and normalises whitespace.
    """
    BRACKETED = re.compile(r"\s*[\[\(\{][^\]\)\}]*[\]\)\}]\s*")
    cleaned = []
    for f in files:
        s = Path(f).stem
        s = s.replace("_", " ").replace("-", " ")
        s = BRACKETED.sub(" ", s)
        s = " ".join(s.split())
        cleaned.append(s.strip())
    return cleaned


def _threshold_type(value):
    ivalue = int(value)
    if not 0 <= ivalue <= 100:
        raise ValueError(f"threshold must be between 0 and 100, got {ivalue}")
    return ivalue
