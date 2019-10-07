#!/bin/bash

# Processes a corpus from a given grammar with the ULL-parser and evaluates the results:

# Usage process_ULLP.sh <grammar_name> <db_name>

# Parameters
gram_name=$1
db_name=$2 # psql db to use
obs_method="any"
cnt_reach=24

ULL_workdir="~/Documents/ULL_project/minimal_workdir"

# TODO
# replace params above in config/params.txt

rangram_workdir="/home/andres/Documents/ULL_project/rangram_workdir/"

workdir_path=$rangram_workdir$gram_name

# TODO: Abort if ULL conda environment has not been acivated
# TODO: conda activate ull

cd $workdir_path

# Parse using ULLP and evaluate
mkdir -p ULL-parser
cd ULL-parser
cp -r $ULL_workdir/* .
cp ../corpus/* beta-pages
cp ../corpus/* gamma-pages

./reset_database.sh $db_name

# Start cogserver and send "one-go" to it.


