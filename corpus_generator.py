#!/usr/bin/env python
# coding=utf-8
# runs on python3

# ASuMa, Aug 2019

import sys, getopt, os
import re
from sentence_generator import GrammarSampler

__all__ = []

def main(argv):
    """
        Corpus_generator takes two mandatory arguments and several optional ones:

        "Usage: corpus_generator.py -o <outfile>
                                    [-g <grammar_mode> -s <corpus_size> -i <input_grammar> 
                                    -v <vocab_size>]"

        outfile             File to output resulting corpus.
        [
        grammar_mode        Either "existing" or "generate". Specifies if using existing
                            grammar file (in which case it should be given via "-i") or
                            if a random grammar should be generated (default grammar parameters
                            can be altered via the corresponding flags below). (default: 'existing')
                            TODO: implement "generate" mode
        corpus_size         Number of sentences to create for the corpus. (default: 10)
        input_grammar       File with given hand-coded grammar.
                            If "existing" mode is used, the grammar parameters are ignored 
                            since no random grammar is generated.
        GRAMMAR PARAMS: *** TODO: NOT IMPLEMENTED YET
        vocab_size          Size of vocabulary for generated grammar [default: 20]
        num_classes         Number of grammatical classes in generated grammar [default: 4]
        num_relations       Max number of relations to create between grammatical classes [def: 7]
        connectors_limit    Max number of connectors allowed per word [deault: 2]
        ]
    """

    kwargs = {}
    # Default values
    input_grammar = ''
    grammar_mode = 'existing'
    corpus_size = 10

    try:
        opts, args = getopt.getopt(argv,"hg:s:o:i:",["grammar_mode=",
            "corpus_size=", "outfile=", "input_grammar="])
    except getopt.GetoptError:
        print('''Usage: corpus_generator.py -o <outfile>
                                    [-g <grammar_mode> -s <corpus_size> -i <input_grammar> -v <vocab_size>]''')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('''Usage: corpus_generator.py -o <outfile>
                                        [-g <grammar_mode> -s <corpus_size> -i <input_grammar> -v <vocab_size>]''')
            sys.exit()
        elif opt in ("-g", "--grammar_mode"):
            if opt != "existing":
                raise getopt.GetoptError("Only 'existing' mode is currently implemented")
            grammar_mode = arg
        elif opt in ("-s", "--corpus_size"):
            corpus_size = int(arg)
        elif opt in ("-o", "--outfile"):
            outfile = arg
        elif opt in ("-i", "--input_grammar"):
            input_grammar = arg

    # Check input grammar file was specified
    if input_grammar == '':
        raise getopt.GetoptError("No grammar file specified")

    #Execute_Precleaner(inputdir, outputdir, **kwargs)
    GenerateCorpus(grammar_mode, corpus_size, outfile, input_grammar)


def GenerateCorpus(grammar_mode: str, corpus_size: int, outfile: str, input_grammar: str):
    """
    Corpus generator. Uses class GrammarSampler in sentence_generator.py
    """

    grammar = GrammarSampler(input_grammar)
    sentences = set(); # keeps unique sentences

    with open(outfile, 'w') as fcorpus:
        with open(outfile + ".ull", 'w') as fparses:
            for counter in range(0, corpus_size):
                sentence, parse = grammar.GenerateParse()
                if sentence not in sentences:
                    sentences.add(sentence)
                    fcorpus.write(sentence + '\n\n')
                    fparses.write(sentence + '\n')
                    fparses.write(parse + '\n\n')
    print(f"Generated {len(sentences)} unique sentences, out of {corpus_size} requested\n")

if __name__ == "__main__":
    main(sys.argv[1:])
