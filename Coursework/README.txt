***** How to Run ******

Before: ensure the named 'stopwordsfile.txt' is in the current directory as this is crucial for accurate preprocessing,
Before: the modules must be executed in the order 'indexer.py > search.py' or will throw error.


******************

1. indexer.py

- to run, enter 'python3 indexer.py name_of_document.txt' in command line.

- indexer.py will work on the file 'preprocessed.txt' produced by executing preprocess.py, and will place the indexed file named 'indexed.txt' in the current directory.

*******************

2. search.py

- to run, enter 'python3 search.py name_of_query_file.txt' in command line.

- search.py will take a txt file containing queries as argument, run on the previously outputted file named 'indexed.txt' the indexer must have run on the document txt file and therefore the indexed.txt file must be in the current directory to execute this module. The results to the query file will be saved to a file named 'results.txt'.

