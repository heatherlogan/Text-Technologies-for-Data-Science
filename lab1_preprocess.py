#!/usr/bin/env python
import sys
import re
import os
import itertools
from stemming.porter2 import stem
from nltk.corpus import stopwords


filename = os.path.abspath(os.path.join('collections', 'trec.sample.txt'))
file = open(filename, 'r').readlines()
stopwords = set(stopwords.words('english'))

def preprocess(f):

    with open("preprocessed.txt", 'w') as f:
        preprocessedfile = []
        for line in file:
            tokenizedline = re.split('[\W]', line)
            for word in tokenizedline:
                word = word.lower()
                if word not in stopwords:
                    preprocessedfile.append(stem(word))
        f.write(' '.join(preprocessedfile))
        print('finished')

if __name__ == '__main__':
    preprocess(file)

