#!/bin/bash

# Processes a corpus from a given grammar with three different methods, and evaluates them:
# SP: stream-parser
# ULLP: ULL parser
# GL: Grammar learner

# Usage evaluate_grammar.sh <grammar_name>

# Parameters
gram_name=$1
maxWinObserve=2
maxWinParse=2

rangram_workdir="/home/andres/Documents/ULL_project/rangram_workdir/"
SPPath="/home/andres/IdeaProjects/stream-parser/src/scripts/"

workdir_path=$rangram_workdir$gram_name
vocab_filename=$gram_name.vocab

# Abort if ULL conda environment has not been acivated


cd $workdir_path

# Parse using SP and evaluate
mkdir -p stream-parser
cd stream-parser

# Create vocabulary file
$SPPath/dictionary_dir.sh ../corpus $vocab_filename

# TODO: conda activate ull

$SPPath/stream_evaluate.sh $vocab_filename ../corpus ../corpus ../GS $maxWinObserve $maxWinParse



