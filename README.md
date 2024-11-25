# SearchEngine
Author: Yuxi Dai, Junyu Li, Frank Xu, Shelly Wu

How to create index use indexer.json?
    in the indexer.json, you should replace the path under if __name__ == "__main__": with the path where DEV folder at, 
    then run indexer file. After the parsing, you will get three files which are index.txt, docid_map.json, secondary_index.json.
    index.txt are inverted index, docid_map.json is a file to locate the url of a docid, and secondary_index is index of inverted index.

How to run the search engine?
    In ui.py, replace the path of docid_map, secondary_index, and index with the path that generated from indexer.json, then type 
    streamlit run ui.py to run the program.