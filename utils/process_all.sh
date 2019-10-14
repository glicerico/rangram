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

# Reset all_results file
echo "" > all_results.txt

# Process with different methods
echo "Parsing corpus with stream parser, with parameters:\n maxWinObserve: $maxWinObserve; maxWinParse: $maxWinParse"
$utils_dir/process_SP.sh $gram_name $maxWinObserve $maxWinParse
echo "Parsing corpus with ULL parser, using database $db_name"
$utils_dir/process_ULLP.sh $gram_name db_name
echo "Learning grammar with Grammar Learner, using GS parses"
$utils_dir/process_GL.sh $gram_name GS

echo "Finished processing. Results available in their respective folders in:\n$HOME/Documents/ULL_project/rangram_workdir/$gram_name"
