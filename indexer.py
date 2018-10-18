import itertools
import re
import sys
from stemming.porter2 import stem


def sort_stopwords():

    # Converts the stopwords file into a list and appends 'id', 'text' and 'headline' as stopwords so these aren't
    # considered in the inverted index

    stopwords_file = open('stopwordsfile.txt', 'r').readlines()
    stopwords = []

    for word in stopwords_file:
        stopwords.append(word.strip())

    stopwords.append('id')
    stopwords.append('text')
    stopwords.append('headline')
    return set(stopwords)


def split_file(file_name):

    # splits each document into string lists [doc_id, text, text .. ] for easier preprocessing

    file = open(file_name, 'r').readlines()

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


def build_index(file_name):

    print("\nBUILDING INDEX\n...")

    stopwords = sort_stopwords()
    inv_index = []

    # Preprocesses and indexes collection per document.

    for document in split_file(file_name):
        docnumber = re.sub("[^0-9]", '', document[0])
        document.pop(0)
        text = ', '.join(document)
        text.replace('\n', '')
        tokenizedline = re.split('[\W]', text)
        tokenizedline = filter(None, tokenizedline)

        processed_text = []
        for word in tokenizedline:
            word = word.lower()
            if word not in stopwords and not word.isdigit() :
                processed_text.append(stem(word))

        if 'headlin' in processed_text:
            processed_text.remove('headlin')
        if 'text' in processed_text:
            processed_text.remove('text')

        # Builds an index for each document then appends each to a large index for full collection

        indexes_per_document = []

        for word in processed_text:
            word_occurrences = {}
            term_obj = {}
            positions = [i+1 for i, x in enumerate(processed_text) if x == word] # All positions of a word per document
            word_occurrences[docnumber] = positions     # Dictionary for {document:[list of positions in doc]}
            term_obj[word] = word_occurrences           # Dictionary for {term: {document: [list of positions in doc]}}
            if term_obj not in indexes_per_document:
                indexes_per_document.append(term_obj)
        inv_index.append(indexes_per_document)

    # Sort and group inverted index by word

    inv_index = list(itertools.chain.from_iterable(inv_index))
    inv_index.sort(key=lambda d: sorted(d.keys()))
    inv_index = itertools.groupby(inv_index, key=lambda x: sorted(x.keys()))


    # Format and save to index file

    f = open('index.txt', 'w')

    for word, positions in inv_index:
        string_word = "{}:\n".format(''.join(word))
        f.write(string_word)
        list_positions = []
        for x in list(positions):
            for key, v in x.items():
                list_positions.append(v)
        for item in list_positions:
            for doc, pos in item.items():
                string_position = "\t{}: {}\n".format(doc, (','.join(map(str, pos))))
                f.write(string_position)
        f.write('\n')

    print("INDEXING COMPLETE\n")
    f.close()


if __name__=='__main__':

    try:
        filename = sys.argv[1]
        build_index(filename)
    except FileNotFoundError:
        print("No such file '{}'".format(filename))



