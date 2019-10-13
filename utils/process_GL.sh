#!/bin/bash

# Learns a given grammar with Grammar-Learner and evaluates the results:

# Usage process_GL.sh <grammar_name> <input_parses>

# Parameters
gram_name=$1
input_parses=$2

HOME="/home/andres/"
rangram_path="$HOME/various_repos/rangram"
rangram_workdir="$HOME/Documents/ULL_project/rangram_workdir/"
ULL_path="$HOME/MyOpenCogSources/language-learning/"

workdir_path=$rangram_workdir/$gram_name

# Create GL directory
mkdir -p $workdir_path/GL/
cd $workdir_path/GL

json_filename=${gram_name}-GL-GT-DB.json
cp $rangram_path/templates/template-GL-GT-DB.json $json_filename
# Replace params above in template for GL
sed -i -e "s/file_path.*/file_path\": \"%ROOT\/results.dat\",/" ${json_filename}
sed -i -e "s/PARSES\".*/PARSES\": \"%ROOT\/..\/${input_parses}\",/" ${json_filename}
sed -i -e "s/parsing\": \"\"/parsing\": \"%ROOT\/..\/${input_parses}\"/g" $json_filename
sed -i -e "s/input_corpus.*/input_corpus\": \"%ROOT\/..\/${input_parses}\",/" ${json_filename}
sed -i -e "s/ref_path.*/ref_path\": \"%ROOT\/..\/${input_parses}\",/" ${json_filename}
sed -i -e "s/grammar_root.*/grammar_root\": \"%ROOT\",/" ${json_filename}

# Learn grammar with GL and evaluate
source activate ull
ull-cli -C ${json_filename}

