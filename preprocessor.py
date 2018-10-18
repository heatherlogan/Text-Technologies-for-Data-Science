#!/usr/bin/env python
import sys
import re
from stemming.porter2 import stem

filename = sys.argv[1]
file = open(filename, 'r').readlines()
all_files = []

stopwords_file = open('stopwordsfile.txt', 'r').readlines()
stopwords = []
for word in stopwords_file:
    stopwords.append(word.strip())
    stopwords.append('id')
stopwords.append('text')
stopwords.append('headline')
stopwords = set(stopwords)


# returns a list of dictionary objects which are the original files by {doc number: text}
# and writes the preprocessed text to a txt file


def split_file():

    print("Splitting file")

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

    print("Finished splitting file")
    return newfile


# saves a preprocessed.txt file and keeps a list of dictionary elements r
# presenting documents to work on when  building indewx

if __name__=='__main__':

    pp_file = []

    print("Beginning preprocessing")

    f = open("preprocessed.txt", 'w')

    for document in split_file():

        # extract document number and tokenize, apply lowercase, remove stops and stem.
        docnumber = re.sub("[^0-9]", '', document[0])
        document.pop(0)
        text = ', '.join(document)
        text.replace('\n', '')
        tokenizedline = re.split('[\W]', text)
        tokenizedline = filter(None, tokenizedline)

        processed_text = []
        for word in tokenizedline:
            word = word.lower()
            if word not in stopwords and not word.isdigit():
                processed_text.append(stem(word))

        # Remove the document tags from text file.

        if 'headlin' in processed_text:
            processed_text.remove('headlin')
        if 'text' in processed_text:
            processed_text.remove('text')

        f.write(' '.join(processed_text))

    print('Finished preprocessing')
