#!/bin/bash

# Processes a corpus from a given grammar with stream-parser and evaluates the results:

# Usage process_SP.sh <grammar_name> <maxWinObserve> <maxWinParse>

if [ $# -lt 3 ]
then
  echo "Usage: ./process_SP.sh <grammar_name> <maxWinObserve> <maxWinParse>"
  exit 0
fi

# Parameters
gram_name=$1
maxWinObserve=$2
maxWinParse=$3

HOME="/home/andres/"
rangram_workdir="$HOME/Documents/ULL_project/rangram_workdir/"
SPPath="$HOME/IdeaProjects/stream-parser/src/scripts/"

workdir_path=$rangram_workdir/$gram_name
vocab_filename=$gram_name.vocab

cd $workdir_path
mkdir -p stream-parser
cd stream-parser

# Create vocabulary file
$SPPath/dictionary_dir.sh ../corpus $vocab_filename

# Parse using SP and evaluate
$SPPath/stream_evaluate.sh $vocab_filename ../corpus ../corpus ../GS $maxWinObserve $maxWinParse

# Append SP results to all_results file
printf "Stream-parser results:\n\n" >> ../all_results.txt
cat results.dat >> ../all_results.txt
printf "#################### \n\n" >> ../all_results.txt
