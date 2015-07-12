#!/usr/bin/python

#dictionary.txt - A file containing a long list of words (one per line).
#letters.txt    - A file containing the new letters of each lesson. Every line is a new lesson.
#                 A position for the symbols can be specified as:
#                   LL: Next to the left word boundary
#                   RR: Next to the right word boundary
#                   LR: Next to the left or right word boundary
#                     : Detached from the word
#
#                 Example letters.txt:
#                 jf
#                 èy
#                 ABCDEFGHIJKLMNOPQRSTUVWXYZ
#                 LR"$
#                 LL(RR)

#Example python generateLesson dictionary.txt lettersList.txt 5   #Generate lesson on line 5
#Example python generateLesson dictionary.txt lettersList.txt     #Generate everything

import sys, re
import textwrap
from random import shuffle, sample
import itertools

RANDOMIZE = 1               #Shuffle card in source dictionary
WORDWRAP = 60               #Wrap lesson text at this length
LETTERSPERLESSON = 2000     #Number of letters in a lesson
MINWORDLENGTH = 4           #Minimum length a word must have to be included in the lesson
SYMBOLSDENSITY = 0.05       #Amount of symbols that should be put in the lesson
NUMBERDENSITY  = 0.3        #Amount of numbers that should be put in the lesson
INCLUDEPREVIOUSSYMBOLS = 1  #Set to 0 to include only symbols from the current lesson
INCLUDEPREVIOUSNUMBERS = 1  #Set to 0 to include only numbers from the current lesson
MAXNUMBERLENGTH = 3         #Maximum length of the generated numbers
MAXLETTERCOMBLENGTH = 4     #Maximum length of the generated combinations of letter (for first 2-3 lessons)

def stripPositionMarkers(txt):
    return txt.replace('LL','').replace('RR','').replace('LR','')

def genCombPerm(elements, maxLength):
    '''Return an array of strings containing different permutations of combinations of the elements
    of different lengths up to the specified maximum length
    E.g. 'ab',2 -> ['a' 'b' 'aa' 'ab' 'ba' 'bb']
    '''
    cperm=[]
    perm = []
    for i in range(maxLength):
        comb = list(itertools.combinations_with_replacement(''.join(elements), i+1))
        for c in comb:
            perm += list(itertools.permutations(c))
    for n in set(perm):
        cperm.append(''.join(n))
    return cperm


def createLesson(currentTxt):
    '''Create a KTouch lesson for the letters passed as input
    '''
    print('Processings letters:' + stripPositionMarkers(currentTxt))

    lettersIdx = letters.index(currentTxt)
    previousTxt = ''.join(letters[0:lettersIdx])
    previousLetters = ''.join(re.findall('[^\W\d_]', previousTxt))
    currentLetters = ''.join(re.findall('[^\W\d_]', currentTxt))

    #Find if in the currentLetters there is at least a real letter (a non-symbol)
    #and set the regular expression for picking the correct words from the dictionary.
    if currentLetters:
        expression = '[{0}{1}]*[{0}]+[{0}{1}]*$'.format(currentLetters, previousLetters)
    else:
        expression = '[{0}]+$'.format(previousLetters)

    #If one of the new letters is a capital one we capitalize the first letter of all the words
    if True in list(map(str.isupper, list(currentLetters))):
        capitalize = True
    else:
        capitalize = False

    lCount = 0  #Letter counter
    goodWords = []
    for w in words:
        if capitalize:
            w = w.title()
        #Select a word with at least MINWORDLENGTH letters that contains at least one of the
        #letters of the current lesson, and is made only by letters present in the past
        #lessons (beside the current one).
        #For symbols/numbers the words isn't required to contain them, because they are added after
        #so we only check against previousLetters.
        #The process stops when we select enough words to fill the lesson as specified by LETTERSPERLESSON
        #or when we exhausted the dictionary.
        if re.match(expression, w):
            if len(w) > MINWORDLENGTH:
                lCount += len(w)
                goodWords.append(w)
                if lCount > LETTERSPERLESSON:
                    break

    #For the first 2-3 lesson the previous block fails, so we need to generate the lesson as
    #combinations/permutations of letters
    if not goodWords:
        dicto = genCombPerm(currentLetters + previousLetters, MAXLETTERCOMBLENGTH)
        while lCount < LETTERSPERLESSON:
            #Pick a word randonly from the generated dictionary
            w = dicto[sample(range(len(dicto)), 1)[0]]
            #Check that the random word contains the currentLetters
            if re.search('[{0}]'.format(''.join(currentLetters)), w):
                lCount += len(w)
                goodWords.append(w)

    #Retrieve the symbols and spread them around the text
    #A position for the symbols can be specified as:
    #LL: Next to the left word boundary
    #RR: Next to the right word boundary
    #LR: Next to the left or right word boundary
    #: Detached from the word
    if INCLUDEPREVIOUSSYMBOLS:
        lettersList = currentTxt + previousTxt
    else:
        lettersList = currentTxt
    symbols = re.findall('[\W_]', lettersList)
    if symbols:
        lSymbols = re.findall('LL([\W_])', lettersList)
        rSymbols = re.findall('RR([\W_])', lettersList)
        lrSymbols = re.findall('LR([\W_])', lettersList)
        aloneSymbols = set(symbols) - set( lSymbols + rSymbols + lrSymbols)

        symbolDensity = SYMBOLSDENSITY/len(symbols) # Per symbols
        nSym = round(LETTERSPERLESSON*symbolDensity)
        for s in aloneSymbols:
            #Append nSym times the symbol to the list of good words
            goodWords += [s] * nSym

        for s in lSymbols:
            #Append nSym times the symbol to the list of good words
            goodWords += ['L' + s] * nSym

        for s in rSymbols:
            #Append nSym times the symbol to the list of good words
            goodWords += ['R' + s] * nSym

        for s in lrSymbols:
            #Append nSym times the symbol to the list of good words
            goodWords += ['L' + s] * round(nSym/2) + ['R' + s] * round(nSym/2)

        shuffle(goodWords)

        #Avoid multiple symbols between words
        newGoodWords = []
        firstSymbol = 1
        for w in goodWords:
            if re.match('\w+$', w):
                newGoodWords.append(w)
                firstSymbol = 1
            elif firstSymbol == 1:
                newGoodWords.append(w)
                firstSymbol = 0
        goodWords = newGoodWords


    #Add the numbers
    previousNumbers = re.findall('\d', previousTxt)
    currentNumbers = re.findall('\d', currentTxt)
    if INCLUDEPREVIOUSNUMBERS:
        numbers = currentNumbers + previousNumbers
    else:
        numbers = currentNumbers
    if numbers:
        nNum = round(LETTERSPERLESSON*NUMBERDENSITY)
        numDictionary = genCombPerm(numbers, MAXNUMBERLENGTH)
        for i in range(nNum):
            #Sample some numbers
            n = numDictionary[sample(range(len(numDictionary)), 1)[0]]
            #If current numbers is empty any picked number is ok to include
            #otherwise check that the selected number contains currentNumbers
            if not currentNumbers or re.search('[{0}]'.format(''.join(currentNumbers)), n):
                goodWords.append(n)
        shuffle(goodWords)


    #If the array is non empty, check that the lesson is long enough otherwise extend it by duplicating the words
    if goodWords:
        clonedWords = list(goodWords)
        while len(''.join(goodWords)) < LETTERSPERLESSON:
            #Scramble the cloned words to make it less repetitive
            shuffle(clonedWords)
            goodWords += clonedWords

    #Now convert the array to text and cut the lesson to the right size
    goodWordsText = ' '.join(goodWords)
    goodWordsText = re.sub('\S*$', '', goodWordsText[0:LETTERSPERLESSON])

    #Position the symbols to the right place
    if symbols:
        #Escape \ as '\\1' or use raw string as r'\1'
        #Remove the postion markers L and R and the corresponding space to position the symbol
        goodWordsText = re.sub('L(\W) ', '\\1', goodWordsText)
        goodWordsText = re.sub(' R(\W)', '\\1', goodWordsText)
        #Avoid symbols to be next to each other
        goodWordsText = re.sub(' (\W)\W*', ' \\1', goodWordsText)
        goodWordsText = re.sub('(\W)\W* ', '\\1 ', goodWordsText)

    #Wrap the text to WORDWRAP characters (KTouch required wrapping at 60)
    wrappedLesson = '\n'.join(textwrap.wrap(goodWordsText, WORDWRAP))

    return wrappedLesson


def formatLesson(currentLetters, lessonText):
    out =  'New letters: {0}\n'.format(stripPositionMarkers(currentLetters))
    out += '------------------------------------------------------------\n'
    out += lessonText
    out += '\n\n'
    return out


#Dictionary file
wordsFile = sys.argv[1]
#File containings the letters which should be learned every lesson (one lesson per line)
lettersFile = sys.argv[2]

with open(wordsFile) as f:
    #Consider only first column, strip newlines, strip hypnetion information from some dictionaries, set to lower case
    words = [re.sub('/.*$', '', line.split(' ')[0].rstrip('\n').lower()) for line in f]
    #Randomize words to avoid having all the variations of the same word in the lesson
    if RANDOMIZE:
        shuffle(words)

with open(lettersFile) as f:
    letters = [line.rstrip('\n') for line in f]

#If we pass a line number (starting from zero) we create only the lesson for the specified letters
#otherwise we create all the lessons
#OUTPUT:
#[letters].txt
#or
#ktouch-lessons.txt

if len(sys.argv) > 3:
    lettersIdx = int(sys.argv[3]) - 1
    currentLetters = letters[lettersIdx]
    with open(stripPositionMarkers(currentLetters) + '.txt', 'w') as f:
        wd = createLesson(currentLetters)
        #Write the lesson to file
        f.write(formatLesson(currentLetters, wd))
else:
    with open('ktouch-lessons.txt', 'w') as f:
        #First lesson is for sure empty, so it won't be processed, but still we write it to file as placeholder
        for currentLetters in letters:
            wd = createLesson(currentLetters)
            #Write the lesson to file
            f.write(formatLesson(currentLetters, wd))
