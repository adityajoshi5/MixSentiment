import re
def tokenize(sentence, minchars=2):
    tokens = []
    for t in re.findall("[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+",sentence.lower()):
        if len(t)>=minchars:
            tokens.append(t)
    return tokens

VOWELS = ['a', 'e', 'i', 'o', 'u']
def removeVovels(string):
    return ''.join([l for l in string.lower() if l not in VOWELS])

if __name__ == '__main__':
    pass

def normalize_matrix(matrix):
    pass


