import pandas as pd
import matplotlib.pyplot as plt
import os
import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# The follwing three definations can be replaced by build-in TfidfVectorizer
# Calculate the Term Frequency in one document(one tweet) bagofWords is a list
def computeTF(wordDict, bagOfWords):
    tfDict = {}
    bagOfWordsCount = len(bagOfWords)
    for word, count in wordDict.items():
        tfDict[word] = count / float(bagOfWordsCount)
    return tfDict

# Calculate the the REVERSE of Document(with unique words) Frequency in the document aggregrates
def computeIDF(documents, uniquewords):
    import math
    N = len(documents)

    idfDict = dict.fromkeys(uniquewords, 0)

    for document in documents:
        for word, val in document.items():
            if val > 0:
                idfDict[word] = idfDict[word] + 1
    
    for word, val in idfDict.items():
        idfDict[word] = math.log(N / float(val))
    return idfDict

# calculate the product of the above results
def computeTFIDF(tfBagOfWords, idfs):
    tfidf = {}
    for word, val in tfBagOfWords.items():
        tfidf[word] = val * idfs[word]
    return tfidf

"""
Read twitter csv data downloaded by Scweet - https://github.com/Altimis/Scweet
The csv file contains columns - UserScreenName,UserName,Timestamp,Text,Emojis,Comments,Likes,Retweets,Image link,Tweet URL
"""
def read_file(path):
    twitter_data_frame = pd.read_csv(path)
 
    print('Print example data after reading the csv file')
    print(twitter_data_frame.head())
    return twitter_data_frame

from nltk.corpus import wordnet
def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    # if the pos_tag of the word cannot be matched in tag_dict, then define it as the defalut 'wordnet.NOUN'
    return tag_dict.get(tag, wordnet.NOUN)    

"""
Tokenize and add column final_token for every line in file
This method excludes all non-english words and meaningless stops
"""
def tokenize_and_add_column(twitter_data_frame):
    wl = WordNetLemmatizer()
    final_tokens_list = []

    # Loop Text column of every line, which is the content of each Tweet
    for line in twitter_data_frame['Text']:
        # Genereate tokens from raw content
        tokens = word_tokenize(line)
        # Filter non-english words
        english_words = [word for word in tokens if word.isalpha()]
        # Filter stop words like for, do, an, etc
        tags = nltk.pos_tag(english_words)
        final_tokens = [word for word, pos in tags if not word.lower() in set(stopwords.words('english'))]
        final_tokens = [wl.lemmatize(word, get_wordnet_pos(word)) for word in final_tokens]
    
        final_tokens_list.append(final_tokens)
    
    # Add final_token column for each line
    twitter_data_frame['final_token'] = pd.Series(final_tokens_list)
    
    print("*****************************")
    print('Print example tokenized twitter text of first row')
    print(twitter_data_frame['final_token'][0])
    return twitter_data_frame

"""
Must be called after tokenize_and_add_column
Calculation based on final_token column data and generate the tfdif column
"""
def calculate_tfidf_and_add_column(twitter_data_frame):
    # Get words SET of all tweets
    words = []
    for line in twitter_data_frame['final_token']:
        words.extend(line)
    uniquewords = set(words)
    
    all_number_of_words = []
    all_tf = []
    # Loop final_token column of every line, which is generated by tokenize_and_add_column method
    for line in twitter_data_frame['final_token']:
        # Count words exists
        numberOfWords = dict.fromkeys(set(line), 0)
        for word in line:
            numberOfWords[word] += 1
        all_number_of_words.append(numberOfWords)

        # Calculate term frequency of tokens of this tweet
        tf = computeTF(numberOfWords, line)
        all_tf.append(tf)
    
    # Calculate Inverse Data Frequency of each word exists in all tweets
    idfs = computeIDF(all_number_of_words, uniquewords)
    
    tfidfs = []
    
    # calculate tfdif of every tweet
    for tf in all_tf:
        tfidfs.append(computeTFIDF(tf, idfs))
    # Add tfdif column for each line   tfdif is the list of dict
    twitter_data_frame['tfidf'] = pd.Series(tfidfs)
        
    print("*****************************")
    print('Print example tfidf of first row')
    print(twitter_data_frame['tfidf'][0])
    return twitter_data_frame