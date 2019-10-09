#!/bin/bash

# Learns a given grammar with Grammar-Learner and evaluates the results:

# Usage process_GL.sh <grammar_name>

# Parameters
gram_name=$1
input_parses=$2

HOME="/home/andres/"
rangram_path="$HOME/various_repos/rangram"
rangram_workdir="$HOME/Documents/ULL_project/rangram_workdir/"
ULL_path="$HOME/MyOpenCogSources/language-learning/"

workdir_path=$rangram_workdir/$gram_name

# Copy input parses to learn grammar from
cp -r $workdir_path/$input_parses $ULL_path/data/tmp/

# Learn grammar with GL and evaluate
source activate ull
cd $ULL_path/pipeline
python ppln.py $rangram_path/templates/tmp.json

mv $ULL_path/output/tmp/ $workdir_path/GL

#cd $workdir_path/GL
#cp $rangram_path/templates/tmp.json ./${gram_name}_ALE.json

# Add current params to json file

