# rangram
Generator of random grammars, and corpora from them.

The current repo is an attempt to test different corpus-processing tools on a number of grammars.

The `src` folder contains the code used to generate random grammars, as well as corpora from them.
This folder includes:

+ grammar_generator.py creates a random grammar given a set of parameters.

The randomly created grammars follow a number of parameters,
specified in the header of the file containing the grammar:
```
% RANDOM GRAMMAR with parameters:
% num_words = 20
% num_classes = 4
% num_class_connectors = 7
% connectors_limit = 2
```

+ sentence_generator.py generates random sentences using a specified grammar.

+ corpus_generator.py uses the previously mentioned files to generate a random corpus.

The `utils` folder contains scripts for different purposes, e.g. to process a given grammar with some tool, and evaluate the results.
