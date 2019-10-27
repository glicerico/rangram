#!/bin/bash

# Creates folder structure and generates new corpus and its GS
# The given grammar name should exist in the workdir_path, inside the grammars folder

# Usage create_corpus.sh <grammarname> <corpus_size>

if [ $# -lt 2 ]
then
  echo "Usage: ./create_corpus.sh <grammarname> <corpus_size>"
  exit 0
fi

grammarname=$1
corpus_size=$2

HOME=/home/andres
rangram_workdir="$HOME/Documents/ULL_project/rangram_workdir/"
rangram_repo="$HOME/various_repos/rangram"

cd $rangram_workdir || exit
mkdir -p "$grammarname"
cd "$grammarname" || exit
mkdir -p corpus GS

# generate corpus and GS
python "${rangram_repo}/src/corpus_generator.py" -i "../grammars/${grammarname}.grammar" -o "${grammarname}.txt" -s "$corpus_size"

# Sort corpus and GS alphabetically (to avoid unlikely-sentence bias, see journal)
vim -T dumb --noplugin -n -es -S "${rangram_repo}/utils/sort_ull.ex" "${grammarname}.txt"
vim -T dumb --noplugin -n -es -S "${rangram_repo}/utils/sort_ull.ex" "${grammarname}.txt.ull"

mv "${grammarname}.txt" corpus
mv "${grammarname}.txt.ull" GS


