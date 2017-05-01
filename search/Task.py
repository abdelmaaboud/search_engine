def BiGram(word):
    word = '$' + word
    count = 0
    length = len(word)
    list = []
    while count < length and count != length-1:
        list.append(word[count] + word[count+1])
        count += 1
    return list

def checkBiGram(word1,word2):
    list_word1 = BiGram(word1)
    list_word2 = BiGram(word2)
    intersect = list(set(list_word1) & set(list_word2))
    intersect_len = len(intersect)
    union = list_word1+list_word2
    union_len = len(union)
    JC = intersect_len / (union_len-intersect_len)

    print(union_len)
    print(intersect_len)
    print(JC)

    if JC >= 0.45:
        return True
    else:
        return False


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


def soundex(word):
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





print(BiGram("ah"))
print(checkBiGram("lord","loord"))
print(EditDistance("cat","ooooo"))
print(soundex("hernam"))
print(soundex("hermann"))
print(soundex("a"))






