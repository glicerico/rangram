#!/usr/bin/env python
# coding: utf-8

import numpy as np
import collections
import random

class GrammarSampler(object):
	"""
	Class to generate a random corpus from a given grammar
	"""
    def __init__(self, grammar, cumul_words):
    	"""
		Initialize class object. Takes:
		grammar:		dictionary of grammar classes with their connectors
		cumul_words:	cumulative distribution of words in each class
    	"""
        self.grammar = grammar
        self.word_dist = cumul_words
        self.word_dist = np.insert(self.word_dist, 0, 0) # help to select words
        self.counter = 0
        self.links = {}
        self.sentence = None
        self.flatTree = None
        self.ullParse = None
        self.ullLinks = []
        
    def ReturnPos(self, word_string):
        """
        Given a word string, find its position in the tree
        """
        split_word = word_string.split("_")
        word_tuple = (int(split_word[2]), int(split_word[1]))
        return self.flatTree.index(word_tuple)

    def GenerateParse(self):
        """
        Generate a lexical tree and return an its corresponding sentence
        """
        # First generate a random tree
        tree_sample = self.GenerateTree()
        print(f"Tree:\n{tree_sample}")
        self.flatTree = list(self.Flatten(tree_sample))
        print(f"Flat tree: {self.flatTree}")
        
        # Obtain links from random tree
        self.ConstructLinks(tree_sample)
        sentence_array = np.full(len(self.flatTree), None) # initialize empty sentence array
        
        # Fill sentence array
        for key, value in self.links.items():
            key_pos = self.ReturnPos(key) # search for word-instance position in the tree
            sentence_array[key_pos] = key 
            for val in value:
                val_pos = self.ReturnPos(val)
                sentence_array[val_pos] = val
                self.ullLinks.append(f"{key_pos} {key} {val_pos} {val}")
                
        # Concatenate parse text output
        self.sentence = " ".join(sentence_array)
        self.ullParse = f"{self.sentence}\n" + "\n".join(self.ullLinks)
        print(f"Sentence: {self.sentence}")
        print(f"ULL parse: \n{self.ullParse}")
        
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
        Generate a random tree of class elements from the
        grammar, starting with the given class.
        """
        if self.counter == 0: # handle initial case
            node_class = rand.randint(0, len(self.grammar) - 1)
            print(f"Seed node_class: {node_class}")
            conjunct = rand.sample(self.grammar[node_class], 1)[0]
        else:
            # select one valid production of this class randomly
            conjunct = self.ChooseConjunct(connector, self.grammar[node_class])
            conjunct.remove(connector) # eliminate connector already used

        tree = [(self.counter, node_class)] # leaf tuple structure: (word_order, class)

        # for non-terminals, recurse
        for conn in conjunct:
            self.counter += 1
            new_node_class = list(conn)
            new_node_class.remove(node_class)
            # determine to insert subtree at beginning or end of current one
            insert_pos = len(tree) if conn.index(node_class) == 0 else 0
            tree.insert(insert_pos, self.GenerateTree(new_node_class[0], conn))
            
        return tree
    
    def SampleWord(self, pos, grammar_class):
        """
        Samples word from given grammar_class, and returns string in format
        "Wa_b_c", where a is the word number, b is the word class, c is word's position
        in the sentence
        """
        chosen_word = rand.randint(self.word_dist[grammar_class], self.word_dist[grammar_class + 1] - 1)
        word_string = "W" + str(chosen_word) + f"_{grammar_class}_" + str(pos)
        return word_string
        
    def ConstructLinks(self, tree):
        """
        Given a tree, store the links it contains in self.links
        """
        curr_word_class = [i for i in tree if isinstance(i, tuple)][0]
        curr_string = self.SampleWord(curr_word_class[0], curr_word_class[1]) # Samples word in string format
        
        # non-terminal case
        if len(tree) > 1:
            self.links[curr_string] = []
            tree.remove(curr_word_class)
            for subtree in tree:
                self.links[curr_string].append(self.ConstructLinks(subtree))
                
        return curr_string

