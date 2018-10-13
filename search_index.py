import os
import sys
import re
from collections import defaultdict
from stemming.porter2 import stem

indexed_file = open('indexed.txt', 'r').readlines()
query_file = open('queries.txt', 'r').read()
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

        print("Finished loading index")
    return index_list


def getpositions(term):
    # stemming and case lower here
    term = stem(term.lower())
    position_list = []
    for index in format_txt_file():
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
    if len(results) < 1:
        results = [0]
    for documentnumber in results:
        print("{} 0 {} 0 1 0".format(queryno, documentnumber))
        f.write("{} 0 {} 0 1 0\n".format(queryno, documentnumber))


def phrasesearch(querynumber, phrase):

    term1, term2 = phrase.split(' ')
    term1_positions = getpositions(term1)
    term2_positions = getpositions(term2)
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
                                if p == p2+1 or p+1 == p2:
                                    results.append(term1_doc)
    printresults(querynumber, results)

def booleansearch(querynumber, query):

    query = query.split(" ")
    results = []
    # boolean searches
    if 'AND' in query:
        results = getand(getpositions(query[0]), getpositions(query[2]))
    elif 'OR' in query:
        results = getor(getpositions(query[0]), getpositions(query[2]))
    elif 'NOT' in query:
        results = getnot(getpositions(query[1]))

    # single phrase search
    elif len(query) == 1:   
        results = []
        for item in getpositions(query[0]):
            for key in item.keys():
                results.append(key)
    else:
        print('Query is badly formed')

    printresults(querynumber, results)


def parsequery():
    # get Query number, and query type, send to appropriate method
    # boolean search, phrase search, proximity search or ranked IR

    for query in query_file.split("\n"):
        if len(query)>0:
            queryno, querytext = query.split(': ')
            queryno = re.sub('[^0-9]', '', queryno)

        if querytext.startswith('#') and querytext.endswith(")"):
            pass

        elif querytext.startswith('"') and querytext.endswith('"'):
            querytext = re.sub('"', '', querytext)
            phrasesearch(queryno, querytext)

        else:
            booleansearch(queryno, querytext)





if __name__=='__main__':
    parsequery()

