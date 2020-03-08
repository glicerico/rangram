#!/bin/bash

# Learns a given grammar with Grammar-Learner and evaluates the results:

# Usage process_GL.sh <grammar_name> <input_parses>

if [ $# -lt 2 ]
then
  echo "Usage: ./process_GL.sh <gram_name> <input_parses>"
  exit 0
fi

# Parameters
gram_name=$1
input_parses=$2

HOME="/home/andres/"
rangram_path="$HOME/repositories/rangram"
rangram_workdir="$HOME/Documents/ULL_project/rangram_workdir/"
ULL_path="$HOME/MyOpenCogSources/language-learning/"

workdir_path=$rangram_workdir/$gram_name

# Create GL directory
rm -r $workdir_path/grammar-learner
mkdir $workdir_path/grammar-learner
cd $workdir_path/grammar-learner

json_filename=${gram_name}-GL-GT-DB.json
cp $rangram_path/templates/template-GL-GT-DB.json $json_filename
# Replace params above in template for GL
sed -i -e "s/file_path.*/file_path\": \"%ROOT\/results.dat\",/" ${json_filename}
sed -i -e "s/PARSES\".*/PARSES\": \"%ROOT\/..\",/" ${json_filename}
sed -i -e "s/parsing\": \"\"/parsing\": \"${input_parses}\"/g" $json_filename
sed -i -e "s/input_corpus.*/input_corpus\": \"%ROOT\/..\/${input_parses}\",/" ${json_filename}
sed -i -e "s/ref_path.*/ref_path\": \"%ROOT\/..\/${input_parses}\",/" ${json_filename}
sed -i -e "s/grammar_root.*/grammar_root\": \"%ROOT\",/" ${json_filename}

# Learn grammar with GL and evaluate
source activate ull
ull-cli -C ${json_filename}

# Append GL results to all_results file
printf "Grammar-learner results:\n\n" >> ../all_results.txt
cat results.dat >> ../all_results.txt
printf "#################### \n\n" >> ../all_results.txt
