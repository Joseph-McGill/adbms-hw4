#!/usr/bin/env python3

from urllib.request import urlretrieve
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import codecs
import re
import string
import nltk
from collections import Counter
from nltk.tokenize import word_tokenize, sent_tokenize
from scipy import spatial
from datetime import datetime
import os.path
import numpy as np

### GLOBAL VARIABLES ### #TODO
# Stop words
with open('stopwords.txt', 'r') as in_file:
    STOP_WORDS = set([word.strip() for word in in_file.readlines()])

# Regex to remove non alphanumeric characters
REGEX = re.compile('[^a-zA-Z]')        

# Threshold for the similarity
#SIMILARITY_THRESHOLD = float(input('Enter a threshold value: '))
SIMILARITY_THRESHOLD = 0.75 #TODO

# Class representing a book
class Book:
    
    # Book constructor
    def __init__(self, book_num, author, pub_date, text, words):
        self.book_num = book_num
        self.author = author
        self.pub_date = pub_date
        self.text = text
        self.words = words
        self.vector = None
    
    # to string method for the object
    def __str__(self):
        return ("--- Book %d ---\nAuthor: %s\nPub_date: %s\nWord count: %d\n" 
                % (self.book_num, self.author, self.pub_date, len(self.words)))


# Function to download the given book number from project gutenberg
def get_book(book_num):
    
    # set the url and file name for the book to download
    # file_name: books/book<book_num>.txt
    # url = http://www.gutenberg.org/files/<book_num>/<book_num>.txt
    file_name = 'books/book' + str(book_num) + '.txt'
    
    # book 40 does not have an associated text file
    if book_num is 40:
        url = 'http://www.gutenberg.org/files/51/51.txt'
    
    else:
        url = 'http://www.gutenberg.org/files/' + str(book_num) +'/' + str(book_num) + '.txt'
    
    # if the file exists, don't download it again
    downloaded = True if os.path.isfile(file_name) else False
        
    # try to download the book until successful 
    while(not downloaded):
        try:
            urlretrieve(url, file_name)
            print("Downloading book %d" % book_num)
            downloaded = True
            
        except HTTPError as err:
            print("Download failed, retrying book %d" % book_num)
            pass
            
    if False: #TODO
        # set the url and get the HTML for BeautifulSoup to parse
        html = urlopen("http://www.gutenberg.org/ebooks/" + str(book_num)).read()
        soup = BeautifulSoup(html, 'html.parser')
        
        # parse the author from the html page
        creator = soup.find(itemprop="creator")
        author = creator.get_text() if creator is not None else "None"
        
        # parse the date from the html page
        raw_date = soup.find(itemprop="datePublished")
        pub_date = datetime.strptime(raw_date.get_text(), '%b %d, %Y')
    
    #TODO
    pub_date = "date"
    author = "author"
    
    # get the book's text from the downloaded file
    with codecs.open(file_name, encoding='latin-1') as book:
        
        # get the full text
        text = book.read()
        
        # remove non alphanumerics and stop words
        words = word_tokenize(REGEX.sub(' ', text.lower()))
        words = [word for word in words if word not in STOP_WORDS]
        
    # return the book object
    return Book(book_num, author, pub_date, text, words)
        
      
# Main Function
def main():
    
    # download the books from project gutenberg
    books = []
    for book_num in range(1, 51):
        books.append(get_book(book_num))
        
    word_set = set() 
    for book in books:
        word_set |= set(book.words)
        
    # turn the set of all words into a sorted list
    word_list = sorted(list(word_set))
    
    for book in books:
        counts = Counter(book.words)
        
        vector = [0 for i in range(len(word_list))]
        
        for j, word in enumerate(word_list):
            vector[j] = counts[word]      
        
        book.vector = vector
    
    for i in range(len(books)):
        for j in range(len(books)):
            similarity = 1 - spatial.distance.cosine(books[i].vector, books[j].vector)
            if (similarity >= SIMILARITY_THRESHOLD and
                books[i].pub_date <= books[j].pub_date and i is not j):
              print("Book %d, Book %d: %f" % (i+1, j+1, similarity))
            
    #for i in range(len(word_list)):
    #    print("%s -> %d : %d" % (word_list[i], books[0].vector[i], books[1].vector[i])) 

           
# Run the main function  
if __name__ == '__main__':
    main()
