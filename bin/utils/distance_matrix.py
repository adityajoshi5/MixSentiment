from gensim.corpora import Dictionary
from gensim import corpora
import MyNormalizer as Mytok
from gensim.models.word2vec import Word2Vec
from scipy.spatial import distance
import numpy
import fuzzywuzzy
from fuzzywuzzy import fuzz
import logging
import traceback
import pickle
from sklearn import preprocessing


class Distance_Matrix(object):
    """
    Process:-
    1. Constructor
    2. Call function to create that particular matrix
    """
    
    matrices = {}
    
    def __init__(self, sentences):
        '''
        Split tokens into words
        '''
        self.sentences = [Mytok.tokenize(s) for s in sentences]
        self.lower_sentences = [s.lower() for s in sentences]
        self.tokens = [Mytok.tokenize(l) for l in self.lower_sentences]
        self.dictionary = corpora.Dictionary(self.tokens)
        self.dictItems = dict(self.dictionary.items())
        self.revdictItems = dict (zip(self.dictItems.values(),self.dictItems.keys()))
    
    def get_dict_index(self, word):
        return self.revdictItems[word] 
    
    def get_word(self, index):
        return self.dictItems[index]   
        
    def create_word2vec_matrix(self, loadPath=False, savePath=False,verbose=False):
        if loadPath:
            #pickle load word2vec from disk
            pass
        else:
            w2vmodel = Word2Vec(self.tokens, size=100, window=5, min_count=2, workers=4) # These parameters should be changed for a larger corpus
        if savePath:
            # Save word2vec
            pass

        # Compute vector distance between each word pair in the dictionary
        allWords = self.dictItems.values()
        thismatrix = numpy.zeros(shape=(len(allWords), len(allWords)))
        for i in range(0, len(allWords)):
            thismatrix[i,i] = 1
            for j in range(i, len(allWords)):
                try:
                    d = distance.euclidean(w2vmodel[allWords[i]], w2vmodel[allWords[j]])
                except:
                    d = float(0)
                if verbose:
                    print allWords[i], allWords[j], d
                thismatrix[i,j] = d
                thismatrix[j,i] = d
        self.matrices["Word2Vec"] = thismatrix
        
        return True # True signifies successful completion
    
    def create_fuzzy_matrix(self, verbose=False, minDist=0.5):
        allWords = self.dictItems.values()
        thismatrix = numpy.zeros(shape=(len(allWords), len(allWords)))
        allWords = self.dictItems.values()
        thismatrix = numpy.zeros(shape=(len(allWords), len(allWords)))
        for i in range(0, len(allWords)):
            thismatrix[i,i] = 1
            for j in range(i, len(allWords)):
#                 d = pow(fuzz.ratio(allWords[i], allWords[j]), 2)/float(10000)
                d = fuzz.ratio(allWords[i], allWords[j])/float(100)
                if d<minDist:
                    d=0
                if verbose:
                    print allWords[i], allWords[j], d
                thismatrix[i,j] = d
                thismatrix[j,i] = d
        self.matrices["Fuzzy"] = thismatrix
        
        return True # True signifies successful completion
    
    def combine_matrices(self):
        """
        Add the scores in each matrix controlled by scores - list of weights for each matrix
        """
        allWords = self.dictItems.values()
        thismatrix = numpy.zeros(shape=(len(allWords), len(allWords)))
        for matrix in self.matrices:
            thismatrix = thismatrix + self.matrices[matrix]
        self.combined_matrix = thismatrix
        return thismatrix
            
    def word_vector(self, word):
        """
        Make sure you already have combined matrix
        """
        try:
            return self.combined_matrix [self.revdictItems[word]]
        except:
            traceback.print_exc()
            logging.error("Combine Matrix has not been created.")
            exit()
    
    def save(self, path):
        """
        Save the whole object
        """
        pickle.dump(self, path)
    
    
    def save_matrices(self, path):
        """
        Pickle dump matrices
        """
        pass
    
    def load_matrices(self, path):
        """
        Pickle load matrics and matrix names from a file
        """
        pass
        
     
if __name__ == '__main__':
    sent = ["Ye kya bakchodi hai", "ajeeb bakchodi hai ye", "sala bakchod"]
    dm = Distance_Matrix(sent)
    print dm.dictItems
    dm.create_fuzzy_matrix(verbose=False)
#     dm.create_word2vec_matrix(verbose=False)
    print dm.combine_matrices()
    print dm.word_vector("bakchodi")