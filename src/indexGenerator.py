"""
Author: Sevtap Fernengel
File name: indexGenerator.py
Description: this file contains the code to create the index file
using the tfidf formula given in the project description file

Usage: to create the index file for nyt199501 simply execute

python3.2 indexGenerator.py

Once the execution is complete, an index.txt file will be created
"""

import re
import math
import operator
import string


indexFileName = 'index.txt' # name of the index file to be created
corpusFileName = '../data/nyt199501.txt' # input file name where the corpus is

# initialize the variables

print('Processing the {0} file to create the index.txt file...'.format(corpusFileName))
docId = '' # used to hold the document id
docCount = 0 # how many documents are in the corpus
wordCounts = dict() # a nested dictionary which holds words counts for the document collection
wordCountsPerDocument = None # a dictionary that holds the word counts for a given document
extractDocIdPattern = re.compile(r'<DOC id="(?P<id>.*?)" .*>') # needed to get the document id

# open the corpus file for reading
with open(corpusFileName) as corpus:
    # read the next line from the file
    for line in corpus:
        # it might be the beginning of a new document
        if line.startswith('<DOC id='):
            # create a new dictionary to hold the word counts for this document
            wordCountsPerDocument = dict()
            # remember the document id for this document
            docId = extractDocIdPattern.match(line).group('id')
        # it is the end of the document
        elif line.startswith('</DOC>'):
            # add the dictionary of word counts into the top level dictionary
            # using the doc id as a key
            wordCounts[docId] = wordCountsPerDocument
        # neither the beginning nor the end of the document
        else:
            # get individual words out of the line
            for word in line.split():
                # remove the punctuation at the end of each word
                word = word.strip(string.punctuation)
                # after removing everything, if there are any characters left
                # then remember this word
                if word:
                    # first initialize the word count, if this word has not been seen before
                    wordCountsPerDocument.setdefault(word, 0)
                    # increase the word count, if this word has been seen before
                    wordCountsPerDocument[word] += 1

# remember how many documents are in the document collection
docCount = len(wordCounts.keys())

# create a dictionary for holding the inverse document frequencies
# for the document collection
# this dictionary is a global dictionary
inverseDocumentFreqs = dict()
# iterate over all the documents
for docId, tfPerDocument in wordCounts.items():
    # iterate over all the words for a given documents
    for term in tfPerDocument.keys():
        # first initialize the inverse term count if this term has not been counted before
        inverseDocumentFreqs.setdefault(term, 0)
        # increase the inverse term count, for every new document this term appears in
        inverseDocumentFreqs[term] += 1

# iterate over each term in the document collection
for term, inverseCount in inverseDocumentFreqs.items():
    # calculate the inverse term frequency using the math formula
    x = docCount
    x /= inverseCount
    inverseDocumentFreqs[term] = math.log(x, 2)

# The nested dictionary to hold the tf*idf for each word for a given document
tfIdf = dict()
# iterate over each document in the collection
for docId, tfPerDocument in wordCounts.items():
    # create a tfidf dictionary for this particular document
    tfIdfPerDocument = dict()
    # for each term in this document
    for term, count in tfPerDocument.items():
        # generate the tf * idf for the term and add to the dictionary
        tfIdfPerDocument[term] = count * inverseDocumentFreqs[term]
    # add tfidf dictionary for a particular document into the top level dictionary
    tfIdf[docId] = tfIdfPerDocument

# In this part we extract the top ten most relevant words for a document
# This is a dictionary for holding the documents with top ten relevant words
relevantWords = dict()
# Iterate over each document in the document collection
for docId, tfIdfPerDocument in  tfIdf.items():
    # create a list of (word, tfidf_for_word) pairs
    topTen = list(tfIdfPerDocument.items())
    # sort this list, so that the word with the highest tfidf_for_word value is on top
    # and slice the top ten values on this list
    topTen = sorted(topTen, key=operator.itemgetter(1), reverse=True)[:10]
    # add the list of (word, tfidf_for_word) pairs to our dictionary
    relevantWords[docId] = topTen

# Finally write the words for each document with the tfidf score to a file
# Open the index.txt file for writing
with open(indexFileName, 'w') as indexFile:
    # Iterate over all the documents in the collection
    for docId, words in relevantWords.items():
        # Iterate over each word for this document
        for word, relevancy in words:
            # create the line with the needed information
            # document id, tfidf score for a word, word
            line = docId + '\t' + str(relevancy) + '\t'+ word + '\n'
            # write this line to the file
            indexFile.write(line)

print('Finished creating the index file')