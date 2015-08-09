VOWELS = ['a', 'e', 'i', 'o', 'u']
def removeVovels(string):
    return ''.join([l for l in string.lower() if l not in VOWELS])

def adjustVovels(string):
    return ''.join([l for l in string.lower() if l not in VOWELS])

def removeH(string):
    return string


if __name__ == '__main__':
    testdata = open('../data/mittal/abpnews_comments.txt').readlines()
    for line in testdata:
        print line.strip()
        print removeVovels(line).strip()
        print ''
