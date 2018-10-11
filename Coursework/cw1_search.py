import os
import sys
import re
from collections import defaultdict
from stemming.porter2 import stem
from string import digits

indexed_file = open('indexed.txt', 'r').readlines()
query_file = open('queries.txt', 'r').readlines()
docnumbers = []

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


# returns intersection positions for two lists

def getand(lst1, lst2):
    found_positions = []
    for item in lst1:
        for key in item.keys():
            for item2 in lst2:
                if key in item2.keys():
                    #found
                    found_positions.append(key)
    return found_positions


# returns union
def getor(lst1, lst2):
    found_positions = []
    for item in lst1:
        for key in item.keys():
            found_positions.append(key)
    for item in lst2:
        for key in item.keys():
            found_positions.append(key)
    return list(set(sorted(found_positions)))


def getnot(lst):
    all_docs = sorted(list(set(docnumbers)))
    doclist = []
    for item in lst:
        for key in item.keys():
            doclist.append(key)
    return [n for n in ([int(x) for x in all_docs]) if n not in doclist]

def printresults(queryno, results):
    f =  open('results.boolean.txt', 'w')
    if len(results) > 0:
        for documentnumber in results:
            print("{} 0 {} 0 1 0".format(queryno, documentnumber))
            f.write("{} 0 {} 0 1 0\n".format(queryno, documentnumber))


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

def get_docs(position_list):
    docs = []
    for position in position_list:
        for key in position.keys():
            docs.append(key)
    return docs


def boolean_and(query):
    idx1 = query.index('AND')
    term1 = query[:idx1].strip()
    term2 = query[idx1+3:].strip()

    if term1.startswith('"') and term1.endswith('"'):
        term1_positions = phrasesearch(1, term1)
    else:
        term1_positions = getpositions(preprocess_term(term1))

    if term2.startswith('"') and term2.endswith('"'):
        term2_positions = phrasesearch(1, term2)
    else:
        term2_positions = getpositions(preprocess_term(term2))

    print(term1_positions)
    print(term2_positions)

    return list(set(term1_positions) & set((term2_positions)))


def boolean_or(query):

    idx1 = query.index('OR')
    term1 = query[:idx1].strip()
    term2 = query[idx1 + 2:].strip()
    if term1.startswith('"') and term1.endswith('"'):
        term1_positions = phrasesearch(1, term1)
    else:
        term1_positions = getpositions(preprocess_term(term1))
    if term2.startswith('"') and term2.endswith('"'):
        term2_positions = phrasesearch(1, term2)
    else:
        term2_positions = getpositions(preprocess_term(term2))

    return list(set(get_docs(term1_positions)) | set(get_docs(term2_positions)))

# query in list format, preprocesses
def parsequery(queryno, query):
    results = []    # list of positions
    bool_ops = ['AND', 'OR', 'NOT']

    if 'AND' in query:
        results = boolean_and(query)
    elif 'OR' in query:
        results = boolean_or(query)

    elif query.startswith('#') and query.endswith(")"):
        results = proximitysearch(query)

    elif query.startswith('"') and query.endswith('"'):
        positions = phrasesearch(1, query)
        t = []
        for p in positions:
            for key in p:
                t.append(key)
        results.extend(list(set(t)))

    elif len(query.split(' '))>0:
        for item in getpositions(query):
            for key in item.keys():
                results.append(key)
    return results


if __name__=='__main__':

    for query in query_file:
        queryno = int(query.split()[0])
        query = query.lstrip(digits).strip()
        results = parsequery(queryno, query)
        printresults(queryno, results)
