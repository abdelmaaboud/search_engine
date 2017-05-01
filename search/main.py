import string


from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from nltk.stem.porter import *
def get_index(text):
    punc = string.punctuation + "^"
    inverted_dic = dict()
    text = text.lower()
    for p in punc:
        text = text.replace(p, "")
    word_list = word_tokenize(text)
    p=re.compile("^(?=.*[a-z]).+$")


    print(word_list)
    for i in range(len(word_list)):

        if p.findall( word_list[i]) ==[] :
            continue
        if word_list[i] in stopwords.words('english'):
            continue

        stemmer = PorterStemmer()
        word = stemmer.stem(word_list[i])



        if word_list[i] in inverted_dic:
            inverted_dic[word]["freq"]+=1
            inverted_dic[word]["positions"].append(i)

        else:
            dic = dict()
            dic["freq"] = 1
            dic["positions"] = [i]
            inverted_dic[word] = dic



    for key in inverted_dic:
        print(key,"  "," freq : ",inverted_dic[key]["freq"]," , positions : ",inverted_dic[key]["positions"])
        print()
    print(len(inverted_dic))



file = open("a.txt")
get_index(file.read())
