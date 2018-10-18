
**** README ****

Each module can be run independently, except if only passing a query file to search.py, then it will assume a file has already been indexed.
stopwordsfile.txt must be in the working directory or preprocessing wont work.


1. preprocessor.py

- to run 'python3 preprocessor txtfile_name.txt'
- saves the preprocessed txt file named "preprocessed.txt" to current directory
Independent of indexer and search modules.

2. indexer.py

- to run 'python3 indexer.py txtfile_name.txt'
- save 'index.txt' to current directory

3. search.py

- to run 'python3 search.py txtfile_name.txt queryfile_name' OR 'python3 search.py queryfile_name.txt'
- saves 'results.txt' to current directory
- if given a txt file and query file, will run indexer.py on the txt file and queries the newly build index.txt file.
- otherwise, assumes an index.txt file already exists in current directory and queries that.