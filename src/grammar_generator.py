#!/usr/bin/env python
# coding: utf-8

# # Random grammar generation
# # Creates a scale-free random grammar with specified parameters

import sys, getopt, os
from fractions import Fraction
import numpy as np
import random as rand

# We start by obtaining the parameters of the grammar
num_words = 20
num_classes = 4
num_class_connectors = 7
connectors_limit = 2
outfile = "rand_grammar.txt"

def main(argv):
    # Populate grammar classes following a Zipf distribution
    harmonic_number = sum(Fraction(1, d) for d in range(1, num_classes + 1))
    zipf_fracs = [1 / x / harmonic_number for x in range(1, num_classes + 1)]
    words_per_class = np.array(np.round(np.array(zipf_fracs) * num_words), dtype = "int")
    cumul_words = np.cumsum(words_per_class) # boundaries for class words

    # Create random connectors between grammar classes
    connectors = set()
    for i in range(0, num_class_connectors - 1):
        randint1 = rand.randint(0, num_classes - 1)
        randint2 = rand.randint(0, num_classes - 1)
        if randint1 != randint2: # avoid classes connecting to themselves; may cause less connections than param
            connectors.add((randint1, randint2))

    # Assign connectors to classes
    # Translate connectors into connector labels
    connectors_dict = {k:[] for k in range(num_classes)}
    connectors_dict_text = {k:[] for k in range(num_classes)}
    for connector in connectors:
        connector_text = "C" + str(connector[0]) + "_" + str(connector[1])
        connectors_dict[connector[0]].append(connector)
        connectors_dict[connector[1]].append(connector)
        connectors_dict_text[connector[0]].append(connector_text + "+")
        connectors_dict_text[connector[1]].append(connector_text + "-")
        
    print(connectors_dict_text)
    print(connectors_dict)


    # Build the disjuncts randomly, with some directives
    dict_disjuncts = {}
    for gramm_class, connects in connectors_dict.items():
         # don't conjunct more connectors than available ones, nor than limit
        max_connectors = min(connectors_limit, len(connects))
        disjuncts = []
        
        for connector in connects: # create one conjunct per connector; arbitrary choice
            num_connectors = rand.randint(1, max_connectors) # determine how many connectors for this conjunct
            conjunct = [connector] # current connector always goes in conjunct
            
            diff_connects = connects[:] # make independent copy
            diff_connects.remove(connector) # don't repeat connector in a conjunct
            conjunct.extend(rand.sample(diff_connects, num_connectors - 1)) # add random connectors to conjunct; no repeats
                
            disjuncts.append(conjunct)
            
        dict_disjuncts[gramm_class] = set(tuple(d) for d in disjuncts) # set eliminates duplicate disjuncts

    print(dict_disjuncts)


    # Translate grammar to dictionary format
    grammar_text = f"""
    % RANDOM GRAMMAR with parameters:
    % num_words = {num_words}
    % num_classes = {num_classes}
    % num_class_connectors = {num_class_connectors}
    % connectors_limit = {connectors_limit}
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    """

    dict_vocab = {} # Vocabulary dict per class
    for curr_class, disjunct in dict_disjuncts.items():
        class_entry = f"% Class: {curr_class}\n" # Description of current disjunct
        # Calculate initial word_id for class
        if curr_class == 0:
            lower_id = 0
        else:
            lower_id = cumul_words[curr_class - 1]
            
        # Add word list to class_entry
        class_words = [f'W{i}' for i in range(lower_id, cumul_words[curr_class])]
        dict_vocab[curr_class] = class_words
        class_entry += " ".join(class_words) + ":\n"
        
        # Add every conjunct to disjunct
        curr_disjunct = []
        for conjunct in disjunct:
            curr_conjunct = []
            for connector in conjunct:
                connector_text = "C" + str(connector[0]) + "_" + str(connector[1])
                sign = "+" if connector[0] == curr_class else "-" # choose connector sign
                curr_conjunct.append(connector_text + sign)
            curr_disjunct.append(" & ".join(curr_conjunct))
            
        class_entry += "(" + ") or (".join(curr_disjunct) + ");\n\n"
        grammar_text += class_entry
        
    print(grammar_text)

    with open(outfile, 'w') as fo:
        fo.write(grammar_text)

    grammar = [dict_disjuncts, dict_vocab]
    return grammar

if __name__ == "__main__":
    main(sys.argv[1:])