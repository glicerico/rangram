#!/bin/bash

# Processes a corpus from a given grammar with the ULL-parser and evaluates the results:

# Usage process_ULLP.sh <grammar_name> <db_name>

# Parameters
gram_name=$1
db_name=$2 # psql db to use
cnt_mode="clique-dist"
cnt_reach=6

HOME="/home/andres"
ULL_workdir="$HOME/Documents/ULL_project/minimal_workdir"
rangram_workdir="$HOME/Documents/ULL_project/rangram_workdir/"

workdir_path=$rangram_workdir$gram_name

cd $workdir_path

# Create local copy of workdir
mkdir -p ULL-parser
cd ULL-parser
cp -r $ULL_workdir/* .

# Replace params above in config/params.txt
sed -i -e "s/cnt_mode\S*/cnt_mode=\"${cnt_mode}\"/" config/params.txt
sed -i -e "s/cnt_reach\S*/cnt_reach=${cnt_reach}/" config/params.txt

cp ../corpus/* beta-pages/
cp ../corpus/* gamma-pages/

./reset_database.sh $db_name

# Parse using ULLP and evaluate
#rm -r mst-parses mi-pairs.txt
# TODO: Start cogserver and send "one-go" to it.

source activate ull
parse-evaluator -i -r ../GS -t mst-parses

mkdir -p stats
mv *.stat stats

