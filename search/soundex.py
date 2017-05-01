import sqlite3
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
conn = sqlite3.connect('db.sqlite3')
cur = conn.execute("select distinct term from searchapp_distencitterm")
word_list = []
for row in cur:
    word_list.append(row[0])
dictionary = dict()
print(len(word_list))
i=0
for word in word_list:
    soundex = get_soundex(word)
    if soundex in dictionary:
        #if word not in dictionary[soundex]:
        dictionary[soundex].append(word)
    else:
        print(soundex)
        dictionary[soundex]=[word]



for key in dictionary:
    terms = ",".join(dictionary[key])
    conn.execute("insert into searchapp_soundexterm (soundex,terms) values(?,?)",(key,terms))
    print(key)
conn.commit()