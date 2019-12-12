#!/usr/bin/env python
# coding=utf-8
# runs on python3

import sys
import os

ROOT_WORD = "###LEFT-WALL###"
IGNORED_WORD = "###PUNCTUATION###"
IGNORED_FLAG = -1


def tag_punctuation(sentence, pos_list):
    """
    Remove punctuation tokens, guided by the tags in the conll file
    """
    tagged_len = 0
    num_punctuations = 0  # count how many tokens are punctuation
    tagged_sentence = []
    tagged_pos = []
    mapping = []

    for cnt, word in enumerate(sentence):
        if pos_list[cnt] not in ['p', 'punct']:  # non-punctuation token
            tagged_sentence.append(word)
            tagged_pos.append(pos_list[cnt])
            mapping.append(cnt - num_punctuations)
            tagged_len += 1
        else:  # punctuation token
            tagged_sentence.append(IGNORED_WORD)
            tagged_pos.append(IGNORED_WORD)
            num_punctuations += 1
            mapping.append(IGNORED_FLAG)

    return tagged_sentence, tagged_len, mapping


def create_links(sentence, mapping, link_ids):
    """
    Create links with correct numbering after punctuation removal
    """
    links = []
    for link in link_ids:
        link.sort()
        mapped_ll = mapping[link[0]]  # mapped ids (adjusting for removed punctuation)
        mapped_rl = mapping[link[1]]  # mapped ids (adjusting for removed punctuation)
        if mapped_rl != IGNORED_FLAG and mapped_ll != IGNORED_FLAG:  # discard links with punctuation
            links.append(str(mapped_ll) + " " + sentence[link[0]] + " " + str(mapped_rl) + " " + sentence[link[1]])

    links.sort()
    return links


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
    sentence = [ROOT_WORD]
    pos_list = ['ROOT']  # List with POS for each word, to detect punctuation
    link_ids = []  # List with word ids for each link

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
                            # Process parse when newline is found
                            if line == "\n":
                                if punct_flag:  # Punctuation removal is an option
                                    tagged_sent, tagged_len, mapping = tag_punctuation(sentence, pos_list)
                                else:
                                    tagged_sent = sentence
                                    tagged_len = len(sentence) - 1  # Do not count ROOT_WORD
                                    mapping = [i for i in range(len(sentence))]

                                # Only print sentences within desired length
                                if 0 < tagged_len <= max_length:
                                    clean_sent = [word for word in tagged_sent[1:] if word != IGNORED_WORD]
                                    clean_pos = [pos for pos in tagged_pos[1:] if pos != IGNORED_WORD]
                                    clean_heads = [head for head in tagged_heads[1:] if head != IGNORED_WORD]
                                    fc.write(" ".join(clean_sent) + "\n\n")  # print to corpus file
                                    fo.write("\t".join(clean_sent) + "\n")  # print to parses file
                                    fo.write("\t".join(clean_pos) + "\n")  # CRFAE needs POS tags twice
                                    fo.write("\t".join(clean_pos) + "\n")  # CRFAE needs POS tags twice
                                    fo.write("\t".join(clean_heads) + "\n")
                                    num_parses += 1

                                # reset arrays
                                sentence = [ROOT_WORD]
                                link_ids = []
                                pos_list = ['ROOT']

                            # Links are still being processed
                            else:
                                if lower_caps:
                                    line = line.lower()
                                split_line = line.split('\t')
                                # store ordered links indexes
                                link_ids.append([int(split_line[6]), int(split_line[0])])
                                pos_list.append(split_line[3])
                                sentence.append(split_line[1])  # build sentence array

    print(f"Converted a total of {num_parses} parses with len <= {max_length}")


if __name__ == "__main__":
    main(sys.argv[1:])
