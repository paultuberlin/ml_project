import re
from nltk import snowball
from nltk.corpus import stopwords
from nltk import word_tokenize
import numpy
import enchant

""" This file contains only filters, those are methods that have as a input and output either a
list of strings, or just a string. Such methods are ment to remove unnecessaire elements, or filter 
information in another way (e.g. by stemming).
"""

def std_filters():
    """This method retuns a arguments dictionary with standart filters. """
    kwargs = {
        "sentence_filters":[punctuation_filter],
        "word_filters":[small_word_filter, stopword_filter, stemming_filter]
    }
    return kwargs

def run_filters_sentence(raw_documents, sentence_filters):
    documents = []
    for d in raw_documents:
        for filt in sentence_filters:
            d = filt(d)
        d = word_tokenize(d)
        documents += [d]
    return documents

def run_filters_words(documents, word_filters):
    new_documents = []
    for d in documents:
        for filt in word_filters:
            d = filt(d)
        new_documents += [d]
    return new_documents

def run_filters(raw_documents, sentence_filters, word_filters):
    documents = []
    for d in raw_documents:
        if type(d) in [str, numpy.str_]:
            for filt in sentence_filters: d = filt(d)
            d = word_tokenize(d)
        if type(d) == list:
            for filt in word_filters: d = filt(d)
        documents += [d]
    return documents

def punctuation_filter(sentence):
    """A simple filter that essentialy substitutes punctuation symbols by whitespaces and at the same
    time gets track of seqqences of severeal whitespaces. Also substitutes '&' by 'und'. It returns a
    sting.
    
    Key Argument:
    sentence -- must be a single string
    """
    filtered_sentence = sentence
    regexps = [(r"[.!?,\-()\[\]\\]", " "),
                (r"&", "und"),
                (r" {2,}", " ")]
    for find, replace in regexps:
        filtered_sentence = re.sub(find, replace, filtered_sentence)
    
    return filtered_sentence
    
def small_word_filter(words, min_=1):
    """This filter removes very small words given list of words. Words are small if they contain less
    or equal then min. 
    """
    new_words = []
    for w in words:
        if(len(w) > min_):
            new_words += [w]
    return new_words
    
def year_tracker(words):
    """This filter tries to find numbersequence that represent years, hower it ristricts itself to find
    years in the range 1700-2199."""
    new_words = []
    for w in words:
        new_word = re.sub(r"^[1][789][0-9]{2}$", "jahreszahl", w) # for 1700-1999
        new_word = re.sub(r"^[2][01][0-9]{2}$", "jahreszahl", new_word) # for 2000-2199
        new_words += [new_word]
    return new_words

def lower_case(words):
    return [w.lower() for w in words]

def stemming_filter(words):
    """This filter essentally executes stemming which is adapted from the snwoball package of nltk.
    Not that as input one has to hand in a already tokenized sentence, i.e. a list of strings, rather
    than a single string."""
    stemmer = snowball.GermanStemmer()
    return [stemmer.stem(w) for w in words]

def stopword_filter(words):
    """Thise method removes all stopwords/functionwords contained in nltk.corpus.stopwords.words('german')"""
    new_words = []
    for w in words:
        if w in stopwords.words("german"): continue
        else: new_words += [w]
    return new_words

def spell_corrector(words):
    """This method check for each string in the list words, wheather it is contained in the german or english
    dictionary. If it is not contained in neither of them, the word is replaced by the first suggestion of the
    german dictionary. Should be run before applying other filters.
    """
    de = enchant.Dict("de_DE")
    en = enchant.Dict("en_GB")
    new_words = []
    for w in words:
        if ( de.check(w) | en.check(w) ):
            new_words += [ w ]
        else:
            sug = de.suggest(w)
            if len(sug) > 0: new_words += [ sug[0] ]
            else: new_words += [ w ]
    return new_words