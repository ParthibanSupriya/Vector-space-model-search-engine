# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 17:46:22 2018

@author: supri
"""
import re
import string
import collections
import math
reg = re.compile('[%s]' % re.escape(string.punctuation))#removes punctuation
data = []#stores the whole 100 docs
query = []#stores the queries
keyword = {}#dictionary of the cleaned word/bag of words and their position
no_of_words = {}#dictionary of documents and total number of words
inverted_index = collections.defaultdict(list) #inverted index 'word' : [('docid',[pos1,pos2..])]
tfmax = {} #stores max no of times a term is repeated
stats = collections.defaultdict(dict) #preprocessed info is stored
id = 1    #as the list index starts with 0 we assifn id as 1
with open('collection-100.txt') as fp:#reaing the collection-100
    dline = fp.readline()
    while dline:
        tmp = dline.strip().lower()#lower is used because 'bank' and 'Bank' means same here
        if len(tmp) > 0:#remove empty lines
            data.append(tmp)#add the doc to data
        dline = fp.readline()
for row in data:#preprocessing the collection
    words = reg.sub('', row).split()
    no_of_words[data.index(row)] = len(words)
    sentence = []#list of the keywords with their location
    for i, word in enumerate(words):
        if len(word) >= 4:
            if word.endswith('s'): word = word[:-1]
            sentence.append((word, i))
    keyword['Doc'+str(id)] = sentence#dictionary with docid as key and keywords as value
    id += 1
for id, sentence in keyword.items():
    for word, i in sentence:
        loc = inverted_index[word]
        if not loc: #checking if the word exists in the inverted index
            loc.append((id, [i]))
        else:
            yes = 0
            for i, (did, poss) in enumerate(loc):
                if id == did:#if the doc already exists we append the position of the word
                    yes = 1
                    loc[i][1].append(i)
                    break
            if not yes:
                loc.append((id, [i]))
    temp = collections.defaultdict(int)
    counter = collections.defaultdict(int)
    for word, _ in sentence:
        temp[word] += 1
        tfmax[id] = temp[max(temp, key=temp.get)]#stores tfmax of each doc
        counter[word] += 1 
        magnitude = 0
        weight = {}
        for word, count in counter.items():
            tfmaxval = tfmax[id]
            idf = math.log(len(data)/len(inverted_index[word]), 2)
            weight[word] = count / tfmaxval * idf
            magnitude += weight[word] ** 2
            stats[id]['norm'] = math.sqrt(magnitude)
            stats[id]['word'] = weight
with open('query-10.txt') as qp:#reading the query file
    qline = qp.readline().strip().lower()
    while qline:
        query.append(reg.sub('', qline).split())
        qline = qp.readline().strip().lower()
for row in query:
    sim = collections.defaultdict(int)
    for word in row:
        if word in inverted_index: #finding the words in the query in the inverted index
            found = inverted_index[word]
            for idq, poss in found:
                tfmaxval1 = tfmax[idq]
                idf = math.log((len(data))/(len(found)), 2)
                sim[idq] += len(poss) / tfmaxval1 * idf
    for id in sim:
        sim[id] /= (math.sqrt(len(row)) * stats[id]['norm'])
        top_doc = {id: sim[id] for id in sorted(sim, key=sim.get, reverse=True)[:3]}
    print('*'*92, '\nquery: %s' % row)#output block
    for id in top_doc.keys():
        print('DID:', id)
        print('\ntop 5 keywords\n')
        word_weights = stats[id]['word']
        weight = sorted(word_weights, key=word_weights.get, reverse=True)[:5]
        for word in weight:
            print('%s->\t%s' % (word, inverted_index[word]))
        print('\nUnique keywords in the document:', len(stats[id]['word']))
        print('Magnitude of the document vector: %.3f' % stats[id]['norm'])
        print('Similarity score: %.3f' % top_doc[id])
        print('.'*92)
print('_'*92)
print('CSIT 6000I: Search Engines and Applications Homework 2 - Done by - Supriya Parthiban - 20567171')
print('_'*92)
