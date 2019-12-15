#!/usr/bin/env python
# coding=utf-8
# runs on python3

import sys
import os

ROOT_WORD = "###LEFT-WALL###"
IGNORED_WORD = "###PUNCTUATION###"
IGNORED_FLAG = -1

from itertools import zip_longest


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def build_links(sentence, heads):
    """
    Build links from sentence and heads list
    """
    links = []
    for cnt, word in enumerate(sentence[1:]):
        hi = int(heads[cnt])  # head index
        hw = sentence[hi]  # head word
        if hi < cnt + 1:
            links.append(" ".join([str(hi), hw, str(cnt + 1), word]))
        else:
            links.append(" ".join([str(cnt + 1), word, str(hi), hw]))

    links.sort()
    return links


def main(argv):
    """
    Transforms dependency parses in CRFAE format to ULL format

    Usage: python crfae2ull.py <dirpath> <max_length>

    dirpath:            (str) Directory path with CRFAE files
    max_length:         (int) Ignore sentences longer than this parameter
    """

    if len(argv) != 2:
        print("Usage: python conll2ull.py <dirpath> <max_length>")

    dirpath = argv[0]
    max_length = int(argv[1])  # max length of sentences to process after punctuation removal (if any)
    print(f"\nProcessing files in {dirpath}\nmax_length={max_length}\n")

    num_parses = 0  # Num of parses in output file
    sentence = [ROOT_WORD]

    # Build directory structure for converted corpus parses
    newdir = dirpath + '_ull_' + str(max_length) + '/'
    if not os.path.isdir(newdir):
        os.mkdir(newdir)
        os.mkdir(newdir + 'GS')
        os.mkdir(newdir + 'corpus')

    for crfae_filename in os.scandir(dirpath):
        if crfae_filename.path.endswith('.crfae') and crfae_filename.is_file():
            with open(crfae_filename, 'r') as fi:
                with open(newdir+'GS/'+crfae_filename.name + ".txt.ull", 'w') as fo:
                    with open(newdir+'corpus/'+crfae_filename.name + ".txt", 'w') as fc:
                        for lines in grouper(fi, 5, ''):
                            assert len(lines) == 5
                            sentence.append(lines[0].split('\t'))
                            sent_len = len(sentence) - 1  # Do not count ROOT_WORD
                            heads = lines[3].split('\t')

                            # Only print sentences within desired lengths
                            if 0 < sent_len <= max_length:
                                links = build_links(sentence, heads)
                                fc.write(" ".join(sentence) + "\n\n")  # print to corpus file
                                fo.write(" ".join(sentence) + "\n")  # print to parses file
                                fo.write("\n".join(links) + "\n\n")
                                num_parses += 1

                                # reset arrays
                                sentence = [ROOT_WORD]

    print(f"Converted a total of {num_parses} parses with len <= {max_length}")


if __name__ == "__main__":
    main(sys.argv[1:])
