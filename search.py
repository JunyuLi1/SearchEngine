import ast
import numpy as np
from collections import defaultdict
import math
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()
import time
import json

def search(query, index, doc_mp, file):
    """
    param:
    query: user input
    index: all index
    doc_mp: map for doc id and the original url
    """

    query_terms = query.split(" ")
    query_lists = []
    result = None
    posting_list = {} #made positing matrix
    tfidf_sum = {}
    total_doc = len(doc_mp)
    total_score = {}
    weight_value = {'title': 4.0, 'h1': 2.5, 'h2': 1.8, 'h3': 1.2, 'b': 1.5, 'n': 1.0}
    #create stemmed query
    for term_not_stem in query_terms:
        term = stemmer.stem(term_not_stem)
        query_lists.append(term)

    #get the files where contains all query information
    for term in query_lists:
        if term in index:
            #new change
            position = index[term]
            
            postings = seek_and_load(position, file)
            
            #end change
            if result is None:
                result = set(posting['docid'] for posting in postings)
            else:
                result = result.intersection(set(posting['docid'] for posting in postings))

            for posting in postings:
                docid = posting['docid']
                tfidf = posting['tfidf']
                if docid in tfidf_sum:
                    tfidf_sum[docid] += tfidf * weight_value[posting['fields']]
                else:
                    tfidf_sum[docid] = tfidf * weight_value[posting['fields']]

            posting_list[term] = postings
        else:
            return [] 
    #get doc length
    doc_length = compute_doc_length(posting_list)

    #count cosine similarity, return a dictionary, key is docid, and value is cosine similarity score
    doc_scores = cosine_similarity(query_lists, posting_list, doc_length, total_doc)
    for doc_id in doc_scores:
        if doc_id in tfidf_sum:
            total_score[doc_id] = doc_scores[doc_id] * tfidf_sum[doc_id]

    # ranked by cosine similarity
    if result is not None:
        sorted_docids = sorted(result, key=lambda docid: total_score[docid], reverse=True)
        return [doc_mp[f'{docid}'] for docid in sorted_docids]
    else:
        return []
    
def seek_and_load(position, file):
    # Move to the specific position in the file
    
    file.seek(position)
    
    # Read the line at the specified position
    
    line = file.readline()
    
    colon_index = line.find(':')
    if colon_index != -1:
        list_repr = line[colon_index + 1:].strip()
        list_repr = list_repr.replace("'", '"')
        # Convert the list representation from string to list using ast.literal_eval()
        #print(list_repr)
        return json.loads(list_repr)
        
    return []
    
def count_query_tfidf(term, query, doc_fre, total_doc):
    tf = (1 + (math.log(query.count(term), 10)))
    idf = math.log((total_doc / doc_fre), 10)
    tfidf = tf*idf
    return tfidf

def compute_doc_length(posting_list):
    doc_lengths = defaultdict(float)
    for postings in posting_list.values():
        for posting in postings:
            wt_d = posting['tfidf']
            doc_lengths[posting['docid']] += wt_d ** 2
    
    for d in doc_lengths:
        doc_lengths[d] = np.sqrt(doc_lengths[d])

    return doc_lengths

def cosine_similarity(query_list, postings_lists, doc_lengths, total_doc):
    scores = defaultdict(float)
    for term in query_list:
        postings = postings_lists[term]
        wt_q = count_query_tfidf(term, query_list, len(postings), total_doc)
        for posting in postings:
            scores[posting['docid']] += posting['tfidf'] * wt_q
    
    for d in scores:
        if doc_lengths[d] != 0:
            scores[d] /= doc_lengths[d]

    return scores
if __name__ == "__main__":
    a = seek_and_load(0)
    print(len(a))