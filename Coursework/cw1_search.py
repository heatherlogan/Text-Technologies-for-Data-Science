import os
import sys
import re
from itertools import chain

import numpy as np
from stemming.porter2 import stem
from string import digits

indexed_file = open('indexed.txt', 'r').readlines()
query_file = open('queries.txt', 'r').readlines()
docnumbers = []
stopwords_file = open('stopwordsfile.txt', 'r').readlines()
stopwords = []
for word in stopwords_file:
    stopwords.append(word.strip())
stopwords.append('id')
stopwords.append('text')
stopwords.append('headline')
stopwords = set(stopwords)


#loads indexed file back into a list of dictionary items [{term: {document:[positions]}}...]

def format_txt_file():

    print("loading index")

    index_list = []
    term_list = []
    for line in indexed_file:
        docno = 0
        idxs = []
        position = {}
        index = {}
        if line.endswith(':\n'):
            term = line.replace(':', '').strip()
            term_list.append(term)
        if line.startswith('\t'):
            split_position = (line.replace('\t', '').replace('\n','').replace(' ', '')).split(':')
            docno, position_list2 = split_position[0], split_position[1]
            idxs = list(map(int, position_list2.split(',')))
            position[int(docno)] = idxs
            docnumbers.append(docno)

        if len(position)>0:
            index[term] = position
            index_list.append(index)
    print('finished loading index')
    return index_list


# load index
inverted_index = format_txt_file()


def preprocess_query(query):
    pp_query = []

    query = query.split(' ')
    for term in query:
        if term not in stopwords:
            term = re.sub(r'\W+', '', stem(term.lower()))
            pp_query.append(term)
    return pp_query

def preprocess_term(term):
    return re.sub(r'\W+', '', stem(term.lower()))


def getpositions(term):
    # stemming and case lower here
    term = stem(term.lower())
    position_list = []
    for index in inverted_index:
        if term in index.keys():
            position_list.append(index.get(term))
    return position_list


def getnot(lst):
    all_docs = sorted(list(set(docnumbers)))
    return [n for n in ([int(x) for x in all_docs]) if n not in lst]


def get_docs(position_list):
    docs = []
    for position in position_list:
        for key in position.keys():
            docs.append(key)
    return docs


def phrasesearch(i, phrase):
    phrase = re.sub('"', '', phrase)
    term1, term2 = phrase.split(' ')
    term1_positions = getpositions(preprocess_term(term1))
    term2_positions = getpositions(preprocess_term(term2))
    results = []

    for position in term1_positions:
        for key in position:
            term1_doc = key
            term1_pos = position[key]

            for position2 in term2_positions:
                for key2 in position2:
                    term2_doc = key2
                    term2_pos = position2[key2]

                    if term1_doc == term2_doc:
                        for p in term1_pos:
                            for p2 in term2_pos:
                                if abs(p-p2) <= i:
                                    results.append(position)
                                    results.append(position2)
    return results # return list of postions

def proximitysearch(query):
    query = re.sub('#', '', query)
    i, query = query.split('(')
    query = re.sub(r'([^\s\w]|_)+', '', query)
    results = phrasesearch(int(i), query)
    return list(set(get_docs(results)))


def boolean_search(query):

    results = []

    if 'AND NOT' in query:
        idx1 = query.index('AND')
        idx2 = idx1 + 7
    elif 'OR NOT' in query:
        idx1 = query.index('OR')
        idx2 = idx1 + 6
    elif 'AND' in query:
        idx1 = query.index('AND')
        idx2 = idx1 + 3
    elif 'OR' in query:
        idx1 = query.index('OR')
        idx2 = idx1 + 2

    term1 = query[:idx1].strip()
    term2 = query[idx2:].strip()

    if term1.startswith('"') and term1.endswith('"'):
        term1_positions = phrasesearch(1, term1)
    else:
        term1_positions = getpositions(preprocess_term(term1))
    if term2.startswith('"') and term2.endswith('"'):
        term2_positions = phrasesearch(1, term2)
    else:
        term2_positions = getpositions(preprocess_term(term2))

    term1_positions = get_docs(term1_positions)
    term2_positions = get_docs(term2_positions)

    if 'NOT' in query:
        term2_positions = getnot(term2_positions)

    if 'AND' in query:
        results = list(set(term1_positions) & set(term2_positions))

    if 'OR' in query:
        results = list(set(term1_positions) | set(term2_positions))

    return results


def rankedir_search(query):
    results = []
    query = query.split(' ')
    N = len(list(set(docnumbers)))
    tfidfs = {}

    def tfidf(tf, df):
        return (1 + np.log10(tf)) * (np.log10(N/df))

    for term in query:
        term = preprocess_term(term)
        positions = getpositions(term)
        docfreq = len(positions)

        for position in positions:
            for doc in position:
                termfreq = len(position[doc])
                t = tfidf(termfreq, docfreq)

                if doc not in tfidfs.keys():
                    tfidfs[doc] = t
                else:
                    newval = tfidfs[doc].__add__(t)
                    tfidfs[doc] = newval
    return tfidfs


def print_results(queryno, results):

    query_results = []
    if len(results) > 0:
        for documentnumber in results:
            output_string = "{} 0 {} 0 1 0".format(queryno, documentnumber)
            query_results.append(output_string)
            print(output)
    return query_results

def print_results_IR(queryno, results):

    query_results = []
    results_c = results.copy()
    for doc, score in results_c.items():
        if score == 0.0:
            results.pop(doc)
    results = (sorted(results.items(), key=lambda kv: kv[1], reverse=True))
    for item in results:
        doc, score = item
        output = "{} 0 {} 0 {} 0".format(queryno, doc, round(score, 3))
        query_results.append(output)
        print(output)

    return query_results


# query in list format, preprocesses
def parsequery(queryno, query):

    results = []    # list of positions
    querytype = "not_ir"
    results_string = []

    if 'AND' in query or 'OR' in query:
        results = boolean_search(query)

    elif query.startswith('#') and query.endswith(")"):
        results = proximitysearch(query)

    elif query.startswith('"') and query.endswith('"'):
        positions = phrasesearch(1, query)
        t = []
        for p in positions:
            for key in p:
                t.append(key)
        results.extend(list(set(t)))

    elif len(query.split(' ')) == 1:
        for item in getpositions(query):
            for key in item.keys():
                results.append(key)
    else:
        querytype = "IR"
        results = rankedir_search(query)

    if querytype == "IR":
        query = preprocess_query(query)
        results_string.append(print_results_IR(queryno, results))
    else:
        results_string.append(print_results(queryno, results))

    return list(chain.from_iterable(results_string))

if __name__=='__main__':

    output = []

    for query in query_file:
        queryno = int(query.split()[0])
        query = query.lstrip(digits).strip()
        results_string = parsequery(queryno, query)

        if len(results_string) > 1000:
            results_string = results_string[:1000]

        if len(results_string)>0:
            output.append(results_string)

    output = list(chain.from_iterable(output))
    f = open('results.ranked.txt', 'w')

    for line in output:
        f.write(line + "\n")
    f.close()
