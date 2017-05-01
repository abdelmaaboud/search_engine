def get_bigram(word):
    word = '$' + word + '$'
    count = 0
    length = len(word)
    list = []
    while count < length and count != length-1:
        list.append(word[count] + word[count+1])
        count += 1
    return list

import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.execute("select distinct term from searchapp_distencitterm")
word_list = []
for row in cur:
    word_list.append(row[0])
dictionary = dict()
print(len(word_list))
i=0
for word in word_list:
    grams = get_bigram(word)
    for gram in grams:

        if gram in dictionary:
            #if word not in dictionary[soundex]:
            dictionary[gram].append(word)
        else:
            print(gram)
            dictionary[gram]=[word]
for key in dictionary:
    print(key ," : " , dictionary[key])


# data base

for key in dictionary:
    terms = ",".join(dictionary[key])
    conn.execute("insert into searchapp_bigramterm (bigram,terms) values(?,?)",(key,terms))
    print(key)
conn.commit()
