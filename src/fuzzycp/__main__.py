#!/usr/bin/env python3

import argparse
import glob
import os
import sys
import shutil
from pathlib import Path

from termcolor import colored
import humanize
from tqdm.auto import tqdm

from fuzzycp import file_matching, read_names, preprocessing, _threshold_type


def _argparse_threshold(value):
    try:
        return _threshold_type(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def get_args():
    p = argparse.ArgumentParser(
        prog="fuzzycp",
        description="File operations with fuzzy name matching.",
    )
    p.add_argument("names", help="path to file containing names to be matched")
    p.add_argument("-s", "--space", action="store_true",
                   help="display disk space occupied by matching files")
    p.add_argument("-c", "--copy", metavar="PATH", type=Path,
                   help="copy matching files to this destination path")
    p.add_argument("-m", "--move", metavar="PATH", type=Path,
                   help="move matching files to a given dir")
    p.add_argument("-o", "--output", metavar="PATH", nargs="?", const="-",
                   help="write matching filenames to file, or stdout if no path given")
    p.add_argument("-t", "--threshold", type=_argparse_threshold, default=50,
                   help="minimum match score (0-100), default 50")
    return p.parse_args()


def main():
    args = get_args()

    if args.output == "-":
        out = sys.stdout
    elif args.output is not None:
        out = open(Path(args.output), "w")
    else:
        out = None

    names = read_names(args.names)
    if not names:
        print("Error: no names to match (file empty or not found).", file=sys.stderr)
        sys.exit(1)

    candidates = glob.glob('*')
    files = [f for f in candidates if os.path.isfile(f)]
    files_cleaned = preprocessing(files)

    map_orig: dict = {}
    for cleaned, orig in zip(files_cleaned, files):
        map_orig.setdefault(cleaned, []).append(orig)

    best_matches = file_matching(names, files_cleaned)

    total = 0
    rows = []
    for name, (cleaned_fn, score) in best_matches.items():
        if score < args.threshold:
            continue
        for original_fn in map_orig[cleaned_fn]:
            rows.append((name, original_fn, round(score)))
            if args.space:
                total += os.path.getsize(original_fn)

    if out is not None:
        for name, original_fn, score in rows:
            print(original_fn, file=out)
        if out is not sys.stdout:
            out.close()
    else:
        col1_w = max((len(r[0]) for r in rows), default=4)
        col2_w = max((len(r[1]) for r in rows), default=10)
        col1_w = max(col1_w, len("Name"))
        col2_w = max(col2_w, len("Best-match"))
        header = (
            colored("Name", "green").ljust(col1_w + (len(colored("Name", "green")) - len("Name")))
            + "  "
            + colored("Best-match", "blue").ljust(col2_w + (len(colored("Best-match", "blue")) - len("Best-match")))
            + "  "
            + colored("Score", "red")
        )
        print(header)
        for name, original_fn, score in rows:
            print(
                colored(name, "green").ljust(col1_w + (len(colored(name, "green")) - len(name)))
                + "  "
                + colored(original_fn, "blue").ljust(col2_w + (len(colored(original_fn, "blue")) - len(original_fn)))
                + "  "
                + colored(str(score), "red")
            )
        if args.space:
            print()
            print("Disk space =", humanize.naturalsize(total, binary=True))

    if args.copy and args.move:
        print("Please specify move or copy, not both.")
        sys.exit(1)
    elif args.copy:
        user_input = input("\n Proceed copying the files marked in blue? (Y/N): ")
        print()
        description = "Copying files"
        dst = Path(args.copy)
    elif args.move:
        user_input = input("\n Proceed moving the files marked in blue? (Y/N): ")
        print()
        description = "Moving files"
        dst = Path(args.move)

    if args.copy or args.move:
        if user_input.lower() == 'y':
            filtered_files = []
            for name, (cleaned_fn, score) in best_matches.items():
                if score >= args.threshold:
                    for original_fn in map_orig[cleaned_fn]:
                        filtered_files.append(original_fn)
            dst.mkdir(parents=True, exist_ok=True)
            for original_fn in tqdm(filtered_files, desc=description):
                src = Path(original_fn)
                target = dst / src.name
                if args.copy:
                    shutil.copy2(src, target)
                if args.move:
                    shutil.move(src, target)
        else:
            print("Operation cancelled.")


if __name__ == "__main__":
    main()
