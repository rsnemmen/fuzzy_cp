# `fuzzycp`: Fuzzy file operations (`mv`, `cp`) 

This program solves the following type of problem for which I found no existing tools. 

## The problem

You have a file `names.txt` containing a list of names:

```
1. The Legend of Zelda: Ocarina of Time
2. Super Mario 64
3. Mario Kart 64
4. GoldenEye 007
5. Super Smash Bros.
6. The Legend of Zelda: Majora's Mask
7. Banjo-Kazooie
8. Donkey Kong 64
9. Star Fox 64
10. Perfect Dark
```

You have a directory with hundreds of files, and you want to copy to another directory only the files that are the best-match to the names in the above list. Here are some examples of files in that directory:

```
'Spider-Man (U) [!].v64'
'StarCraft 64 (U) [!].v64'
'Starfox 64 1.1 (U).v64'                                                                           'Starshot - Space Circus Fever (U) [!].z64'
'Star Wars - Rogue Squadron (U) [!].v64'
'Star Wars - Shadows of the Empire (U) (V1.2) [!].v64'
'Star Wars Episode I - Battle for Naboo (U) [!].v64'
'Star Wars Episode I - Racer (U) [!].v64'
'Stunt Racer 64 (U) [!].z64'
'Super Bowling 64 (U) [!].z64'
'Supercross 2000 (U) [!].z64'
'Superman (U) (M3) [!].z64'
'Super Mario 64 (U) [!].v64'
```

## The solution

Normally people would do this sort of thing by manually selecting file by file and copying them. Not anymore. Here is how you solve this using `fuzzycp`. First `cd` to the directory containing the files.

Copy only the best-matching files to directory `dest/directory`:

    fuzzycp names.txt -c dest/directory

Move only the best-matching files to directory `dest/directory`:

    fuzzycp names.txt -m dest/directory

Print the best-matching files and the matching score:

    fuzzycp names.txt 

Print the best-matching files, and the space they occupy:

    fuzzycp names.txt -s


## Installation

TBD

```shell
brew install fuzzycp

pip install fuzzycp
```
