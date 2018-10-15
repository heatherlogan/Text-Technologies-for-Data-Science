import sys
import re
from stemming.porter2 import stem

file = open(sys.argv[1], 'r').readlines()
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
# presenting documents to work on when  building index


def preprocess():

    pp_file = []

    print("Beginning preprocess")
    f = open("output_files/preprocessed.txt", 'w')

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
        pp_file.extend(document)
        f.write(' '.join(processed_text))
    print('finished preprocessing')
    return pp_file


if __name__=='__main__':
    file = preprocess()