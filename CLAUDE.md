# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`fuzzycp` is a single-file Python CLI tool (`fuzzycp.py`) that performs copy/move file operations using fuzzy name matching. Given a text file of names (one per line), it finds the best-matching filenames in the current working directory and optionally copies or moves them.

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python fuzzycp.py names.txt              # print matches with scores
python fuzzycp.py names.txt -s           # also show disk space
python fuzzycp.py names.txt -t 70        # only show matches with score >= 70
python fuzzycp.py names.txt -c dest/dir  # copy matched files
python fuzzycp.py names.txt -m dest/dir  # move matched files
python fuzzycp.py names.txt -o           # write matched filenames to stdout
python fuzzycp.py names.txt -o out.txt   # write matched filenames to file
```

## Building a standalone binary

```bash
pyinstaller fuzzycp.spec
# Output binary: dist/fuzzycp
```

## Architecture

The entire program lives in `fuzzycp.py` and executes at module level (no `main()` guard). The flow is:

1. **Argument parsing** (`get_args`) — argparse, positional `names` file + flags `-s`, `-c`, `-m`, `-o`, `-t`
2. **Read names** (`read_names`) — reads the query names list from the provided file
3. **Discover candidates** — `glob.glob('*')` on the current working directory (non-hidden files only)
4. **Preprocess filenames** (`preprocessing`) — strips extension, replaces `_`/`-` with spaces, removes bracketed content (e.g. `(U) [!]`), normalizes whitespace; builds a `map_orig` dict from cleaned name → original filename
5. **Fuzzy match** (`file_matching`) — uses `rapidfuzz.process.extractOne` with `fuzz.QRatio` scorer to find the best match per name from the cleaned filenames list
6. **Filter & output** — filters matches below `args.threshold` (default 50), prints name | best-match | score (colorized), or writes filenames to file/stdout if `-o` given
7. **File operation** — prompts for confirmation, then copies (`shutil.copy2`) or moves (`shutil.move`) matched files to destination with a `tqdm` progress bar

The scorer (`QRatio`) is a fast Levenshtein-based percentage after basic lowercase/whitespace cleaning. Swapping for a different `rapidfuzz` scorer is straightforward in `file_matching()`.

