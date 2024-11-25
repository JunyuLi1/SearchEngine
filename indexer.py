import os
import re
import json
import math
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import hashlib
import ast

class Posting:
    def __init__(self, docid, tfidf, fields, position):
        self.docid = docid
        self.tfidf = tfidf
        self.fields = fields
        self.position = position

    def to_dict(self):
        return {
            'docid': self.docid,
            'tfidf': self.tfidf,
            'fields': self.fields,
            'position': self.position
        }
    def __eq__(self, other):
        return (self.docid == other.docid) and (self.tfidf == other.tfidf)
    
    def __repr__(self):
        return f"Posting(docid={self.docid}, tfidf={self.tfidf}, fields={self.fields}, position={self.position})"


class SimpleIndexer:
    def __init__(self):
        self.index = defaultdict(list)
        self.stemmer = PorterStemmer()
        self.num_doc = 0
        self.stop_words = []
        self.unqiue_word = 0
        self.docid_map = {}
        self.visited_hashes = []
        self.weight = {'title': 6, 'h1': 5, 'h2': 4, 'h3': 2, 'b': 3, 'n': 1}

    def tokenize(self, text):
        tokens = []
        temp_word = ""
        for char in text:
            if '0' <= char.lower() <= '9' or 'a' <= char.lower() <= 'z':
                temp_word += char.lower()
            else:
                if temp_word:
                    tokens.append(temp_word)
                    temp_word = ""
        if temp_word:                       # Add the last word if there is one
            tokens.append(temp_word)
        return tokens


    def index_document(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            full_html_text,important_text = self.get_html_text(data['content'])
            tokens = self.tokenize(full_html_text)
            #fingerprint2 = self.get_fingerprint(tokens) #similarity
            #if self.check_all_sim(fingerprint2):
            stem_count = defaultdict(lambda: [0, 'n'])
            for keys,value in important_text.items():
                for i in range(len(value)):
                    value[i] = self.tokenize(value[i]) #lis of lis
            for token in tokens:
                stemmed_token = self.stemmer.stem(token)
                stem_count[stemmed_token][0] += 1
            for keys in important_text:
                for each_important in important_text[keys]:
                    for token2 in each_important:
                        stemmed_token = self.stemmer.stem(token2)
                        if stemmed_token in stem_count:
                            if keys == 'title':
                                stem_count[stemmed_token][1] = 'title'
                            if keys == 'h1':
                                if self.weight[stem_count[stemmed_token][1]] < 5:
                                    stem_count[stemmed_token][1] = 'h1'
                            if keys == 'h2':
                                if self.weight[stem_count[stemmed_token][1]] < 4:
                                    stem_count[stemmed_token][1] = 'h2'
                            if keys == 'h3':
                                if self.weight[stem_count[stemmed_token][1]] < 2:
                                    stem_count[stemmed_token][1] = 'h3'
                            if keys == 'b':
                                if self.weight[stem_count[stemmed_token][1]] < 3:
                                    stem_count[stemmed_token][1] = 'b'
            self.num_doc += 1
            for s_token, frequency in stem_count.items():
                posting = Posting(self.num_doc, frequency[0], frequency[1], position = 0)
                self.index[s_token].append(posting)
            self.docid_map[self.num_doc] = data['url']
                #self.visited_hashes.append(fingerprint2)     


    def index_files(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith('.json'):
                    file_path = os.path.join(root, file_name)
                    self.index_document(file_path)
                    print(self.num_doc)
                    # if len(self.index) > 200000:
                    #     self.merge_with_existing_index()
                    #     self.index.clear()
                    #     print("Memory cleared")
    
    def get_html_text(self, source):
        """get texts that user could see using bs4"""
        soup = BeautifulSoup(source, 'lxml')
        source = str(soup) #check brokenhtml
        soup = BeautifulSoup(source, 'lxml')

        #all_tags = soup.find_all(True)  #important text
        extracted_text = {'h1': [], 'h2': [], 'h3': [], 'b': [], 'title':[]}
        # for tag in all_tags:
        #     if tag.name:
        #         if tag.name in extracted_text:
        #             extracted_text[tag.name].append(tag.get_text())
        #         if tag.has_attr('title'):
        #             extracted_text['title'].append(tag['title'])
        title_tag = soup.find('title')
        if title_tag:
            extracted_text['title'].append(title_tag.get_text())

        # Extract h1, h2, h3, and b tags content
        for tag_name in ['h1', 'h2', 'h3', 'b']:
            for tag in soup.find_all(tag_name):
                extracted_text[tag_name].append(tag.get_text())

        for script in soup(["script", "style"]):
            script.decompose()
        full_html_text = self.get_related_text(soup.get_text())

        return full_html_text,extracted_text

    def get_related_text(self, text):
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text


    def write_report(self):

        report = f"Number of documents: {self.num_doc}\nNumber of unique words: {self.unqiue_word}"

        file_size_kb = os.path.getsize('index.txt') / 1024  # Convert bytes to kilobytes

        report += f"\nFile size: {file_size_kb:.2f} KB"

        with open('report.txt', "w") as file:
            file.write(report)

        with open("docid_map.json", 'w', encoding='utf-8') as file:
            json.dump(self.docid_map, file)    

    


    def get_fingerprint(self, lisOfAllToken): #use this function to calculate hash value
        tokenFrequency = self.computeWordFrequencies(lisOfAllToken)#compute frequency
        vector = [0] * 64 #initialize vector(fingerprint)
        for key, (weight, binary_string) in tokenFrequency.items():
            for i, bit in enumerate(binary_string):
                # if 0 mult -1, 1 otherwise
                multiplier = 1 if bit == '1' else -1
                # weight binary
                vector[i] += weight * multiplier
        #generating fingerprint
        for i in range(64):
            if vector[i] > 0:
                vector[i] = 1
            else:
                vector[i] = 0
        return vector

    def get_score(self,fingerprint1, fingerprint2):
        score = 0
        finalfingerprint = [0]*64
        for i in range(64): #bitwise two fingerprint
            if fingerprint1[i] == fingerprint2[i]:
                finalfingerprint[i] = 1
            else:
                finalfingerprint[i] = 0
        for value in finalfingerprint:
            score += value
        return score/64

    def computeWordFrequencies(self,listToken):
        wordDict = {}
        for item in listToken:
            word_hashvalue = self.simple_hash_to_binary(item)
            if item not in wordDict:
                wordDict[item] = [1,word_hashvalue]
            else:
                wordDict[item][0] +=1
        return wordDict

    def simple_hash_to_binary(self,value): #compute binary value of word hash value
        hash_object = hashlib.sha256(value.encode())
        hex_dig = hash_object.hexdigest()
        hash_int = int(hex_dig, 16) #conver hex to int
        lower_64_bits = hash_int & ((1 << 64) - 1) #get low 64 bits
        binary_representation = bin(lower_64_bits)[2:].zfill(64) #convert to bin
        return binary_representation

    def check_all_sim(self,fingerprint2): #check for all
        for value in self.visited_hashes:
            score = self.get_score(value, fingerprint2)
            if  score > 0.9:
                return False
        return True
    

    def merge_with_existing_index(self):
        # Load the existing index from the JSON file
        try:
            with open("index.txt", 'r', encoding='utf-8') as file:
                existing_index = self.parse_txt_to_dict()
        except:
            existing_index = {}

        # Merge the new index with the existing index
        for key, postings in self.index.items():
            if key in existing_index:
                existing_index[key].extend(posting.to_dict() for posting in postings)
            else:
                existing_index[key] = [posting.to_dict() for posting in postings]
        self.unqiue_word = len(existing_index)

        # Save the merged index back to the text file
        with open("index.txt", 'w', encoding='utf-8') as file:
            for key, value in existing_index.items():
                file.write(f'{str(key)}: {value}\n')

    def parse_txt_to_dict(file_path):
        result_dict = {}
        with open("index.txt", 'r', encoding='utf-8') as file:
            for line in file:
                # Find the first colon to separate the term from the list representation
                colon_index = line.find(':')
                if colon_index != -1:
                    # Extract term and list representation
                    term = line[:colon_index].strip()
                    list_repr = line[colon_index + 1:].strip()
                    # Convert the list representation from string to list using ast.literal_eval()
                    result_dict[term] = ast.literal_eval(list_repr)
        return result_dict

    def count_and_save_tfidf(self):
        #the algorithm is "w t,d = (1+log(tft,d)) x log(N/dft)"
        with open("index.txt", 'r+', encoding='utf-8') as file:
            existing_index = self.parse_txt_to_dict()

            for term in existing_index:
                for posting in existing_index[term]:
                    tf = (1 + (math.log(posting['tfidf'], 10)))
                    idf = math.log((self.num_doc / len(existing_index[term])), 10)
                    tfidf = tf*idf
                    posting['tfidf'] = tfidf
            # file.seek(0)
            # file.truncate()
            for key, value in existing_index.items():
                file.write(f'{key}: {value}\n')
  

def generate_positions():
    positions = {}
    current_position = 0
    with open("index.txt", 'r', encoding='utf-8') as file:
        for line in file:
            # Use regular expression to extract term and postings
            match = re.match(r'([^:]+): (.+)', line.strip())
            if match:
                term = match.group(1).strip()
                positions[term] = current_position
                # Update the current position by adding the length of the line plus the length of the newline character
                current_position += len(line.encode('utf-8')) + 1
    return positions

if __name__ == "__main__":
    indexer = SimpleIndexer()
    
    indexer.index_files(".\DEV")

    indexer.merge_with_existing_index()
    indexer.count_and_save_tfidf()
    positions = generate_positions()
    with open("secondary_index.json", 'w', encoding='utf-8') as file:
        json.dump(positions, file)
    indexer.write_report()
    