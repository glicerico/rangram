#!/usr/bin/env python
# coding=utf-8
# runs on python3

import sys
import os
import string

ROOT_WORD = "###LEFT-WALL###"
IGNORED_WORD = "###PUNCTUATION###"
IGNORED_FLAG = -1


def tag_punctuation(sentence):
    """
    Remove punctuation, and tag every token that only contains punctuation
    """
    tagged_sentence = []
    tagged_len = -1  # start negative to avoid counting the ROOT_WORD
    mapping = []
    num_punctuations = 0  # count how many tokens are punctuation
    translator = str.maketrans('', '', string.punctuation)  # create translation table
    for cnt, word in enumerate(sentence):
        new_word = word.translate(translator)
        if len(new_word) > 0:
            tagged_sentence.append(new_word)
            mapping.append(cnt - num_punctuations)
            tagged_len += 1
        else:
            tagged_sentence.append(IGNORED_WORD)
            num_punctuations += 1
            mapping.append(IGNORED_FLAG)

    return tagged_sentence, tagged_len, mapping


def create_links(sentence, mapping, link_ids):
    """
    Create links with correct numbering after punctuation removal
    """
    links = []
    for link in link_ids:
        mapped_ll = mapping[link[0]]  # mapped ids (adjusting for removed punctuation)
        mapped_rl = mapping[link[1]]  # mapped ids (adjusting for removed punctuation)
        if mapped_rl != IGNORED_FLAG and mapped_ll != IGNORED_FLAG:  # discard links with punctuation
            links.append(str(mapped_ll) + " " + sentence[link[0]] + " " + str(mapped_rl) + " " + sentence[link[1]])

    links.sort()
    return links


def main(argv):
    """
    Transforms dependency parses in CoNLL format to ULL format

    Usage: python conll2ull.py <conll_filepath> <punct_flag> <max_length> <lower_caps>

    conll_filepath:     (str) Filepath to CONLL file
    punct_flag:         (int) Boolean flag to remove or not remove punctuation
    max_length:         (int) Ignore sentences longer than this parameter, after punctuation removal
    lower_caps:         (int) Boolean flag to convert to lowercaps
    """

    if len(argv) < 4:
        print("Usage: python conll2ull.py <conll_filepath> <punct_flag> <max_length>")

    dirpath = argv[0]
    punct_flag = bool(int(argv[1]))  # Flag to remove punctuation
    punct_str = punct_flag * 'noPunct'  # String flag
    max_length = int(argv[2])  # max length of sentences to process after punctuation removal (if any)
    lower_caps = bool(int(argv[3]))  # Flag to convert to lowercaps
    lower_str = lower_caps * 'lower'
    print(f"\nProcessing file {dirpath}\npunct_flag={punct_flag}\nmax_length={max_length}\n")

    num_parses = 0  # num of parses in output file
    sentence = [ROOT_WORD]
    link_ids = []

    newdir = dirpath + '_ull_' + punct_str + str(max_length) + lower_str + '/'
    os.mkdir(newdir)
    os.mkdir(newdir + 'GS')
    os.mkdir(newdir + 'corpus')
    for conll_filename in os.scandir(dirpath):
        if conll_filename.path.endswith('.conll') and conll_filename.is_file():
            with open(conll_filename, 'r') as fi:
                with open(newdir+'GS/'+conll_filename.name + ".txt.ull", 'w') as fo:
                    with open(newdir+'corpus/'+conll_filename.name + ".txt", 'w') as fc:
                        lines = fi.readlines()
                        for line in lines:
                            # Process parse when newline is found
                            if line == "\n":
                                if punct_flag:  # Punctuation removal is an option
                                    tagged_sent, tagged_len, mapping = tag_punctuation(sentence)
                                else:
                                    tagged_sent = sentence
                                    tagged_len = len(sentence) - 1  # Do not count ROOT_WORD
                                    mapping = [i for i in range(len(sentence))]

                                # Only print sentences within desired length
                                if 0 < tagged_len <= max_length:
                                    links = create_links(tagged_sent, mapping, link_ids)
                                    clean_sent = [word for word in tagged_sent[1:] if word != IGNORED_WORD]
                                    fc.write(" ".join(clean_sent) + "\n\n")  # print to corpus file
                                    fo.write(" ".join(clean_sent) + "\n")  # print to parses file
                                    fo.write("\n".join(links) + "\n\n")
                                    num_parses += 1

                                # reset arrays
                                sentence = [ROOT_WORD]
                                link_ids = []

                            # Links are still being processed
                            else:
                                if lower_caps:
                                    line = line.lower()
                                split_line = line.split('\t')
                                link_ids.append([int(split_line[6]), int(split_line[0])])  # store links indexes
                                sentence.append(split_line[1])  # build sentence array

    print(f"Converted {num_parses} parses with len <= {max_length}")


if __name__ == "__main__":
    main(sys.argv[1:])
