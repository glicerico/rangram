#!/usr/bin/env python
# coding: utf-8

# Class to generate random sentences from a given grammar.
# Based on CFG sentence generator at:
# https://eli.thegreenplace.net/2010/01/28/generating-random-sentences-from-a-context-free-grammar

import numpy as np
import collections
import random as rand
import re


class GrammarSampler(object):
    """
    Class to generate a random sentence and parse from a given grammar
    """

    def __init__(self, grammar_file):
        """
        Initialize class object. Takes:
        grammar:        dictionary of grammar classes with their connectors
        cumul_words:    cumulative distribution of words in each class
        """
        self.disj_dict = {}
        self.word_dict = {}
        self.GrammarParser(grammar_file)
        self.counter = 0  # tracks order of words generation
        self.links = {}
        self.sentence = None
        self.tree = []
        self.ullParse = None
        self.ullLinks = []

    def GrammarParser(self, grammar_file):
        """
        Opens a given grammar file and parses both vocabulary
        and disjuncts from each class, then puts them in the 
        proper class variables.
        """
        with open(grammar_file, 'r') as fg:
            data = fg.readlines()

        # Read content in grammar file
        class_num = 0
        rules = {}
        for line in data:
            line = re.sub(r"[)(\n]", "", line)  # remove all parenthesis and newlines
            if re.search(r"^[^%]*: *$", line):
                self.word_dict[class_num] = line.split()  # parse vocabulary
                self.word_dict[class_num][-1] = self.word_dict[class_num][-1].rstrip(':')  # remove final ":"
            elif re.search(r"^[^%]*; *$", line):
                rules[class_num] = line.split(" or ")
                rules[class_num][-1] = rules[class_num][-1].rstrip(';')  # remove final ";"
                class_num += 1

        # Parse disjuncts, following specific format as outputted by grammar_generator.py
        for key, value in rules.items():
            self.disj_dict[key] = []
            for conjunct in value:
                connectors = conjunct.split(" & ")
                conjunct_list = []
                for connector in connectors:
                    split_conn = connector.split("_")
                    conjunct_list.append((int(split_conn[0][1:]), int(split_conn[1][:-1])))
                self.disj_dict[key].append(conjunct_list)
            self.disj_dict[key] = tuple(self.disj_dict[key])

    def GenerateParse(self):
        """
        MAIN ENTRY POINT
        Generate a lexical tree and return its corresponding sentence and parse
        """
        # Reset global variables
        self.counter = 0
        self.ullLinks = []
        self.links = {}

        # First generate a random tree
        self.GenerateTree()

        sentence_array = np.full(len(self.tree), None)  # initialize empty sentence array

        # Fill sentence array
        for key, value in self.links.items():
            key_word, key_pos = self.ReturnPos(key)  # search for word-instance position in the tree
            sentence_array[key_pos - 1] = key_word
            for val in value:
                val_word, val_pos = self.ReturnPos(val)
                sentence_array[val_pos - 1] = val_word
                if key_pos < val_pos:
                    self.ullLinks.append(f"{key_pos} {key_word} {val_pos} {val_word}")
                else:
                    self.ullLinks.append(f"{val_pos} {val_word} {key_pos} {key_word}")

        # Concatenate parse text output
        self.sentence = " ".join(sentence_array)
        self.ullLinks.sort()
        sortedLinks = "\n".join(self.ullLinks)
        print(f"ULL parse: \n{self.sentence}\n{sortedLinks}\n")

        return self.sentence, sortedLinks

    def ReturnPos(self, word_string):
        """
        Given a word string, find its position in the tree.
        Returns actual word, and its position in the sentence
        """
        split_word = word_string.split("_")
        word_tuple = (int(split_word[2]), int(split_word[1]))
        return split_word[0], self.tree.index(word_tuple) + 1

    def ChooseConjunct(self, connector, disjunct):
        """
        Chooses a random conjunct from the ones in disjunct that contain connector
        """
        valid_conjs = [conj for conj in disjunct if connector in conj]  # filters inappropriate connectors
        return list(rand.choice(valid_conjs))

    def GenerateTree(self, node_class=None, connector=(), parent_size=0, node_pos=0):
        """
        Recursive method to generate a random tree of class elements from the
        grammar, starting with the given class.
        """
        if self.counter == 0:  # handle initial case
            node_class = rand.randint(0, len(self.disj_dict) - 1)  # choose random class to begin
            conjunct = rand.sample(self.disj_dict[node_class], 1)[0]  # choose random conjunct
            self.tree = [(self.counter, node_class)]
        else:  # select one valid production of this class randomly
            conjunct = self.ChooseConjunct(connector, self.disj_dict[node_class])

        parent_counter = self.counter # save it for link creation
        size_r = 0  # counts words inserted to the right by this call
        size_l = 0  # counts words inserted to the left by this call
        insert_pos_r = node_pos + 1
        insert_pos_l = node_pos

        # Insert word from new node, and recurse to expand the node
        for conn in conjunct:
            new_node_class = list(conn)
            new_node_class.remove(node_class)

            if conn == connector:  # don't insert if it's parent node; adjust insert_pos
                if conn.index(node_class) == 0:
                    insert_pos_r += parent_size
                else:
                    insert_pos_l -= parent_size
            else:
                self.counter += 1
                new_node = (self.counter, new_node_class[0])
                self.ConstructLink((parent_counter, node_class), new_node)  # store link
                # insert to right or left
                if conn.index(node_class) == 0:  # right
                    self.tree.insert(insert_pos_r, new_node)
                    size_r += 1
                    size_branch = self.GenerateTree(new_node_class[0], conn, size_r + size_l + parent_size, insert_pos_r)
                    size_r += size_branch  # add size of newly added branch
                else:  # left
                    self.tree.insert(insert_pos_l, new_node)
                    size_l += 1
                    size_branch = self.GenerateTree(new_node_class[0], conn, size_r + size_l + parent_size, insert_pos_l)
                    size_l += size_branch  # add size of newly added branch
                    insert_pos_r += 1 + size_branch  # correct position for added word and branch on left

        return size_r + size_l

    def SampleWord(self, pos, grammar_class):
        """
        Samples word from given grammar_class, and returns string in format
        "word_a_b", where a is the word class, b is word's position
        in the sentence
        """
        chosen_word = rand.choice(self.word_dict[grammar_class])
        word_string = chosen_word + f"_{grammar_class}_" + str(pos)
        return word_string

    def ConstructLink(self, parent_node, child_node):
        """
        Method to form an entry in self.links from a pair of connected nodes
        """
        # Sample words in string format
        parent_string = self.SampleWord(parent_node[0], parent_node[1])
        child_string = self.SampleWord(child_node[0], child_node[1])

        if parent_string not in self.links:
            self.links[parent_string] = []
        self.links[parent_string].append(child_string)

    def ConstructLinks(self, tree):
        """
        Iterative method to store links that given tree contains.
        Links are stored in self.links
        """
        # Every list has only one tuple in current level, and 0 or more lists. Find the tuple:
        curr_word_class = [i for i in tree if isinstance(i, tuple)][0]
        curr_string = self.SampleWord(curr_word_class[0], curr_word_class[1])  # Samples word in string format

        # non-terminal case
        if len(tree) > 1:
            self.links[curr_string] = []
            tree.remove(curr_word_class)
            for subtree in tree:
                self.links[curr_string].append(self.ConstructLinks(subtree))

        return curr_string
