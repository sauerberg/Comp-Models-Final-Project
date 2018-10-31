"""
Loads associations into memory. Can be used to create both weighted and
unweighted matrices without and with unnormed targets.
"""

import numpy as np

class AssociationMatrix:
    def __init__(self):
        '''
        '''
        self.assocs = dict() # dict mapping string cues to lists of tuples: (string target, float strengths, bool normed)
        self.normed_items = [] # enumerating list of string normed words
        self.unnormed_items = [] # enumerating list of string unnormed words
        self.matrix = None # matrix of relations, indices match from items
        
    def load(self, filename):
        '''
        '''
        self.assocs.clear()
        self.items.clear()
        assoc_file = open(filename)
        
        print("Loading cue-target pairs from file: '{0}'".format(filename))
        i = 1
        for line in assoc_file:
            line_data = line.split(',')
            if len(line_data) < 5:
                print("EXCEPTION: Line {0} failed to load".format(i))
            # Load data fields 1, 2, 3, 4 and 5 (see USF free association norms: appendix A)
            cue, target = line_data[0].strip(), line_data[1].strip(), line_data[2].strip()
            normed = True if normed == "YES" else False
            fsg = float(line_data[4].strip()) / float(line_data[3].strip())
            # Add the data into self.assocs and the lists self.normed_items and self.unnormed_items
            self.normed_items.add(cue)
            if not normed:
                self.unnormed_items.add(target)
            target_list = self.assocs.setdefault(cue, [])
            self.assocs[cue] = target_list.add(tuple(target, fsg, normed))
            # Status messages; comment out if undesired
            if i % 10000 == 0:
                print("...{0} cue-target lines parsed...".format(i))
            i += 1
        np.sort(self.unnormed_items)
        print("Load complete: {0} cue-target lines parsed, yielding {1} total cues".format(i, len(self.assocs)))
    
    def init_matrix(self):
        '''
        '''
        self.matrix = np.zeros(tuple())

def createNormedBooleanMatrix(dict, normed_list, fileName="normedBooleanMatrix"):
    """
    Creates an nxn matrix where n is the number of cues and writes it to the given location
    The i,jth entry is 1 iff people produced target j when given cue i
    Only considers normed targets (targets that were tested as cues)
    Pickles the matrix and writes it to the given file
    :param dict: a dictionary mapping cues to 3-d tuples: the target word, the association strength, and whether the target is normed
    :param normed_list: a list of the cues
    :param fileName: the name of the file to write the pickled matrix to
    """
    matrix = np.zeros((len(normed_list), len(normed_list)), dtype=bool)
    for i in len(normed_list):
        for target in dict[normed_list[i]]:
            if target[2]:  # the target was normed
                matrix[i][normed_list.index(target[0])] = True
    file = open(fileName,'w')
    matrix.dump(file)


def createNormedStochaticMatrix(dict, normed_list, fileName="normedStochasticMatrix"):
    """
    Creates an nxn matrix where n is the number of cues and writes it to the given location
    The i,jth entry is the fraction of the time people produced target j when given cue i
    Only considers normed targets (targets that were tested as cues)
    Pickles the matrix and writes it to the given file
    :param dict: a dictionary mapping cues to 3-d tuples: the target word, the association strength, and whether the target is normed
    :param normed_list: a list of the cues
    :param fileName: the name of the file to write the pickled matrix to
    """
    matrix = np.zeros((len(normed_list), len(normed_list)), dtype=float)
    for i in len(normed_list):
        for target in dict[normed_list[i]]:
            if target[2]:  # the target was normed
                matrix[i][normed_list.index(target[0])] = target[1]

    # normalizes the entries of each row to sum to 1 to make it a stochastic matrix
    for row in matrix:
        sum = 0
        for col in row:
            sum += col
        for col in row:
            col = col / sum

    file = open(fileName,'w')
    matrix.dump(file)

def createFullBooleanMatrix(dict, normed_list, unnormed_list, fileName="fullBooleanMatrix"):
    """
    Creates an n+m square matrix where n and m are the length of the normed and unnormed lists
    The i,jth entry is 1 iff people produced target j when given cue i
    Pickles the matrix and writes it to the given file
    :param dict: a dictionary mapping cues to 3-d tuples: the target word, the association strength, and whether the target is normed
    :param normed_list: a list of the cues
    :param unnormed_list: a list of the responses produced that were never given as cues
    :param fileName: the name of the file to write the pickled matrix to
    """
    matrix = np.zeros((len(normed_list) + len(unnormed_list), len(normed_list) + len(unnormed_list)), dtype=float)
    for i in len(normed_list):
        for target in dict[normed_list[i]]:
            if target[2]:  # target is normed
                matrix[i][normed_list.index(target[0])] = True
            else:  # target not normed
                matrix[i][len(normed_list) + unnormed_list.index(target[0])] = True

    # give unnormed cues edges to every target
    for i in range(len(unnormed_list)):
        for j in range(len(normed_list) + len(unnormed_list)):
            if not i == j :  # node shouldn't have an out-edge to itself
                matrix[len(normed_list)][j] = True

    file = open(fileName,'w')
    matrix.dump(file)

def createFullStochasticMatrix(dict, normed_list, unnormed_list, fileName="fullStochasticMatrix"):
    """
    Creates an n+m square matrix where n and m are the length of the normed and unnormed lists
    The i,jth entry is the fraction of the time people produced target j when given cue i
    Pickles the matrix and writes it to the given file
    :param dict: a dictionary mapping cues to 3-d tuples: the target word, the association strength, and whether the target is normed
    :param normed_list: a list of the cues
    :param unnormed_list: a list of the responses produced that were never given as cues
    :param fileName: the name of the file to write the pickled matrix to
    """
    matrix = np.zeros((len(normed_list) + len(unnormed_list), len(normed_list) + len(unnormed_list)), dtype=float)
    for i in len(normed_list):
        for target in dict[normed_list[i]]:
            if target[2]:  # target is normed
                matrix[i][normed_list.index(target[0])] = target[1]
            else:  # target not normed
                matrix[i][len(normed_list) + unnormed_list.index(target[0])] = target[1]

    # give unnormed cues edges to every target. Weights will later be normalized to sum to 1
    for i in range(len(unnormed_list)):
        for j in range(len(normed_list) + len(unnormed_list)):
            if not i == j:  # node shouldn't have an out-edge to itself
                matrix[len(normed_list)][j] = 1

    # normalizes the entries of each row to sum to 1 to make it a stochastic matrix
    for row in matrix:
        sum = 0
        for col in row:
            sum += col
        for col in row:
            col = col / sum

    file = open(fileName,'w')
    matrix.dump(file)


