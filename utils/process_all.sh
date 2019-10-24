#!/bin/bash

# Processes a corpus from a given grammar with three different methods, and evaluates them:
# SP: stream-parser
# ULLP: ULL parser
# GL: Grammar learner

# Usage evaluate_grammar.sh <grammar_name>

# Parameters
gram_name=$1
maxWinObserve=10
maxWinParse=10
db_name="test"

HOME=/home/andres
utils_dir="$HOME/various_repos/rangram/utils/"
rangram_workdir="$HOME/Documents/ULL_project/rangram_workdir/"
workdir_path=$rangram_workdir/$gram_name

# Reset all_results file
cd "${workdir_path}" || exit
truncate -s 0 all_results.txt

# Generate sequential and random baselines
source activate ull
mkdir -p sequential
cd sequential || exit
parse-evaluator -si -r ../GS -t ../GS
# Append sequential results to all_results file
{
  printf "Sequential parser results:\n\n"; cat ./*.stat; printf "#################### \n\n"
} >> ../all_results.txt
cd ..

mkdir -p random
cd random || exit
parse-evaluator -zi -r ../GS -t ../GS
# Append random results to all_results file
{
  printf "Random parser results:\n\n"
  cat ./*.stat
  printf "#################### \n\n"
} >> ../all_results.txt
cd ..

# Process with different methods
printf "Parsing corpus with stream parser, with parameters:\n maxWinObserve: %s maxWinParse: %s\n" "$maxWinObserve" "$maxWinParse"
$utils_dir/process_SP.sh "$gram_name" $maxWinObserve $maxWinParse
printf "Parsing corpus with ULL parser, using database %s\n" "$db_name"
$utils_dir/process_ULLP.sh "$gram_name" "$db_name"
printf "Learning grammar with Grammar Learner, using GS parses\n"
$utils_dir/process_GL.sh "$gram_name" GS

printf "Finished processing. Results available in their respective folders in:\n%s/Documents/ULL_project/rangram_workdir/%s \n" "$HOME" "$gram_name"
