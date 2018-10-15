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

# saves a preprocessed.txt file and keeps a list of dictionary elements r
# presenting documents to work on when  building indewx


def preprocess():

    print("Beginning preprocess")
    f = open("preprocessed.txt", 'w')
    pp_file = []

    for document in split_file():
        docnumber = re.sub("[^0-9]", '', document[0])
        document.pop(0)
        text = ', '.join(document)
        text.replace('\n', '')
        tokenizedline = re.split('[\W]', text)
        tokenizedline = filter(None, tokenizedline)

        processed_text = []
        for word in tokenizedline:
            word = word.lower()
            if word not in stopwords:
                processed_text.append(stem(word))

        if 'headlin' in processed_text:
            processed_text.remove('headlin')
        if 'text' in processed_text:
            processed_text.remove('text')

        document = {}
        document[docnumber] = processed_text
        pp_file.append(document)
        f.write(' '.join(processed_text))
    print('finished preprocessing')
    return pp_file



# fix to keep numbers
def get_unique_terms():
    pp_words = open('preprocessed.txt', 'r').read()
    unique_terms = [x for x in (list(set(pp_words.split(' ')))) if not (x.isdigit() or x[0] == '-' and x[1:].isdigit())]
    unique_terms.sort()
    return unique_terms



def build_index(preprocessed_file, terms):
    print("Beginning building index")
    inverted_index = []
    #loop through each term
    for term in terms:
        all_positions = []
        print("Building for term: {}".format(term))
        for document in preproccessed_file:
            for docno in document:
                words = (document[docno])
                i = 0
                pos = []
                for word in words:
                    i += 1
                    position = {}
                    if term == word:
                        match = i
                        pos.append(match)
                        position[docno] = pos

                        if position not in all_positions:
                            all_positions.append(position)

                            index = {}
                            index[term] = all_positions

                            if index not in inverted_index:
                                inverted_index.append(index)
    print("Finished building index")
    return inverted_index


def print_and_save(inv_index):

    print("Beginning formatting")

    f = open('indexed.txt', 'w')
    for index in inv_index:
        for term,indexes in index.items():
            f.write("{}:\n".format(term))
            print("{}:".format(term))
            for position in indexes:
                for docno,pos in position.items():
                    pos = (','.join(map(str, pos)))
                    f.write("\t{}: {}\n".format(docno, pos))
                    print("\t{}: {}".format(docno, pos))
            f.write('\n')
            print('')
    print('*****finished******')


if __name__=='__main__':

    preproccessed_file = preprocess()
    terms = get_unique_terms()
    inverted_index = build_index(preproccessed_file, terms)
    print_and_save(inverted_index)