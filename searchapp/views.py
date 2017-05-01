from django.shortcuts import render,render_to_response
import json
from .models import Document,Inverted_Index_Element,SoundexTerm,BiGramTerm
from django.http import HttpResponse,HttpResponseRedirect
from.models import WebSiteCrawler,Document
from django.core.paginator import Paginator
# Create your views here.

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *
import string


def search(request):
    try :
        if request.GET:
            page = request.GET.get('page', 1)
            term=request.GET['q']
            if request.GET.get("soundex",None) and request.GET.get("soundex",None)!="None":
                print("soundex")
                sound = get_soundex(term)
                print(sound)
                all_soundex = SoundexTerm.objects.get(soundex=sound)
                docs =[]
                print(all_soundex)
                print("all : ",all_soundex.terms)
                word_list = all_soundex.terms.split(",")

                for word in word_list:
                    ## limit of returned documents
                    if len(docs) > 150:
                        break
                    inverted_list = Inverted_Index_Element.objects.filter(term=word)
                    for inv in inverted_list:
                        doc = Document.objects.get(pk=inv.doc_id)
                        if doc not in docs:
                            docs.append(doc)
                for word in word_list:
                    l = list(Document.objects.filter(title__icontains=word))
                    for d in l:
                        docs.insert(0, d)

            elif request.GET.get("correction",None) and request.GET.get("correction",None)!="None":
                print("correction")
                ret = correct(term,request)
                return render_to_response("result.html",ret )


            elif '"' in term:
                term=term.strip('"')
                docs = get_documents(term, True)

            else:
                docs = MultiKeywordSearch(term)
                if docs ==[]:
                    ret = correct(term,request)
                    return render_to_response("result.html", ret)

            print("term " ,term)
            pages = Paginator(docs,15)
            docs = pages.page(page)
            return render_to_response("result.html",{"docs":docs,"term":term,"soundex":request.GET.get("soundex",None),"correction":request.GET.get("correction",None)})
        else:
            return render_to_response('search.html')
    except Exception as e:
        return HttpResponse("<h2>error</h2><br>"+str(e))

def correct(term,request):
    bigrams = get_bigram(term)
    print(bigrams)
    print(len(bigrams))
    all_terms = []
    for bi in bigrams:
        print(bi)
        terms = BiGramTerm.objects.get(bigram=bi).terms.split(",")
        print("terms : ", terms, str(len(terms)))
        for t in terms:
            if t not in all_terms and checkBiGram(term, t):
                print("t : ", t)
                all_terms.append(t)
    print("all : ", all_terms)
    print(len(all_terms))
    ### will add edite distance
    distance = dict()
    mini_dsitance = 50
    min_term = ""
    for t in all_terms:
        distance[t] = EditDistance(t, term)
        print(t, distance[t])
        if mini_dsitance > distance[t]:
            mini_dsitance = distance[t]
            min_term = t
    print(min_term)
    docs = []

    result_terms = []
    for t in distance:
        print(t)
        print(distance[t])
        if distance[t] == mini_dsitance:
            result_terms.append(t)
    print("result : ", result_terms)
    return {"docs": docs, "result_terms": result_terms,"term":term,"soundex":request.GET.get("soundex",None),"correction":request.GET.get("correction",None)}



def MultiKeywordSearch(keyword):
    print("MultiKeywordSearch ",keyword)
    word_list = preproccess(keyword)
    docs=get_documents(keyword)
    """
    for word in word_list:
        inverted_list=Inverted_Index_Element.objects.filter(term=word)
        for inv in inverted_list :
            print(inv.doc_id)
            docs.append(Document.objects.get(pk=inv.doc_id))
    """
    ## call ranking function !!
    # then add in start all documents have term in title

    for word in word_list:
        l = list(Document.objects.filter(title__icontains=word))
        print(l)
        for d in l :
            docs.insert(0,d)
    return docs

def get_documents(keyword,exact= False):
    word_list = preproccess(keyword)
    all_inverted_list=[]
    big_list=[]
    for word in word_list:
        inverted_list=Inverted_Index_Element.objects.filter(term=word)
        all_inverted_list.append(inverted_list)
        docs_id_list=[]
        for i in inverted_list:
            docs_id_list.append(i.doc_id)
        big_list.append(docs_id_list)
    intersect=big_list[0]
    for i in range(len(big_list)):
        intersect = list(set(big_list[i]) & set(intersect))
    docs=list(Document.objects.filter(id__in=intersect))
    print(docs)
    if not exact :
        return docs





def EditDistance(word1,word2):
    m = len(word1)
    n = len(word2)
    Matrix = [[0 for x in range(n+1)] for y in range(m+1)]
    for i in range(0,m+1):
        Matrix[i][0] = i
    for i in range(0,n+1):
        Matrix[0][i] = i
    for i in range(1,m+1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                Matrix[i][j] = Matrix[i-1][j-1]
            else:
                Matrix[i][j] = 1 + min(Matrix[i][j - 1], Matrix[i - 1][j], Matrix[i - 1][j - 1])
    return Matrix[m][n]

def get_bigram(word):
    word = '$' + word + '$'
    count = 0
    length = len(word)
    list = []
    while count < length and count != length-1:
        list.append(word[count] + word[count+1])
        count += 1
    return list


def checkBiGram(word1,word2):
    list_word1 = get_bigram(word1)
    list_word2 = get_bigram(word2)
    intersect = list(set(list_word1) & set(list_word2))
    intersect_len = len(intersect)
    union = list_word1+list_word2
    union_len = len(union)
    JC = intersect_len / (union_len-intersect_len)



    if JC >= 0.45:
        return True
    else:
        return False



def preproccess(text):
    punc = string.punctuation + "^"
    text = text.lower()
    for p in punc:
        text = text.replace(p, "")
    word_list = word_tokenize(text)
    stemmer = PorterStemmer()
    return_list=[]

    for word in word_list:
        try:
            return_list.append(stemmer.stem(word))
        except:
            continue
    return return_list

def EditDistance(word1,word2):
    m = len(word1)
    n = len(word2)
    Matrix = [[0 for x in range(n+1)] for y in range(m+1)]
    for i in range(0,m+1):
        Matrix[i][0] = i
    for i in range(0,n+1):
        Matrix[0][i] = i
    for i in range(1,m+1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                Matrix[i][j] = Matrix[i-1][j-1]
            else:
                Matrix[i][j] = 1 + min(Matrix[i][j - 1], Matrix[i - 1][j], Matrix[i - 1][j - 1])
    return Matrix[m][n]

def get_soundex(word):
    new_word = word[0] + ""
    for i in range(1,len(word)):
        if word[i] == 'a' or word[i] == 'e' or word[i] == 'i'or word[i] == 'o' or word[i] == 'u'or word[i] == 'h'or word[i] == 'w' or word[i] == 'y':
            new_word += '0'
        elif word[i] == 'b' or word[i] == 'f' or word[i] == 'p'or word[i] == 'v':
            new_word += '1'
        elif word[i] == 'c' or word[i] == 'g' or word[i] == 'j' or word[i] == 'k' or word[i] == 'q' or word[i] == 's' or word[i] == 'x' or word[i] == 'z':
            new_word += '2'
        elif word[i] == 'd' or word[i] == 't':
            new_word +='3'
        elif word[i] == 'l':
            new_word += '4'
        elif word[i] == 'm' or word[i] == 'n':
            new_word += '5'
        elif word[i]=='r':
            new_word += '6'
    prev = '$'
    word_unique = ""
    for i in range(0,len(new_word)):
        if prev != new_word[i]:
            word_unique += new_word[i]
        prev = new_word[i]

    #remove zeros
    word_filtered = ""
    for i in range(0,len(word_unique)):
        if word_unique[i] != '0':
            word_filtered += word_unique[i]

    word_returned = word_filtered
    if len(word_filtered) > 4:
        word_returned = word_filtered[0:4]
    elif len(word_filtered) < 4:
        for i in range(len(word_filtered),4):
            word_returned += "0"
    return word_returned


def index(request):
    return HttpResponse("Hello, world. You're at the search index.")
def crawl(request):

    webs = WebSiteCrawler.objects.all()
    for w in webs:
        w.crawl()
def get_terms(request):
    docs = Document.objects.all()
    for doc in docs[291:600]:
        doc.get_terms()
        print(doc.pk)
def get_index(request):
    docs = Document.objects.all()
    for doc in docs [292:]:
        inverted = doc.get_index()
        print(doc.pk)

    return HttpResponse(str(inverted))
