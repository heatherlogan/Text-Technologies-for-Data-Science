import os
import sys
import re
from stemming.porter2 import stem
from nltk.corpus import stopwords

filename = os.path.abspath(os.path.join('collections', 'trec.sample.txt'))
file = open(filename, 'r').readlines()

pp_filename = 'preprocessed.txt'
pp_file = open(pp_filename, 'r').read()

def get_unique_words():
    def remove_headings(words):
        newwords = []
        for i in words:
            if not i.isdigit() and i != 'id' and i != 'text' and i != 'headline':
                newwords.append(i)
        return newwords
    return list(set(remove_headings(pp_file.split(" "))))


# split original file into documents into [[id, headline, text]] or [[id, text]
def split_file():
    file_pos = []
    for item in file:
        if re.match('^ID:', item):
            file_pos.append(file.index(item))
    file_pos.append(len(file))
    positions = ([file_pos[i:i + 2] for i in range(len(file_pos) + 1 - 2)])
    newfile = []
    for i in positions:
        [a, b] = i
        newfile.append(file[a:b])
    return newfile



def split2():
    texts, words = {}
    for item in file:
        if re.match('^ID:', item):
            texts


def do():
    file = split_file()
    f = open("indexed.txt", 'w')

    for word in get_unique_words():
        print(word)
        f.write(word + ":\n")

        for line in file:
            for l in line:
                if l.startswith('TEXT') or l.startswith('HEADLINE'):
                    doc_index = [i + 1 for i, x in enumerate(((re.sub(r'([^\s\w]|_)+', '',
                                                                         l.replace("TEXT: ", ""))).lower().strip()).split(' '))
                                 if (x == word or stem(x) == stem(word))]
                    if not len(doc_index) == 0:
                        docnumber = re.sub("[^0-9]", "", line[0])
                        f.write("       {}: ".format(docnumber) +
                                ','.join(str(v) for v in doc_index) +"\n")
                        print("       {}: ".format(docnumber) + ','.join(str(v) for v in doc_index) )






