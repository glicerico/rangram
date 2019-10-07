#!/bin/bash

# Processes a corpus from a given grammar with stream-parser and evaluates the results:
# SP: stream-parser

# Usage process_SP.sh <grammar_name> <maxWinObserve> <maxWinParse>

# Parameters
gram_name=$1
maxWinObserve=$2
maxWinParse=$3

rangram_workdir="/home/andres/Documents/ULL_project/rangram_workdir/"
SPPath="/home/andres/IdeaProjects/stream-parser/src/scripts/"

workdir_path=$rangram_workdir$gram_name
vocab_filename=$gram_name.vocab

# TODO: Abort if ULL conda environment has not been acivated

cd $workdir_path

# Parse using SP and evaluate
mkdir -p stream-parser
cd stream-parser

# Create vocabulary file
$SPPath/dictionary_dir.sh ../corpus $vocab_filename

# TODO: conda activate ull

$SPPath/stream_evaluate.sh $vocab_filename ../corpus ../corpus ../GS $maxWinObserve $maxWinParse



