import itertools
import re
from stemming.porter2 import stem

filename = 'trec.sample.txt' #change to sys.argv[1]
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

def split_file():

    # gets indexes of all 'ID's'
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

    print("finished splitting file")

    return newfile


def preprocess():

    inv_index = []

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
            if word not in stopwords and not word.isdigit() :
                processed_text.append(stem(word))

        if 'headlin' in processed_text:
            processed_text.remove('headlin')
        if 'text' in processed_text:
            processed_text.remove('text')

        indexes_per_document = []

        for word in processed_text:
            word_occurences = {}
            term_obj = {}
            positions = [i+1 for i, x in enumerate(processed_text) if x == word]
            word_occurences[docnumber] = positions
            term_obj[word] = word_occurences
            if term_obj not in indexes_per_document:
                indexes_per_document.append(term_obj)
        inv_index.append(indexes_per_document)

    # Sort and group inverted index

    inv_index = list(itertools.chain.from_iterable(inv_index))
    inv_index.sort(key=lambda d: sorted(d.keys()))
    inv_index = itertools.groupby(inv_index, key=lambda x: sorted(x.keys()))

    # Print and save to file

    f = open('indexed.txt', 'w')

    for word, positions in inv_index:
        string_word = "{}:\n".format(''.join(word))
        f.write(string_word)
        list_positions = []
        for x in list(positions):
            for key, v in x.items():
                list_positions.append(v)
        print(list_positions)
        for item in list_positions:
            for doc, pos in item.items():
                string_position = "\t{}: {}\n".format(doc, (','.join(map(str, pos))))
                f.write(string_position)
        f.write('\n')
        # pretty print

preprocess()
