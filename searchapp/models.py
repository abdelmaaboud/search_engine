from django.db import models
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from nltk.stem.porter import *


# Create your models here.
class WebSiteCrawler(models.Model):
    url =  models.URLField(max_length=1000)
    title = models.CharField(max_length=300)
    max_pages = models.IntegerField()
    def __str__(self):
        return self.title



    def crawl(self):

        if "http" in self.url:
            self.base_url = self.url.split("//")[1]
        self.all_links=[self.url]
        j = 0

        while len(self.all_links) < self.max_pages:
            url = self.all_links[j]
            self.get_all_href(url)
            j += 1
            print(j)
        print("to save")
        for link in self.all_links:
            print("save :" ,url)
            self.save_url(link)

        #get all urls from the
    def get_all_href(self,url):
        text = requests.get(url).text
        soup = BeautifulSoup(text, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            href = link.get("href")
            if href is None:
                continue
            if '#' in href:
                continue
            if 'http' not in href or "//" not in href:
                href = urljoin(url, href)
                if href not in self.all_links:
                    if self.base_url in href:
                        self.all_links.append(href)
                        print("a7a")
                        print(href)
            if len(self.all_links) > self.max_pages:
                return

    def save_url(self,url):
        print(url)
        req = requests.get(url)
        type = req.headers.get('content-type')
        if "text/html" not in type:
            print(type, url)
            return
        text = req.text
        soup = BeautifulSoup(text, 'html.parser')
        title = soup.find('title').string
        if title is None:
            return
        for script in soup(["script", "style"]):
            script.extract()
        if self.base_url in url:
            soup = soup.find("div",{"id" :"content"})
        #soup = soup.find("div", attrs={"id": "content"})
        if soup is None:
            return
        text = soup.getText().strip()
        doc= Document.objects.create(url=url,title=title,text=text)

        #doc.save()
        print("saving ... ", url)

class Inverted_Index_Element(models.Model):
    term = models.CharField(max_length=200)
    doc_id = models.IntegerField()
    freq = models.IntegerField()
    positions = models.TextField()
    def __str__(self):
        return self.term+ "  / " + str(self.doc_id) + "  /  " + str(self.freq)


class Document(models.Model):
    url =  models.URLField(max_length=1000)
    title = models.CharField(max_length=300)
    text = models.TextField()
    def __str__(self):
        return self.title

    def get_index(self):
        punc = string.punctuation + "^"

        inverted_dic = dict()
        text = self.text.lower()
        for p in punc:
            text = text.replace(p, "")
        word_list = word_tokenize(text)
        p = re.compile("^(?=.*[a-z]).+$")

        print(word_list)
        for i in range(len(word_list)):
            try :
                if word_list[i] in stopwords.words('english'):
                    continue
                if p.findall(word_list[i]) == []:
                    continue
                stemmer = PorterStemmer()
                word = stemmer.stem(word_list[i])

                if word in inverted_dic:
                    inverted_dic[word]["freq"] += 1
                    inverted_dic[word]["positions"].append(i)

                else:
                    dic = dict()
                    dic["freq"] = 1
                    dic["positions"] = [i]
                    inverted_dic[word] = dic
            except Exception as e:
                print(str(e))
                continue
        print(inverted_dic)
        for key in inverted_dic:
            try:
                inv = Inverted_Index_Element(  term=key,freq=inverted_dic[key]["freq"],positions=inverted_dic[key]["positions"],doc_id=self.pk)
                inv.save()
            except :
                continue


        return inverted_dic
    def get_terms(self):
        punc = string.punctuation + "^"
        terms_dic = dict()
        text = self.text.lower()
        for p in punc:
            text = text.replace(p, "")
        word_list = word_tokenize(text)
        filtered_words = [word for word in word_list if word not in stopwords.words('english')]
        p = re.compile("^(?=.*[a-z]).+$")
        for i in range(len(filtered_words)):
            if p.findall(filtered_words[i]) == []:
                continue
            if filtered_words[i] in terms_dic:
                terms_dic[filtered_words[i]]["freq"] += 1
            else:
                dic = dict()
                dic["freq"] = 1
                #dic["positions"] = [i]
                terms_dic[filtered_words[i]] = dic
        print(terms_dic)
        for key in terms_dic:
            term = Term( term=key,freq=terms_dic[key]["freq"],doc_id=self.pk)
            term.save()

        return terms_dic

class Term(models.Model):
        term = models.CharField(max_length=200)
        doc_id = models.IntegerField()
        freq = models.IntegerField()

        def __str__(self):
            return self.term + "  / " + str(self.doc_id) + "  /  " + str(self.freq)


class DistencitTerm(models.Model):
    term = models.CharField(max_length=200)

    def __str__(self):
        return self.term
class SoundexTerm(models.Model):
    soundex = models.CharField(max_length=10)
    terms = models.TextField()

    def __str__(self):
        return self.soundex
class BiGramTerm(models.Model):
    bigram = models.CharField(max_length=10)
    terms = models.TextField()

    def __str__(self):
        return self.bigram