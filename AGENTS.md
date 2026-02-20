# AGENTS.md

Guidelines for AI coding agents working in the `fuzzycp` repository.

## Project Overview

`fuzzycp` is a single-file Python CLI tool (`fuzzycp.py`) that performs copy/move file operations using fuzzy name matching. Given a text file of names (one per line), it finds the best-matching filenames in the current working directory and optionally copies or moves them.

## Build Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python fuzzycp.py names.txt              # print matches with scores
python fuzzycp.py names.txt -s           # also show disk space
python fuzzycp.py names.txt -c dest/dir  # copy matched files
python fuzzycp.py names.txt -m dest/dir  # move matched files
python fuzzycp.py names.txt -o           # write matched filenames to stdout
python fuzzycp.py names.txt -o out.txt   # write matched filenames to file

# Build standalone binary (macOS)
pyinstaller fuzzycp.spec
# Output binary: dist/fuzzycp
```

## Lint/Typecheck Commands

```bash
# Type checking (if mypy installed)
mypy fuzzycp.py --ignore-missing-imports

# Linting (if ruff installed)
ruff check fuzzycp.py

# Format check (if black installed)
black --check fuzzycp.py
```

## Test Commands

No test suite exists yet. When tests are added:

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_foo.py

# Run a single test function
pytest tests/test_foo.py::test_function_name

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=fuzzycp
```

## Code Style Guidelines

### Imports

Group imports by purpose with inline comments. Order: standard library, third-party, local (if any).

```python
# Fuzzy name matching
from rapidfuzz import process, fuzz
# Parsing command-line arguments
import argparse
# File operations, regex
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
```

### Formatting

- Line length: 88 characters (black default)
- Use 4 spaces for indentation
- No trailing whitespace
- Single blank line between functions
- Multiple blank lines (4) to separate major code sections

### Types

Type hints are not currently used but can be added. When adding:

```python
from typing import Dict, List, Tuple, Optional

def file_matching(names: List[str], filenames: List[str]) -> Dict[str, Tuple[str, float]]:
    ...

def read_names(filepath: str) -> List[str]:
    ...
```

### Naming Conventions

- Functions: `snake_case` (e.g., `file_matching`, `read_names`, `get_args`)
- Variables: `snake_case` (e.g., `best_matches`, `cleaned_fn`, `total`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `BRACKETED` for compiled regex)
- Command-line flags: single letter short form, `--word` long form (e.g., `-s`, `--space`)

### Error Handling

- Use try/except with specific exceptions
- Print user-friendly error messages to stderr
- Return sensible defaults (e.g., empty list for file read errors)
- Use `sys.exit(1)` for fatal errors

```python
try:
    with open(filepath, 'r') as file:
        names = [line.strip() for line in file]
    return names
except FileNotFoundError:
    print(f"Error: The file at {filepath} was not found.")
    return []
```

- Validate mutually exclusive arguments:

```python
if args.copy and args.move:
    print("Please specify move or copy, not both.")
    sys.exit(1)
```

### Docstrings

Use triple-quoted docstrings with Args/Returns sections for functions:

```python
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
```

### Comments

- Use inline comments to explain non-obvious logic
- Group major code sections with comment headers:

```python
# Parsing and preprocessing
# --------------------------------------------------------------------------------
```

### File Structure

The entire program lives in `fuzzycp.py` with this flow:

1. Imports
2. Function definitions
3. Main execution (module level, no `if __name__ == "__main__"` guard)

### Path Handling

- Use `pathlib.Path` for all path operations
- Use `Path.stem` to get filename without extension
- Use `Path.mkdir(parents=True, exist_ok=True)` for creating directories

### CLI Arguments

Use `argparse` with these patterns:

```python
p = argparse.ArgumentParser(prog="fuzzycp",
    description="File operations with fuzzy name matching.")

p.add_argument("names", help="path to file containing names to be matched")
p.add_argument("-s", "--space", action="store_true", help="...")
p.add_argument("-c", "--copy", metavar="PATH", type=Path, help="...")
p.add_argument("-o", "--output", metavar="PATH", nargs="?", const="-", help="...")
```

### Progress Bars

Use `tqdm` for long-running operations:

```python
for item in tqdm(items, total=len(items), desc="Processing"):
    # process item
```

### Output Formatting

- Use `termcolor.colored()` for terminal output with colors
- Use `humanize.naturalsize()` for human-readable file sizes
- Print errors to `sys.stderr` when appropriate

## Dependencies

From `requirements.txt`:
- `rapidfuzz` - fuzzy string matching
- `termcolor` - terminal colors
- `humanize` - human-readable file sizes
- `tqdm` - progress bars

## Key Functions

| Function | Purpose |
|----------|---------|
| `get_args()` | Parse command-line arguments |
| `read_names(filepath)` | Read query names from file |
| `preprocessing(files)` | Clean filenames (strip extension, normalize) |
| `file_matching(names, filenames)` | Fuzzy match names to filenames |

## Fuzzy Matching

The scorer (`fuzz.QRatio`) is a fast Levenshtein-based percentage after basic lowercase/whitespace cleaning. To swap for a different scorer, modify `file_matching()`:

```python
best_match = process.extractOne(name, filenames, scorer=fuzz.QRatio)
```

Other available scorers: `fuzz.ratio`, `fuzz.WRatio`, `fuzz.partial_ratio`
