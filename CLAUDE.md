# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`fuzzycp` is a Python package and CLI tool that performs copy/move file operations using fuzzy name matching. Given a text file of names (one per line), it finds the best-matching filenames in the current working directory and optionally copies or moves them.

## Package layout

```
src/fuzzycp/
    __init__.py   — public API (file_matching, preprocessing, read_names, _threshold_type)
    __main__.py   — CLI entry point (get_args, main)
```

## Installing

```bash
pip install -e .          # editable install, enables `from fuzzycp import …`
```

## Running

```bash
# As a module (after editable install)
python -m fuzzycp names.txt              # print matches with scores
python -m fuzzycp names.txt -s           # also show disk space
python -m fuzzycp names.txt -t 70        # only show matches with score >= 70
python -m fuzzycp names.txt -c dest/dir  # copy matched files
python -m fuzzycp names.txt -m dest/dir  # move matched files
python -m fuzzycp names.txt -o           # write matched filenames to stdout
python -m fuzzycp names.txt -o out.txt   # write matched filenames to file
```

## Building a standalone binary

```bash
pyinstaller fuzzycp.spec
# Output binary: dist/fuzzycp
```

## Using as a library

```python
from fuzzycp import file_matching, preprocessing, read_names

files_cleaned = preprocessing(list_of_filenames)   # strips tags, extension, normalises whitespace
matches = file_matching(names, files_cleaned)       # dict: name → (best_cleaned_fn, score)
```

## Architecture

1. **`__init__.py`** — pure functions, no side effects, no argparse:
   - `preprocessing(files)` — strips extension, replaces `_`/`-` with spaces, removes bracketed content (e.g. `(U) [!]`), normalises whitespace. Returns cleaned list parallel to input.
   - `file_matching(names, filenames)` — uses `rapidfuzz.process.extractOne` with `fuzz.WRatio` to find one best match per name. Returns dict of `name → (cleaned_fn, score)`.
   - `read_names(filepath)` — reads query names from file, one per line.
2. **`__main__.py`** — argparse, candidate discovery (`glob.glob('*')`), `map_orig` collision handling, formatted output (termcolor), file copy/move (shutil + tqdm progress).

The scorer (`WRatio`) tries `ratio`, `partial_ratio`, `token_sort_ratio`, `token_set_ratio` and returns the max — robust for partial or reordered tokens. Swapping scorer is one line in `file_matching()`.

`map_orig` groups multiple files that clean to the same stem (e.g. `movie.mp4` and `movie.mkv`) so all variants are included in the operation.
