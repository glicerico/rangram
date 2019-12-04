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
        lines = fi.readlines()
        for line in lines:
            if line == "\n":
                sentence = ['ROOT']
                for link in links_ids:
                    links.append(li + " " + sentence[li] + " " + split_line[0] + " " + split_line[1])
            else:
                split_line = line.split('\t')
                link_ids.append([split_line[6], split_line[0]])  # store links indexes
                sentence.append(split_line[1]) # form sentence


if __name__ == "__main__":
    main(sys.argv[1:])
