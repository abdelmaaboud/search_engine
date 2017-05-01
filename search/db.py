import sqlite3
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from nltk.stem.porter import *
import string
conn = sqlite3.connect('db.sqlite3')
#"select * from auth_group;"
#
all_docs= []
all_ids=[]
cur = conn.execute("select * from searchapp_document")
for row in cur:
    all_docs.append(row[3])
    all_ids.append(row[0])
    print(row[0])
    if len(all_docs) > 1600:
        break


def get_terms(text,id):
        punc = string.punctuation + "^"
        terms_dic = dict()
        text = text.lower()
        for p in punc:
            text = text.replace(p, "")
        word_list = word_tokenize(text)
        filtered_words = [word for word in word_list if word not in stopwords.words('english')]
        p = re.compile("^[a-z]+$")
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
        #print(terms_dic)
        for key in terms_dic:
            cur.execute('insert into searchapp_term (term,doc_id,freq) values (?,?,?)',(key,id,terms_dic[key]["freq"]))
            #term = Term( term=key,freq=terms_dic[key]["freq"],doc_id=self.pk)
        conn.commit()

        return terms_dic
def get_index(text,id):
    punc = string.punctuation + "^"
    inverted_dic = dict()
    text = text.lower()
    for p in punc:
        text = text.replace(p, "")
    word_list = word_tokenize(text)
    p=re.compile("^[a-z]+$")
    print(word_list)
    for i in range(len(word_list)):
        try:
            if p.findall( word_list[i]) ==[] :
                continue
            if word_list[i] in stopwords.words('english'):
                continue

            stemmer = PorterStemmer()
            word = stemmer.stem(word_list[i])
            if word in inverted_dic:
                inverted_dic[word]["freq"]+=1
                inverted_dic[word]["positions"].append(i)
            else:
                dic = dict()
                dic["freq"] = 1
                dic["positions"] = [i]
                inverted_dic[word] = dic
        except :
            continue

    for key in inverted_dic:
        cur.execute('insert into searchapp_inverted_index_element (term,doc_id,freq,positions) values (?,?,?,?)', (key, id, inverted_dic[key]["freq"],str(inverted_dic[key]["positions"])))
    print(len(inverted_dic))
    if id%5==0:
        conn.commit()



for i in range(len(all_ids)):
    text = all_docs[i]
    get_index(text,all_ids[i])
    print(all_ids[i])
conn.commit()


for i in range(len(all_ids)):
    text = all_docs[i]
    get_terms(text,all_ids[i])
    print(all_ids[i])
conn.commit()
