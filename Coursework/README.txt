How to Run


1. indexer.py

- indexer.py will take a txt file as argument containting a list of documents and save a preprocessed version of the file
named 'preprocessed.txt', and the indexed file named 'indexed.txt' in the current directory.

- to run, enter 'python3 indexer.py nameofdocumentfile.txt' in command line.

- ensure that the file named 'stopwordsfile.txt' is in the current directory as this is crucial for accurate
preprocessing.



2. search.py

- search.py will take a txt file containing queries, run on the previously outputted file named 'indexed.txt'.
the indexer must have run on the document txt file and therefore the indexed.txt file must be in the current directory
to execute this module. The results to the query file will be saved to a file named 'results.txt'.

- to run, enter 'python3 search.py nameofqueryfile.txt' in command line.
