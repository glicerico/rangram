#!/usr/bin/env python
# coding: utf-8

# Class to generate random sentences from a given grammar.
# Based on CFG sentence generator at:
# https://eli.thegreenplace.net/2010/01/28/generating-random-sentences-from-a-context-free-grammar

import numpy as np
import random as rand
import re


class Grammar:
    """
    Class containing a link-parser grammar
    """
    def __init__(self, grammar_file):
        """
        Initialize grammar. Reads grammar from Link Grammar-formatted file.
        :param grammar_file:
        """
        self.disj_dict = {}
        self.word_dict = {}
        self.grammar_parser(grammar_file)

    def set_disj_dict(self, disj_dict):
        self.disj_dict = disj_dict

    def get_disj_dict(self):
        return self.disj_dict

    def set_word_dict(self, word_dict):
        self.word_dict = word_dict

    def grammar_parser(self, grammar_file):
        """
        Opens a given grammar file and parses both vocabulary
        and disjuncts from each class, then puts them in the
        proper class variables.
        """
        with open(grammar_file, 'r') as fg:
            data = fg.readlines()

        # Read content in grammar file
        # File format is very specific:
        # a) All comments start with % or <
        # b) For each rule, vocabulary comes in a single line, which ends in colon.
        # c) Rules come in a single line, which ends in semi-colon, and each rule has
        # to be an explicit conjunction of connectors, surrounded by parenthesis or not. "&" operator has priority
        # over "or" operator.
        class_num = 0
        rules = {}
        for line in data:
            line = re.sub(r"[)(\n]", "", line)  # remove all parenthesis and newlines
            if re.search(r"^[^%<]*: *$", line):  # Lines that contain vocabulary list
                line = re.sub(r"\"", "", line)  # remove all quotes from vocabulary
                self.word_dict[class_num] = line.split()  # parse vocabulary
                self.word_dict[class_num][-1] = self.word_dict[class_num][-1].rstrip(':')  # remove final ":"
            elif re.search(r"^[^%<]*; *$", line):  # Lines that contain rules list
                rules[class_num] = line.split(" or ")
                rules[class_num][-1] = rules[class_num][-1].rstrip(';')  # remove final ";"
                class_num += 1

        # Parse disjuncts. The file format must show a disjunction of explicit conjunctions (no short-hand notation)
        # E.g.  (AB+ & CD-) or (CD-) or (CD- & AE+ & AB+);
        for key, value in rules.items():
            self.disj_dict[key] = [conn.split(" & ") for conn in value]


class GrammarSampler:
    """
    Class to generate a random sentence and parse from a given grammar
    """
    def __init__(self, grammar):
        """
        Initialize class object. Takes a grammar object.
        """
        self.disj_dict = grammar.disj_dict  # Local rules dictionary
        self.word_dict = grammar.word_dict  # Local vocab dictionary
        self.counter = 0  # tracks order of words generation
        self.links = {}
        self.sentence = None
        self.tree = []
        self.ull_parse = None
        self.ull_links = []

    def generate_parse(self, starting_node=None, starting_rule=None):
        """
        MAIN ENTRY POINT
        Generate a lexical tree and return its corresponding sentence and parse
        :param: starting_node:  Node to start the parse tree
        """
        # Reset global variables
        self.counter = 0
        self.ull_links = []
        self.links = {}

        # First generate a random tree, with optional starting node
        self.generate_tree(node_class=starting_node, rule=starting_rule)

        sentence_array = np.full(len(self.tree), None)  # initialize empty sentence array

        # Fill sentence array, and create links output in ULL format
        for key, value in self.links.items():
            key_word, key_pos = self.return_pos(key)  # search for word-instance position in the tree
            sentence_array[key_pos - 1] = key_word
            for val in value:
                val_word, val_pos = self.return_pos(val)
                sentence_array[val_pos - 1] = val_word
                # Fill in the links in ULL format
                if key_pos < val_pos:
                    self.ull_links.append(f"{key_pos} {key_word} {val_pos} {val_word}")
                else:
                    self.ull_links.append(f"{val_pos} {val_word} {key_pos} {key_word}")

        # Concatenate parse text output
        self.sentence = " ".join(sentence_array) + "."  # Add final punctuation, better for BERT
        self.ull_links.sort()
        sorted_links = "\n".join(self.ull_links)
        print(f"ULL parse: \n{self.sentence}\n{sorted_links}\n")

        return self.sentence, sorted_links

    def return_pos(self, word_string):
        """
        Given a word string, find its position in the tree.
        Returns actual word, and its position in the sentence
        """
        split_word = word_string.split("_")
        word_tuple = (int(split_word[2]), int(split_word[1]))
        return split_word[0], self.tree.index(word_tuple) + 1

    @staticmethod
    def choose_conjunct(connector, disjunct):
        """
        Chooses a random conjunct from the ones in disjunct that contain connector
        """
        valid_conjs = [conj for conj in disjunct if connector in conj]  # filters inappropriate connectors
        return list(rand.choice(valid_conjs))

    def generate_tree(self, node_class=None, rule=None, connector=(), parent_size=0, node_pos=0):
        """
        Recursive method to generate a random tree of class elements from the
        grammar, starting with the given class and rule.
        """
        if self.counter == 0:  # handle initial case
            if node_class is None:
                node_class = rand.randint(0, len(self.disj_dict) - 1)  # choose random class to begin
            if rule is None:
                rule = rand.sample(self.disj_dict[node_class], 1)[0]  # choose random rule
            self.tree = [(self.counter, node_class)]
        else:  # select one valid production of this class randomly
            rule = self.choose_conjunct(connector, self.disj_dict[node_class])

        parent_counter = self.counter  # save current counter for link creation
        size_r = 0  # words inserted to the right by this call of method
        size_l = 0  # words inserted to the left by this call of method
        insert_pos_r = node_pos + 1  # position to insert on the right of current node
        insert_pos_l = node_pos  # position to insert on the left of current node

        # Insert new node, and recurse to expand the node
        for conn in rule:
            new_node_class = list(conn)
            new_node_class.remove(node_class)  # obtain which other class is linked

            if conn == connector:  # don't insert if conn is parent node; and adjust insert_pos
                if conn.index(node_class) == 0:
                    insert_pos_r += parent_size
                else:
                    insert_pos_l -= parent_size
            else:
                self.counter += 1
                new_node = (self.counter, new_node_class[0])
                self.construct_link((parent_counter, node_class), new_node)  # store link
                # insert to right or left and recurse
                if conn.index(node_class) == 0:  # right
                    self.tree.insert(insert_pos_r, new_node)
                    size_r += 1
                    size_branch = \
                        self.generate_tree(node_class=new_node_class[0], connector=conn,
                                           parent_size=size_r + size_l + parent_size, node_pos=insert_pos_r)
                    size_r += size_branch  # add size of newly added branch
                else:  # left
                    self.tree.insert(insert_pos_l, new_node)
                    size_l += 1
                    size_branch = \
                        self.generate_tree(node_class=new_node_class[0], connector=conn,
                                           parent_size=size_r + size_l + parent_size, node_pos=insert_pos_l)
                    size_l += size_branch  # add size of newly added branch

                insert_pos_r += 1 + size_branch  # update for added word and branch

        return size_r + size_l  # return num of added words by current iteration

    def sample_word(self, pos, grammar_class):
        """
        Samples word from given grammar_class, and returns string in format
        "word_a_b", where a is the word class, b is word's position
        in the sentence
        """
        chosen_word = rand.choice(self.word_dict[grammar_class])
        word_string = chosen_word + f"_{grammar_class}_" + str(pos)
        return word_string

    def construct_link(self, parent_node, child_node):
        """
        Method to form an entry in self.links from a pair of connected nodes
        """
        # Sample words in string format
        parent_string = self.sample_word(parent_node[0], parent_node[1])
        child_string = self.sample_word(child_node[0], child_node[1])

        if parent_string not in self.links:
            self.links[parent_string] = []
        self.links[parent_string].append(child_string)

