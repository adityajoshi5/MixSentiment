from distances.distance_matrix import Distance_Matrix
import normalization.MyNormalizer as Mytok
import numpy
from sklearn.svm import SVC
from sklearn import preprocessing
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics.metrics import confusion_matrix
from normalization import RuleBasedNormalizer, MyNormalizer
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.lda import LDA

def visualize2D(data):
    from matplotlib.mlab import PCA as mlabPCA
    import matplotlib.pyplot as plt
    mlab_pca = mlabPCA(data.T)
 
    plt.plot(mlab_pca.Y[:,0],mlab_pca.Y[:,1], 'o', markersize=7,\
            color='blue', alpha=0.5, label='class1')
    
    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.xlim([-1,1])
    plt.ylim([-1,1])
    plt.legend()
    plt.title('Transformed samples with class labels from matplotlib.mlab.PCA()')
    
    plt.show()


def getFeatures(sentence, distance_mat, verbose=False):
    returnable = numpy.array([0]*len(distance_mat.dictionary))
    sentence = Mytok.tokenize(sentence)
    for word in sentence:
        thisWordVector = distance_mat.word_vector(word)
        returnable = numpy.add(returnable, thisWordVector)
#     returnable = returnable/len(sentence)   ### Think more about it - sentence length normalization etc
    if verbose:
        print returnable
    return returnable

def accuracy(original, predicted):
    scores = confusion_matrix(original, predicted)
    print scores
    print numpy.trace(scores)/float(numpy.sum(scores))
    

def train_validate(filename, test_ratio=0.3):
    numpy.set_printoptions(threshold=numpy.nan)
    filetext = [l.strip().split('\t') for l in open(filename, 'r').readlines()]
    lines = [l[0] for l in filetext]
#     lines = [RuleBasedNormalizer.removeVovels(l[0]) for l in filetext]
    data = []
    labels = [int(l[1]) for l in filetext]
    
    dm = Distance_Matrix(lines)
    dm.create_fuzzy_matrix(minDist=0.9)
#     dm.create_word2vec_matrix()
    dm.combine_matrices()
       
    for l in lines:
        data.append(  getFeatures(l, dm)  )
    data = preprocessing.normalize(data, axis=0)
#     data = MyNormalizer.normalize_matrix(data)    
    data = numpy.asarray(data)
    
     
    f = open("temp.txt", "w")
    for row in data:
        f.write(str(row.tolist()) + "\n")
    f.close()
    
    split = int(test_ratio*data.shape[0])
    training_data = data[:-split]
    training_labels = labels[:-split]
    test_data = data[-split:]
    # New try : Fisher LDA before training
    clf = LDA()
    clf.fit(training_data, training_labels)
    training_data = clf.transform(training_data)
    test_data = clf.transform(test_data)
    
    lab = labels[-split:]
    
    print "Training SVM"
    clf = OneVsRestClassifier(SVC())
    clf.fit(numpy.array(training_data), numpy.array(training_labels)) 
    pre = clf.predict(test_data)
    accuracy(lab, pre)
    
    print "Training GNB"
    clf = OneVsRestClassifier(GaussianNB())
    clf.fit(numpy.array(training_data), numpy.array(training_labels)) 
    pre = clf.predict(test_data)
    accuracy(lab, pre)    

    print "Training MNB"
    clf = MultinomialNB()
    clf.fit(numpy.array(training_data), numpy.array(training_labels)) 
    pre = clf.predict(test_data)
    accuracy(lab, pre)    
    
    print "Training Forest"
    clf = RandomForestClassifier()
    clf.fit(numpy.array(training_data), numpy.array(training_labels)) 
    pre = clf.predict(test_data)
    accuracy(lab, pre)
    
    print "Logistic Regression"
    clf = LogisticRegression()
    clf.fit(numpy.array(training_data), numpy.array(training_labels)) 
    pre = clf.predict(test_data)
    accuracy(lab, pre)
    
if __name__ == '__main__':
#     train_validate("../data/mittal/all.txt")
    train_validate("../data/mittal/small")