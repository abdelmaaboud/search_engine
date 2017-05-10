from django.shortcuts import render,render_to_response,HttpResponse
from twisted.conch.insults.insults import privateModes
from .models import Document,Inverted_Index_Element,SoundexTerm,BiGramTerm
from django.core.paginator import Paginator
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *
import string
def search(request):
    try :
        if request.GET:
            page = request.GET.get('page', 1)
            term=request.GET['q'].lower().strip()
            if term=="":
                return render_to_response('search.html')
            #exact
            elif '"' in term:
                t=term.strip('"')
                docs = get_documents(t, True)
                return render_to_response("result.html",
                                          {"docs": docs, "term": term, "soundex": request.GET.get("soundex", None),
                                           "correction": request.GET.get("correction", None)})
            #soundex
            if request.GET.get("soundex",None) and request.GET.get("soundex",None)!="None":
                #ret = get_soundex_documents(term,request)
                ret = get_soundex_terms(term,request)

                return render_to_response("result.html", ret)



            #spelling correction
            elif request.GET.get("correction",None) and request.GET.get("correction",None)!="None":
                ret = correct(term,request)
                return render_to_response("result.html",ret )
            #multi keyword
            else:
                docs = MultiKeywordSearch(term)
                if docs ==[]:
                    ret = correct(term,request)
                    return render_to_response("result.html", ret)
            #split documents to pages
            pages = Paginator(docs,15)
            docs = pages.page(page)
            return render_to_response("result.html",{"docs":docs,"term":term,"soundex":request.GET.get("soundex",None),"correction":request.GET.get("correction",None)})
        else:
            return render_to_response('search.html')
    except Exception as e:
        return HttpResponse("<h2>error</h2><br>"+str(e))
def get_soundex_terms(term,request):
    docs = []
    word_list = word_tokenize(term)
    if len(word_list) == 1:
        sound = get_soundex(term)
        print(sound)
        all_soundex = SoundexTerm.objects.get(soundex=sound)
        docs = []
        result_terms = all_soundex.terms.split(",")
        print(result_terms)
    else:
        corriction_list = []
        for word in word_list:
            sound = get_soundex(word)
            corriction_list.append(SoundexTerm.objects.get(soundex=sound).terms.split(","))
            print(corriction_list)
        first_list = corriction_list[0]
        for i in range(1, len(corriction_list)):
            first_list = get_words_combination(first_list, corriction_list[i])
            print(first_list)
        result_terms = first_list
    return {"docs": docs, "result_terms": result_terms, "term": term,
                "soundex": request.GET.get("soundex", None),
                "correction": request.GET.get("correction", None)}
def get_soundex_documents(term,request):
    sound = get_soundex(term)
    print(sound)
    all_soundex = SoundexTerm.objects.get(soundex=sound)
    docs = []
    word_list = all_soundex.terms.split(",")
    print(word_list)
    for word in word_list:
        ## limit of returned documents
        if len(docs) > 200:
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

    return {"docs": docs, "term": term,
                "soundex": request.GET.get("soundex", None),
                "correction": request.GET.get("correction", None)}

def correct(term,request):
    docs = []
    word_list = word_tokenize(term)
    if len(word_list) > 1 :
        corriction_list=[]
        for word in word_list:
            corriction_list.append(get_correction_terms(word))
            print(corriction_list)
        first_list = corriction_list[0]
        for i in range(1,len(corriction_list)):
            first_list= get_words_combination(first_list, corriction_list[i])
            print(first_list)
        result_terms = first_list
        return {"docs": docs, "result_terms": result_terms,"term":term,"soundex":request.GET.get("soundex",None),"correction":request.GET.get("correction",None)}

    else :
        result_terms = get_correction_terms(term)

        return {"docs": docs, "result_terms": result_terms,"term":term,"soundex":request.GET.get("soundex",None),"correction":request.GET.get("correction",None)}
def get_words_combination(list1,list2):
    result = []
    for i in list1:
        for j in list2:
            result.append(i+" "+ j)
    print(result)
    return result

def get_correction_terms(term):
    bigrams = get_bigram(term)
    all_terms = []
    for bi in bigrams:
        print(bi)
        terms = BiGramTerm.objects.get(bigram=bi).terms.split(",")
        for t in terms:
            if t not in all_terms and checkBiGram(term, t):
                all_terms.append(t)
    ### will add edite distance
    distance = dict()
    mini_dsitance = 50
    for t in all_terms:
        distance[t] = EditDistance(t, term)
        if mini_dsitance > distance[t]:
            mini_dsitance = distance[t]


    result_terms = []
    for t in distance:
        if distance[t] == mini_dsitance:
            result_terms.append(t)
    return result_terms
def MultiKeywordSearch(keyword):
    word_list = preproccess(keyword)
    docs = []
    l = list(Document.objects.filter(title__icontains=keyword))
    for d in l:
        docs.append(d)
    docs_returned= get_documents(keyword)
    if len(word_list)==1:
        return docs + docs_returned
    print(docs_returned)
    rank = Rank(keyword,docs_returned)
    print(rank)
    for r in rank:
        doc = Document.objects.get(pk=r)
        if doc not in docs:
            docs.append(doc)
    return docs
#get all documents (exact search or multikeyword)
def get_documents(keyword,exact= False):
    word_list = preproccess(keyword)
    all_inverted_list=[]
    big_list=[]
    for word in word_list:
        inverted_list=Inverted_Index_Element.objects.filter(term=word)
        all_inverted_list.append(list(inverted_list))
        docs_id_list=[]
        for i in inverted_list:
            docs_id_list.append(i.doc_id)
        big_list.append(docs_id_list)
    intersect=big_list[0]
    docs = []
    for i in range(len(big_list)):
        intersect = list(set(big_list[i]) & set(intersect))
    if len (word_list) ==1:
        rank = dict()
        for inv in inverted_list:
            rank[inv.doc_id] =inv.freq
        b = [(k, rank[k]) for k in sorted(rank, key=rank.get, reverse=True)]
        print(b)
        for i in b:
            doc = Document.objects.get(pk=i[0])
            docs.append(doc)
        print(docs)
        return docs


    docs=list(Document.objects.filter(id__in=intersect))


    if not exact :
        return docs
    if intersect==[]:
        return []
    rank = dict()
    inverted_list = []
    for word in word_list:
        inverted = list(Inverted_Index_Element.objects.filter(term=word, doc_id__in=intersect))
        print("len : ",word , len(inverted))
        inverted_list.append(inverted)

    for j in range (len(inverted_list[0])):
        positions= []
        for i in range(len(inverted_list)):
            pos =list(map(int ,inverted_list[i][j].positions.strip("[").strip("]").split(",")))
            positions.append(pos)
            id = inverted_list[i][j].doc_id
        r= calculateRanking_exact(positions)

        if r >0:
            rank[id] =r
            print(id , " rank : ",r )

    docs = []
    b = [(k, rank[k]) for k in sorted(rank, key=rank.get, reverse=True)]
    print(b)

    for i in b:
        doc= Document.objects.get(pk=i[0])
        docs.append(doc)
    print(docs)
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
#preprocessing
def preproccess(text):
    punc = string.punctuation + "^"
    text = text.lower()
    for p in punc:
        text = text.replace(p, "")
    word_list = word_tokenize(text)
    stemmer = PorterStemmer()
    return_list=[]

    for word in word_list:
        if word not in stopwords.words('english'):
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
def RankingAlgorithm(searchquery, documents):
    searchquery_split=searchquery.split()

    dic =dict()
    query_term_dict=dict()
    l=list()
    for query_term in searchquery_split:
        for doc_number in documents.keys():
            doc=documents[doc_number].split()
            for i in range(len(doc)):
                if query_term==doc[i]:
                    dic={doc_number:i}
                    l.append(dic)
        query_term_dict[query_term]=l
        l=[]
    dic2=query_term_dict
    #print query_term_dict

    l=[]

    dic2=calculateDistance(query_term_dict, searchquery_split,documents)

    l=[]
    l_tmp1=[]
    l_tmp2=[]
    final_rank=[]
    for d in dic2.keys():
        l.append(dic2[d])

    l_tmp1.sort()

    l.sort()
    for i in range(len(l)):
       for d in dic2.keys():
          if l[i]==dic2[d]:
             final_rank.append(d)
             del dic2[d]
             break

    return final_rank
def calculateDistance(dic, searchquery,documetns):
   distance_dict=dict()
   distance_list=[]
   q_term1_list=dic[searchquery[0]]
   q_term2_list=dic[searchquery[1]]
   q_term1_listx=[]
   q_term2_listx=[]
   for i in range(len(q_term1_list)):
       dic_tmp=q_term1_list[i]
       for key in dic_tmp.keys():
         q_term1_listx.append([key,dic_tmp[key]])
   for i in range(len(q_term2_list)):
       dic_tmp = q_term2_list[i]
       for key in dic_tmp.keys():
           q_term2_listx.append([key, dic_tmp[key]])
   i=0
   j=0
   tmp_index=0
   min_dic = dict()
   for k in documetns.keys():
       min_dic[k] = 1000

   while True:
         l1=q_term1_listx[i]
         l2=q_term2_listx[j]
         if l1[0]==l2[0]:
           if [l1[0],abs(l1[1]-l2[1])] not in distance_list and l1[1]-l2[1]<0:
               diff = abs(l1[1] - l2[1])
               if diff < min_dic[l1[0]]:
                   min_dic[l1[0]] = diff
                   distance_dict[l1[0]]=diff
         j+=1
         if j==len(q_term2_listx):
             i+=1
             j=0
         if  i==len(q_term1_listx):
             break

   return distance_dict
def MainRanking(searchquery,documents):
    searchquery_split=searchquery.split()
    List_of_terms=[]
    for i in range(len(searchquery_split)-1):
        combination=searchquery_split[i]+" "+searchquery_split[i+1]
        List_of_terms.append(combination)
    l=[]
    #print List_of_terms,"*"
    for term in List_of_terms:
        l.append(RankingAlgorithm(term,documents))
    rank_dict=dict()
    for d in documents.keys():
        rank_dict[d]=0
    final_rank=[]
    max=0
    save_index=0
    k=0
    print(l)
    while True:
       for i in range(len(l)):
            if k==len(l[i]):
                for d in documents.keys():
                    if d not in final_rank:
                        final_rank.append(d)
                return final_rank
            rank_dict[l[i][k]]+=1
            if(rank_dict[l[i][k]]>max):
                max=rank_dict[l[i][k]]
                save_index=l[i][k]
       if save_index not in final_rank:
          final_rank.append(save_index)
       for d in documents.keys():
           rank_dict[d] = 0
       max=0
       save_index=0
       k+=1
def Rank(query,documents):
    if documents==[]:
        return []
    documents_dict=dict()
    for doc in documents:
        documents_dict[doc.id]=doc.text.lower()
    return MainRanking(query.lower(), documents_dict)
def calculateRanking_exact(BigPositionsList):
    count = len(BigPositionsList)
    if count == 1:
        return len(BigPositionsList[0])
    rank = 0
    for i in BigPositionsList[0]:
        expected = i+1
        countR = 1
        flag = False
        while countR < count:
            if expected in BigPositionsList[countR]:
                expected += 1
                countR += 1
                flag = True
            else:
                flag = False
                break
        if flag == True:
            rank += 1
    return rank
