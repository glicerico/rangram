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
db_name=test

HOME=/home/andres
utils_dir="$HOME/various_repos/rangram/utils/"
workdir_path=$rangram_workdir/$gram_name

# Reset all_results file
truncate -s 0 ${workdir_path}/all_results.txt

# Process with different methods
printf "Parsing corpus with stream parser, with parameters:\n maxWinObserve: $maxWinObserve; maxWinParse: $maxWinParse\n"
$utils_dir/process_SP.sh $gram_name $maxWinObserve $maxWinParse
printf "Parsing corpus with ULL parser, using database $db_name\n"
$utils_dir/process_ULLP.sh $gram_name db_name
printf "Learning grammar with Grammar Learner, using GS parses\n"
$utils_dir/process_GL.sh $gram_name GS

printf "Finished processing. Results available in their respective folders in:\n$HOME/Documents/ULL_project/rangram_workdir/$gram_name \n"
