#!/bin/bash

# Processes a corpus from a given grammar with the ULL-parser and evaluates the results:

# Usage process_ULLP.sh <grammar_name> <db_name>

if [ $# -lt 2 ]
then
  echo "Usage: ./process_ULLP.sh <gram_name> <db_name>"
  exit 0
fi

# Parameters
gram_name=$1
db_name=$2 # psql db to use
cnt_mode="clique-dist"
cnt_reach=6

HOME="/home/andres"
ULL_workdir="$HOME/Documents/ULL_project/minimal_workdir"
rangram_workdir="$HOME/Documents/ULL_project/rangram_workdir/"

workdir_path=$rangram_workdir/$gram_name

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
rm -r mst-parses mi-pairs.txt

# Parse using ULLP and evaluate
# TODO: Start cogserver and send "one-go" to it.
byobu new-session -d -s 'ULLP' -n 'cogsrv' "nice guile -l launch-cogserver.scm -- --mode pairs --lang en --db $db_name; $SHELL"
echo "Waiting for launch-cogserver.sh to compile..."
sleep 10
tmux new-window -n 'processing' "./one-go.sh; source activate ull; parse-evaluator -i -r ../GS -t mst-parses; tmux kill-session -t 'ULLP'"
tmux attach
echo "Results stored in *.stat file"

# Append SP results to all_results file
printf "ULL parser results:\n\n" >> ../all_results.txt
cat *.stat >> ../all_results.txt
printf "#################### \n\n" >> ../all_results.txt
