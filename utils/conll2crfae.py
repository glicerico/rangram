#!/usr/bin/env python
# coding=utf-8
# runs on python3

import sys
import os

ROOT_WORD = "###LEFT-WALL###"
IGNORED_WORD = "###PUNCTUATION###"
IGNORED_FLAG = -1


def tag_punctuation(sentence, pos_list, heads_list):
    """
    Remove punctuation tokens, guided by the tags in the conll file
    """
    tagged_len = 0
    num_punctuations = 0  # count how many tokens are punctuation
    tagged_sentence = []
    clean_pos = []
    clean_heads = []
    mapping = []

    for cnt, word in enumerate(sentence):
        if pos_list[cnt] not in ['p', 'punct']:  # non-punctuation token
            tagged_sentence.append(word)
            clean_pos.append(pos_list[cnt])
            clean_heads.append(heads_list[cnt])
            mapping.append(cnt - num_punctuations)
            tagged_len += 1
        else:  # token is punctuation
            tagged_sentence.append(IGNORED_WORD)
            num_punctuations += 1
            mapping.append(IGNORED_FLAG)

    return tagged_sentence, tagged_len, mapping, clean_pos, clean_heads

def main(argv):
    """
    Transforms dependency parses in CoNLL format to CRFAE parser input format

    Usage: python conll2crfae.py <dirpath> <punct_flag> <max_length> <lower_caps>

    dirpath:            (str) Directory path with CONLL files
    punct_flag:         (int) Boolean flag to remove or not remove punctuation
    max_length:         (int) Ignore sentences longer than this parameter, after punctuation removal
    lower_caps:         (int) Boolean flag to convert to lowercaps
    """

    if len(argv) < 4:
        print("Usage: python conll2crfae.py <dirpath> <punct_flag> <max_length>")

    dirpath = argv[0]
    punct_flag = bool(int(argv[1]))  # Flag to remove punctuation
    punct_str = punct_flag * 'noPunct'  # String flag
    max_length = int(argv[2])  # max length of sentences to process after punctuation removal (if any)
    lower_caps = bool(int(argv[3]))  # Flag to convert to lowercaps
    lower_str = lower_caps * 'lower'
    print(f"\nProcessing files in {dirpath}\npunct_flag={punct_flag}\nmax_length={max_length}\n")

    num_parses = 0  # Num of parses in output file
    sentence = []
    pos_list = []  # List with POS for each word, to detect punctuation
    heads_list = []  # List with heads for each word, to detect punctuation

    # Build directory structure for converted corpus parses
    newdir = dirpath + '_crfae_' + punct_str + '_' + str(max_length) + '_' + lower_str + '/'
    if not os.path.isdir(newdir):
        os.mkdir(newdir)
        os.mkdir(newdir + 'GS')
        os.mkdir(newdir + 'corpus')

    for conll_filename in os.scandir(dirpath):
        if conll_filename.path.endswith('.conll') and conll_filename.is_file():
            with open(conll_filename, 'r') as fi:
                with open(newdir+'GS/'+conll_filename.name + ".txt.crfae", 'w') as fo:
                    with open(newdir+'corpus/'+conll_filename.name + ".txt", 'w') as fc:
                        lines = fi.readlines()
                        for line in lines:
                            # Skip comments
                            if line.startswith("#"):
                                pass
                            # Process parse when newline is found
                            elif line == "\n":
                                if punct_flag:  # Punctuation removal is an option
                                    tagged_sent, tagged_len, mapping, clean_pos, clean_heads = tag_punctuation(sentence, pos_list, heads_list)
                                else:
                                    tagged_sent = sentence
                                    tagged_len = len(sentence) - 1  # Do not count ROOT_WORD
                                    clean_pos = pos_list

                                # Only print sentences within desired length
                                if 0 < tagged_len <= max_length:
                                    clean_sent = [word for word in tagged_sent if word != IGNORED_WORD]
                                    fc.write(" ".join(clean_sent) + "\n\n")  # print to corpus file
                                    fo.write("\t".join(clean_sent) + "\n")  # print to parses file
                                    fo.write("\t".join(clean_pos) + "\n")  # CRFAE needs POS tags twice
                                    fo.write("\t".join(clean_pos) + "\n")  # CRFAE needs POS tags twice
                                    fo.write("\t".join(clean_heads) + "\n\n")
                                    num_parses += 1

                                # reset arrays
                                sentence = []
                                pos_list = []
                                heads_list = []

                            # Links are still being processed
                            else:
                                if lower_caps:
                                    line = line.lower()
                                split_line = line.split('\t')
                                sentence.append(split_line[1])  # build sentence array
                                pos_list.append(split_line[3])
                                heads_list.append(split_line[6])

    print(f"Converted a total of {num_parses} parses with len <= {max_length}")


if __name__ == "__main__":
    main(sys.argv[1:])
