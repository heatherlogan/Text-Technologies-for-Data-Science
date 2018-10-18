import numpy as np
from itertools import chain
from string import digits
from indexer import *


# if a txt file and a query file are given, then index the txt file as in indexer.py and query that output.
# if only a query file is given, then query 'index.txt' in the current directory.

if len(sys.argv) == 3:
    build_index(sys.argv[1])
    query_file = open(sys.argv[2], 'r').readlines()
else:
    query_file = open(sys.argv[1], 'r').readlines()

indexed_file = open('index.txt', 'r').readlines()

docnumbers = []


def format_txt_file():

    # Loads indexed file back into a list of dictionary items [{term: {document:[positions]}}...]

    index_list = []
    term_list = []
    for line in indexed_file:
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
    return index_list


# load index
inverted_index = format_txt_file()


def preprocess_query(query):

    pp_query = []
    stopwords = sort_stopwords()
    query = query.split(' ')
    for term in query:
        if term not in stopwords:
            term = re.sub(r'\W+', '', stem(term.lower()))
            pp_query.append(term)
    return pp_query


def preprocess_term(term):
    return re.sub(r'\W+', '', stem(term.lower()))


def getpositions(term):

    # For a term, retrieves a list of all positions from the inverted index.

    position_list = []
    for index in inverted_index:
        if term in index.keys():
            position_list.append(index.get(term))
    return position_list


def getnot(lst):

    # takes list of documents and returns the all documents in collection except those in list.

    all_docs = sorted(list(set(docnumbers)))
    return [n for n in ([int(x) for x in all_docs]) if n not in lst]


def get_docs(position_list):

    # extracts the documents from a list of {doc:[position]} dictionaries

    docs = []
    for position in position_list:
        for key in position.keys():
            docs.append(key)
    return docs


def phrasesearch(i, phrase):

    # used for both phrase search and proximity search.
    # if phrase search, i=1, if proximity search, i is passed from proximity search method.

    phrase = re.sub('"', '', phrase)
    term1, term2 = phrase.split(' ')
    term1_positions = getpositions(preprocess_term(term1))
    term2_positions = getpositions(preprocess_term(term2))
    results = []

    # loops through all positions that both terms occur in and adds to list if distance between terms <= i.

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

    # format query and send to phrase search with i being the distance given.

    query = re.sub('#', '', query)
    i, query = query.split('(')
    query = re.sub(r'([^\s\w]|_)+', '', query)
    results = phrasesearch(int(i), query)

    return list(set(get_docs(results)))


def boolean_search(query):

    # Gets type of boolean query, splits into the two terms mentioned.

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

    # If either term is a phrase search then get results from phrase method.

    if term1.startswith('"') and term1.endswith('"'):
        term1_positions = phrasesearch(1, term1)
    else:
        term1_positions = getpositions(preprocess_term(term1))
    if term2.startswith('"') and term2.endswith('"'):
        term2_positions = phrasesearch(1, term2)
    else:
        term2_positions = getpositions(preprocess_term(term2))

    # Convert to list of documents without indexes

    term1_positions = get_docs(term1_positions)
    term2_positions = get_docs(term2_positions)


    if 'NOT' in query:
        term2_positions = getnot(term2_positions) # revert list

    if 'AND' in query:
        results = list(set(term1_positions) & set(term2_positions))
    if 'OR' in query:
        results = list(set(term1_positions) | set(term2_positions))

    return results


def rankedir_search(query):

    # gets list of positions for each term in the query and calculates tfidf score for each document

    query = query.split(' ')
    N = len(list(set(docnumbers)))
    tfidfs = {} # Dictionary to store {docnumber: tfidf score}

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


def print_results(queryno, results):    # formats the list of results per query to TREC format for boolean, phrase and proximity queries

    query_results = []
    if len(results) > 0:
        for documentnumber in results:
            output_string = "{} 0 {} 0 1 0".format(queryno, documentnumber)
            query_results.append(output_string)

    return query_results


def print_results_IR(queryno, results):     # formats the list of results per query to TREC format for rank queries

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

    return query_results


# Query in list format, preprocesses

def parsequery(queryno, query):

    results = []    # list of positions
    querytype = "not_ir"       # variable used to decide which print/save method to use for rank or bool/phrase query
    results_string = []

    # check structure of query to send to appropriate search method

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

    elif len(query.split(' ')) == 1: # single word query
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

    print("\nANSWERING QUERIES\n...")

    output = []

    for query in query_file:
        queryno = int(query.split()[0])
        query = query.lstrip(digits).strip()
        results_string = parsequery(queryno, query)

        if len(results_string) > 1000: # only print out first 1000 queries
            results_string = results_string[:1000]

        if len(results_string)>0:
            output.append(results_string)

    # save to file

    output = list(chain.from_iterable(output))
    f = open('results.txt', 'w')

    for line in output:
        f.write(line + "\n")
    f.close()

    print("QUERYING COMPLETE\n")
