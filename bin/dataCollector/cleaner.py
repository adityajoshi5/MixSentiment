import re
from string import atoi
import math
from random import shuffle
import random

_dataset_folder = "../../Dataset/"

englishwords = set([x.strip() for x in open('english.txt','r').readlines()])
stopwords = set([x.strip() for x in open('stopwords.txt','r').readlines()])
personname_regex = "[A-Z][a-z]+[\s\,\.][A-Z][a-z]+[\s\,\.]"

def make_tsv_line(contents):
    # contents might be tuple or list. make it a single string separated by tabs and \n
    return "\t".join([str(x) for x in contents])+"\n"

def contains_names(sentence):
    # regex to return how many name-like appearences exist
    name_matches = re.findall(personname_regex, sentence)
    capstyle_matches = re.findall("[A-Z][a-z]", sentence)
    return name_matches, capstyle_matches

def mixcode_score(sentence):
    
    lowersentence = sentence.lower()
    words = re.compile("([\w][\w]*'?\w?)").findall(lowersentence)
    englishmatch = set(words).intersection(set(englishwords))
    stopmatch = set(words).intersection(set(stopwords))
    nonmatch = set(words) - set(englishwords)
    names, capWords = contains_names(sentence)
    
    E = len(englishmatch)
    W = len(words)
    N = len(capWords)
    S = len(stopmatch)
    UNKN = sentence.count('?')
    CHAR = len(sentence)
    if W<3:
        return 0
    
    noeng = (W-E)/float(W)
    nonam  = (W-N)/float(W)
    nostp = (W-S)/float(W)
    unkrat = (CHAR-UNKN)/float(CHAR)
    
    score = noeng * nonam * nostp* unkrat 
    return score
    
def add_to_main_dataset(dataset_folder, coming_post_file, coming_comment_file, check_score=True):
    _indexfile = dataset_folder+"index.dat"
    _mainfile = dataset_folder+"mainn.dat"
    _annotablefile = dataset_folder+"annotable.dat"
    _counterfile = dataset_folder+"counter.dat"
    
    # Load counter value
    cfil = open(_counterfile, 'r').readlines()
    ind_key = int(cfil[0].strip()) + 1
    mainn_key =  int(cfil[1].strip()) + 1
    anno_key = int(cfil[2].strip()) + 1
    
    # Open reading file handles
    inpost = open(coming_post_file, 'r') 
    incomm = open(coming_comment_file, 'r')
    
    # Open writable file handles
    index = open(_indexfile, 'a')
    mainn = open(_mainfile, 'a')
    annotable = open(_annotablefile, 'a')
    '''
    ANNOTATION SCHEMA :
    message, annoID, indexID, rawFile, rawFileRow, rawFileID
    
    INDEX SCHEMA : 
    indKey, type, rawFile, annoFile, rawFileRow, rawFileKey, annoFileRow, annoFileKey, mainnFileKey
    '''
    i=0
    for line in inpost.readlines():
        lineparts = line.strip().split('\t')
        mainn.write(str(mainn_key)+"\t"+line)
        index.write(make_tsv_line((ind_key, 'POSTS', coming_post_file ,'NOANNO', i, lineparts[0], 'NOANNO', 'NOANNO', mainn_key)))
        mainn_key+=1
        ind_key+=1
        i+=1
    i=0
    j=0
    print "Writing Comments"
    for line in incomm.readlines():
        lineparts = line.strip().split('\t')
        score = mixcode_score(lineparts[2])
        mainn.write(str(mainn_key)+"\t"+line)
#         print score, lineparts[2]
        if score<0.4:
            # indKey, type, rawFile, annoFile, rawFileRow, rawFileKey, annoFileRow, annoFileKey, mainnFileKey
            index.write(make_tsv_line(( ind_key, 'COMMENTS', coming_comment_file, "LOWSCORE", i, lineparts[0], 'LOWSCORE', 'LOWSCORE', mainn_key)))
        
        else:
            # message, annoID, indexID, rawFile, rawFileRow, rawFileID
            annotable.write(make_tsv_line((lineparts[2], anno_key, ind_key, coming_comment_file, i, lineparts[0])))
            # indKey, type, rawFile, annoFile, rawFileRow, rawFileKey, annoFileRow, annoFileKey, mainnFileKey
            index.write(make_tsv_line((ind_key, 'COMMENTS', coming_comment_file, _annotablefile, i, lineparts[0], j, anno_key, mainn_key)))
            anno_key+=1
            j+=1
            
            
        mainn_key+=1
        ind_key+=1
        i+=1
    
    
    
    # Close all handles    
    index.close()
    mainn.close()
    annotable.close()
    
    # Update counter value
    cfil = open(_counterfile, 'w')
    cfil.write(str(ind_key)+"\n"+str(mainn_key)+"\n"+str(anno_key))
    cfil.close()
    
def remove_long_rows(annotationfilepath, outputannotationfilepath):
    lines = open(annotationfilepath).readlines()
    writable = []
    linesread = set()
    counter=0
    for l in lines:
        parts = l.split('\t')
        this_sentence = parts[0]  
        if len(this_sentence.split(' ')) <50 and len(this_sentence.split(' '))>7:
            if not this_sentence.lower() in linesread:
                linesread.add(this_sentence.lower())
                writable.append(  '\t'.join(parts)  )
                counter+=1
        if len(this_sentence.split(' ')) <= 7:
            randno = random.random()
            if randno > 0.6:
                if not this_sentence.lower() in linesread:
                    linesread.add(this_sentence.lower())
                    writable.append(  '\t'.join(parts)  )
                    counter+=1
           
    import numpy as np    
    np.random.shuffle(writable)
    outfile = open(outputannotationfilepath, 'w')
    outfile.writelines(writable)
    outfile.close()

def main():
#     com = "../../NewData/BeingSalmanKhan_comment_07_17_18_03.txt"
#     post= "../../NewData/BeingSalmanKhan_post_07_17_18_03.txt"
#     add_to_main_dataset(_dataset_folder, post,com )
    remove_long_rows("../../Dataset/annotable.dat", "../../Dataset/pranjal_annotations.dat")

if __name__ == '__main__':
    main()