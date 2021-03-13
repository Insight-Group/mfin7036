import pandas as pd
import re
import string
import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize


"""
Tokenize and add column final_token for every tweet in file
This method excludes all non-english words and meaningless stops
"""
def tokenize_and_add_column(twitter_data_frame):
    wl = WordNetLemmatizer()
    word_tokens_column = []
    sent_tokens_column = []
    processed_text_column = []

    # Loop Text column of every tweet, which is the content of each Tweet
    for tweet in twitter_data_frame['Text']:
        # Remove urls
        tweet = re.sub(r"http\S+|www\S+|https\S+", '', tweet, flags=re.MULTILINE)
        # Remove user @ references and '#' from tweet
        tweet = re.sub(r'\@\w+|\#','', tweet)
        # Remove punctuations
        tweet = tweet.translate(str.maketrans('', '', string.punctuation))
        # Generate tokens
        words = word_tokenize(tweet)
        sents = sent_tokenize(tweet)
        # Filter out non-english words
        english_words = [word for word in words if word.encode().isalpha()]
        # Filter out stopwords like for, do, an, etc
        tags = nltk.pos_tag(english_words)
        nonstop_words = [word for word, pos in tags if not word.lower() in set(stopwords.words('english'))]
        word_tokens = [wl.lemmatize(word, get_wordnet_pos(word)) for word in nonstop_words]

        word_tokens_column.append(word_tokens)
        sent_tokens_column.append(sents)
        
        if len(word_tokens) == 0:
            processed_text_column.append("without useful information")
        else:
            processed_text_column.append(" ".join(word_tokens))
    
    # Add columns for each tweet - three types of processed data
    twitter_data_frame['word_tokens'] = pd.Series(word_tokens_column)        
    twitter_data_frame['sent_tokens'] = pd.Series(sent_tokens_column)
    twitter_data_frame['processed_text'] = pd.Series(processed_text_column)
    
    return twitter_data_frame

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
Must be called after tokenize_and_add_column
Calculation based on word_tokens column data and generate the tfdif column
"""
def calculate_tfidf_and_add_column(twitter_data_frame):
    # Get words SET of all tweets
    words = []
    for tweet in twitter_data_frame['word_tokens']:
        words.extend(tweet)
    uniquewords = set(words)
    
    all_number_of_words = []
    all_tf = []
    # Loop word_tokens column of every tweet, which is generated by tokenize_and_add_column method
    for tweet in twitter_data_frame['word_tokens']:
        # Count words exists
        numberOfWords = dict.fromkeys(set(tweet), 0)
        for word in tweet:
            numberOfWords[word] += 1
        all_number_of_words.append(numberOfWords)

        # Calculate term frequency of tokens of this tweet
        tf = computeTF(numberOfWords, tweet)
        all_tf.append(tf)
    
    # Calculate Inverse Data Frequency of each word exists in all tweets
    idfs = computeIDF(all_number_of_words, uniquewords)
    
    tfidfs = []
    
    # calculate tfdif of every tweet
    for tf in all_tf:
        tfidfs.append(computeTFIDF(tf, idfs))
    # Add tfdif column for each tweet, tfdif is the list of dict
    twitter_data_frame['tfidf'] = pd.Series(tfidfs)
        
    return twitter_data_frame


# The follwing three definations can be replaced by build-in function TfidfVectorizer
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
        tfidf[word.lower()] = val * idfs[word]
    return tfidf


