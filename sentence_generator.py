#!/usr/bin/env python
# coding: utf-8

import numpy as np
import collections
import random as rand
import re

class GrammarSampler(object):
    """
    Class to generate a random corpus from a given grammar
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
        self.counter = 0
        self.links = {}
        self.sentence = None
        self.flatTree = None
        self.ullParse = None
        self.ullLinks = []

    def GrammarParser(self, grammar_file):
        """
        Opens a given grammar file and parses both vocabulary
        and disjuncts from each class, then puts them in the 
        proper class variables.
        """
        with open("rand_grammar.txt", 'r') as fg:
            data = fg.readlines()

        # Read content in grammar file
        class_num = 0
        rules = {}
        for line in data:
            if re.search(r"^ *%", line):
                print("Comment")
            elif re.search(r"^.*: *$", line):
                self.word_dict[class_num] = line.split()[:-1] # parse vocabulary
                class_num += 1
            elif re.search(r"^.*; *$", line):
                rules[class_num] = line.split(" or ")[:-1]

        # Parse disjuncts
        for key, value in rules:
            terms = value[1:-1].split(" & ") # Remove "C" in each connector and separate them
            self.disj_dict[key] = tuple([tuple(term[1:].split("_")) for term in terms])

    def GenerateParse(self):
        """
        MAIN ENTRY POINT
        Generate a lexical tree and return its corresponding sentence
        """
        # Reset global variables
        self.counter = 0
        self.ullLinks = []
        self.links = {}

        # First generate a random tree
        tree_sample = self.GenerateTree()
        print(f"Tree:\n{tree_sample}")
        self.flatTree = list(self.Flatten(tree_sample))
        
        # Obtain links from random tree
        self.ConstructLinks(tree_sample)

        sentence_array = np.full(len(self.flatTree), None) # initialize empty sentence array
        
        # Fill sentence array
        for key, value in self.links.items():
            key_word, key_pos = self.ReturnPos(key) # search for word-instance position in the tree
            sentence_array[key_pos] = key_word
            for val in value:
                val_word, val_pos = self.ReturnPos(val)
                sentence_array[val_pos] = val_word
                if key_pos < val_pos:
                    self.ullLinks.append(f"{key_pos} {key_word} {val_pos} {val_word}")
                else:
                    self.ullLinks.append(f"{val_pos} {val_word} {key_pos} {key_word}")

        # Concatenate parse text output
        self.sentence = " ".join(sentence_array)
        self.ullLinks.sort()
        self.ullParse = f"{self.sentence}\n" + "\n".join(self.ullLinks)
        print(f"ULL parse: \n{self.ullParse}")

        return self.ullParse
        
    def ReturnPos(self, word_string):
        """
        Given a word string, find its position in the tree.
        Returns actual word, and its position in the sentence
        """
        split_word = word_string.split("_")
        word_tuple = (int(split_word[2]), int(split_word[1]))
        return split_word[0], self.flatTree.index(word_tuple)

    def Flatten(self, l): # taken from https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists
        """
        Given a list of nested lists, returns a flat structure in the same sequence.
        Useful to find the order of words in a sentence
        """
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes, tuple)):
                yield from self.Flatten(el)
            else:
                yield el    
    
    def ChooseConjunct(self, connector, disjunct):
        """
        Chooses a random conjunct from the ones in disjunct that contain connector
        """
        valid_conjs = [conj for conj in disjunct if connector in conj] # filters inappropriate connectors
        return list(rand.choice(valid_conjs))

    def GenerateTree(self, node_class = None, connector = ()):
        """ 
        Recursive method to generate a random tree of class elements from the
        grammar, starting with the given class.
        """
        if self.counter == 0: # handle initial case
            node_class = rand.randint(0, len(self.disj_dict) - 1)
            conjunct = rand.sample(self.disj_dict[node_class], 1)[0]
        else:
            # select one valid production of this class randomly
            conjunct = self.ChooseConjunct(connector, self.disj_dict[node_class])
            conjunct.remove(connector) # eliminate connector already used

        tree = [(self.counter, node_class)] # leaf tuple structure: (word_order, class)

        # for non-terminals, recurse
        for conn in conjunct:
            self.counter += 1
            new_node_class = list(conn)
            new_node_class.remove(node_class)
            # decide to insert subtree at beginning or end of current one
            insert_pos = len(tree) if conn.index(node_class) == 0 else 0
            tree.insert(insert_pos, self.GenerateTree(new_node_class[0], conn))
            
        return tree
    
    def SampleWord(self, pos, grammar_class):
        """
        Samples word from given grammar_class, and returns string in format
        "word_a_b", where a is the word class, b is word's position
        in the sentence
        """
        chosen_word = rand.choice(self.word_dict[grammar_class])
        word_string = chosen_word + f"_{grammar_class}_" + str(pos)
        return word_string
        
    def ConstructLinks(self, tree):
        """
        Iterative method to store links that given tree contains.
        Links are stored in self.links
        """
        # Every list has only one tuple in current level, and 0 or more lists. Find the tuple:
        curr_word_class = [i for i in tree if isinstance(i, tuple)][0]
        curr_string = self.SampleWord(curr_word_class[0], curr_word_class[1]) # Samples word in string format
        
        # non-terminal case
        if len(tree) > 1:
            self.links[curr_string] = []
            tree.remove(curr_word_class)
            for subtree in tree:
                self.links[curr_string].append(self.ConstructLinks(subtree))
                
        return curr_string
