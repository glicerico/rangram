#!/usr/bin/env python
# coding=utf-8
# runs on python3

import sys
import os.path


def main(argv):
    sentence = ['ROOT']
    link_ids = []
    links = []

    with open(argv[0], 'r') as fi:
        with open(argv[0] + ".ull", 'w') as fo:
            lines = fi.readlines()
            for line in lines:
                if line == "\n":
                    for link in link_ids:
                        links.append(link[0] + " " + sentence[int(link[0])] + " " + link[1] + " " + sentence[int(link[1])])
                    fo.write(" ".join(sentence[1:]) + "\n")
                    links.sort()
                    fo.write("\n".join(links) + "\n\n")
                    # reset arrays
                    sentence = ['ROOT']
                    link_ids = []
                else:
                    split_line = line.split('\t')
                    link_ids.append([split_line[6], split_line[0]])  # store links indexes
                    sentence.append(split_line[1])  # form sentence


if __name__ == "__main__":
    main(sys.argv[1:])
