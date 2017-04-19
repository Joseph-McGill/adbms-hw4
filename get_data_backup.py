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

# Class representing a book
class Book:
    
    # Book constructor
    def __init__(self, author, pub_date, text, words):
        self.author = author
        self.pub_date = pub_date
        self.text = text
        self.words = words


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
    
    # try to download the book until successful 
    downloaded = False
    while(not downloaded):
        try:
            urlretrieve(url, file_name)
            print("Downloading book %d" % book_num)
            downloaded = True
            
        except HTTPError as err:
            print("Download failed, retrying book %d" % book_num)
            pass

    # set the url and get the HTML for BeautifulSoup to parse
    html = urlopen("http://www.gutenberg.org/ebooks/" + str(i)).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # parse the author from the html page
    author = soup.find(itemprop="creator")
    
    # parse the date from the html page
    raw_date = soup.find(itemprop="datePublished")
    date = datetime.strptime(raw_date.get_text(), '%b %d, %Y')
    
    # return the book object
    return Book(author, date,)
        
        
# Main Function
def main():

    books = []
    # download the books from project gutenberg
    for book_num in range(1, 51):
        books.append(get_book(book_num))
        
  
# get author information from the webpages         
if False:

    # get the author information for each book
    for i in range(1, 51):
    
        # set the url and get the HTML for BeautifulSoup to parse
        html = urlopen("http://www.gutenberg.org/ebooks/" + str(i)).read()
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find(itemprop="creator")
        date = soup.find(itemprop="datePublished")
        out_str = ""
        if results is not None:
            out_str += "Book " + str(i) + " author: " + results.get_text()
        
        else:
            out_str += "No author found"
        
        if date is not None:
            date = datetime.strptime(date.get_text(), '%b %d, %Y')
            #dates.append(date)
            out_str += " Date: " + str(date)
            
        else:
            out_str += " No date found"
            
        print(out_str)
# remove stop words from the downloaded books        
if False:

    SIMILARITY_THRESHOLD = float(input('Enter a threshold value: '))
    # get the stop words from a text file
    with open('stopwords.txt', 'r') as in_file:
        stop_words = in_file.readlines()
        stop_words = set([word.strip() for word in stop_words])
    
    
    #TODO handle punctuation
    # remove stop words from each book
    word_set = set()
    books = []
    regex = re.compile('[^a-zA-Z]')
    for i in range(1, 51):
        
        # splt the book into words and remove stop words
        with codecs.open('books/book' + str(i) + '.txt', encoding='latin-1') as book:
            book_text = regex.sub(' ', book.read().lower())
            book_words = word_tokenize(book_text)
            book_words = [word for word in book_words if word not in stop_words]
            books.append(book_words)
            word_set |= set(book_words)
    
    # turn the set of all words into a sorted list
    word_list = sorted(list(word_set))
    
    # create the word vectors
    vectors = [[0] * len(word_list) for i in range(50)]
    
        
    for i, book in enumerate(books):
        counts = Counter(book)
        
        for j, word in enumerate(word_list):
            vectors[i][j] = counts[word]
    
    #for i in range(len(vectors[0])):
    #    print("%d : %d" % (vectors[0][i], vectors[1][i]))
    for i in range(len(vectors)):
        for j in range(len(vectors)):
            similarity = 1 - spatial.distance.cosine(vectors[i], vectors[j])
            if similarity >= SIMILARITY_THRESHOLD and i is not j:
              print("Book %d, Book %d: %f" % (i+1, j+1, similarity))
          
# Run the main function  
if __name__ == '__main__':
    main()
