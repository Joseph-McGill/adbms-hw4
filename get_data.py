#!/usr/bin/env python3

import re
import os.path
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
from nltk.tokenize import word_tokenize
from scipy import spatial
from urllib.request import urlretrieve
from urllib.request import urlopen
from urllib.error import HTTPError


### GLOBAL VARIABLES ###
# Stop words
with open('stopwords.txt', 'r') as in_file:
    STOP_WORDS = set([word.strip() for word in in_file.readlines()])

# Regex to remove non alphanumeric characters
REGEX = re.compile('[^a-zA-Z]')        

# Threshold for the similarity
SIMILARITY_THRESHOLD = float(input('Enter a threshold value: '))


# Class representing a book
class Book:
    
    # Book constructor
    def __init__(self, book_num, title, author_name, author_birth_year, pub_date, text, words):
        self.book_num = book_num
        self.title = title
        self.author_name = author_name
        self.author_birth_year = author_birth_year
        self.pub_date = pub_date
        self.text = text
        self.words = words
        self.vector = None
    
    # to string method for the object
    def __str__(self):
        return ("--- Book %d ---\nAuthor: %s\nPub_date: %s\nWord count: %d\n" 
                % (self.book_num, self.author_name, self.pub_date, len(self.words)))


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
        
    # set the url and get the HTML for BeautifulSoup to parse
    html = urlopen("http://www.gutenberg.org/ebooks/" + str(book_num)).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # parse the author from the html page
    raw_author = soup.find(itemprop="creator")
    author = raw_author.get_text() if raw_author is not None else None
    
    # set the author info to None if none is found
    if author is not None:
    
        # get the author's name 
        author_name = re.search(r'[^\d]+', author).group(0).strip(', ')
        
        # get the author's birth year
        years = re.findall('\d+', author)
        author_birth_year = years[0] if len(years) > 0 else None
    
    else:
        author_name = None
        author_birth_year = None
        
    # parse the date from the html page
    raw_date = soup.find(itemprop="datePublished")
    pub_date = datetime.strptime(raw_date.get_text(), '%b %d, %Y')
    
    # parse the book title from the html page
    raw_title = soup.find(itemprop="name")
    title = raw_title.get_text() if raw_title is not None else None
    regex_title = re.search(r'(.*) by\b', title)
    
    if regex_title is not None:
        title = regex_title.group(1)
        
    # get the book's text from the downloaded file
    with open(file_name, 'r') as book:
        
        # get the full text
        text = book.read()
        
        # remove non alphanumerics and stop words
        words = word_tokenize(REGEX.sub(' ', text.lower()))
        words = [word for word in words if word not in STOP_WORDS]
        
    # return the book object
    return Book(book_num, title, author_name, author_birth_year, pub_date, text, words)


# Function to calculate and print the book similarities to a file
def print_similarities(books):

    # create a set of the distinct words from every book
    word_set = set() 
    for book in books:
        word_set |= set(book.words)
        
    # turn the set of all words into a sorted list
    word_list = sorted(list(word_set))
    
    # create the weight vectors for each book
    for book in books:
        counts = Counter(book.words)
        
        vector = [0 for i in range(len(word_list))]
        
        for j, word in enumerate(word_list):
            vector[j] = counts[word]      
        
        book.vector = vector
    
    # calculate and print the cosine similartiy values
    with open('similarities.txt', 'w') as out:
        for i in range(len(books)):
            for j in range(len(books)):
                similarity = 1 - spatial.distance.cosine(books[i].vector, books[j].vector)
                if (similarity >= SIMILARITY_THRESHOLD and
                    books[i].pub_date <= books[j].pub_date and i is not j):
                  out.write("%d\t%d\t%f\n" % (i+1, j+1, similarity))


# Function to print the authors of the books to a file
def print_authors(books):

    # get a list of the unique authors
    author_set = set()
    for book in books:
        if (book.author_name is not None):
            author_set.add((book.author_name, book.author_birth_year))
    
    # extract the author information  
    with open('authors.txt', 'w') as out:
        author_id = 1 
        for author in author_set:
            out.write("%d\t%s\t%s\n" % (author_id, author[0], author[1]))
            author_id += 1      


# Function to print the book information to a file
def print_books(books):
    
    with open('books.txt', 'w') as out:
        for book in books:
            out.write("%d\t%s\t%s\t%s\n" % 
            (book.book_num, book.title, book.author_name, 
            book.pub_date.strftime("%Y-%m-%d")))
   
    
# Main Function
def main():
    
    # download the books from project gutenberg
    books = []
    for book_num in range(1, 51):
        books.append(get_book(book_num))
    
    # calculate the cosine similarities between 
    # the books and print them to a file
    print_similarities(books)
    
    # print the author information to a file 
    print_authors(books)
    
    # print the book information to a file
    print_books(books)
 
                
# Run the main function  
if __name__ == '__main__':
    main()
