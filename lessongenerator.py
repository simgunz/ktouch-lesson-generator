#!/usr/bin/python
"""
KTouch lesson generator.

Usage:
  ktouch_lesson_generator [options] <letterslist> [<dictionary>]

  Generate a set of ktouch lessons, one for each line in <letterslist> file.
  If dictionary is not specified generates random combinations of letters instead of meaningful words.

Options:
  -n --lesson-number=<n>                   Line number of the lesson to be generated. If not specified all lessons are generated.
  -w --word-wrap=<n>                       Wrap lesson text at this length. [default: 60]
     --letters-per-lesson=<n>              Number of letters in a lesson. [default: 2000]
     --min-word-length=<n>                 Minimum length a word must have to be included in the lesson. [default: 4]
     --symbols-density=<f>                 Amount of symbols that should be put in the lesson. [default: 0.05]
     --numbers-density=<f>                 Amount of numbers that should be put in the lesson. [default: 0.3]
     --inlcude-previous-symbols            Set to 0 to include only symbols from the current lesson. [default: False]
     --include-previous-numbers            Set to 0 to include only numbers from the current lesson. [default: False]
     --max-number-length=<n>               Maximum length of the generated numbers. [default: 3]
     --max-letters-combination-length=<n>  Maximum length of the generated combinations of letter (for first 2-3 lessons). [default: 4]
  -h --help                                Show this screen.
  -v --version                             Show version.

Format of <letterslist> file:
  <letterslist> is a file containing the new letters of each lesson. Every line is a new lesson.
  A position for the symbols can be specified as:
  LL: Next to the left word boundary
  RR: Next to the right word boundary
  LR: Next to the left or right word boundary
    : Detached from the word

  Example letters.txt:
    jf
    èy
    ABCDEFGHIJKLMNOPQRSTUVWXYZ
    LR"$
    LL(RR)
"""

import sys, re
import textwrap
from docopt import docopt
from random import shuffle, sample, random
from schema import Schema, Use, Or
import itertools

RE_POSITION_MARKERS = re.compile('(LL|RR|LR)')

def stripPositionMarkers(txt):
    return re.sub(RE_POSITION_MARKERS, '', txt)

def genCombPerm(elements, maxLength):
    '''Return an array of strings containing different permutations of combinations of the elements
    of different lengths up to the specified maximum length
    E.g. 'ab' -> ['a' 'b' 'aa' 'ab' 'ba' 'bb']
    '''
    return list({''.join(p) for i in range(maxLength)
                            for c in itertools.combinations_with_replacement(''.join(elements), i+1)
                            for p in itertools.permutations(c)})


def createLesson(currentTxt, words, word_wrap=60, letters_per_lesson=2000, min_word_length=4,
    symbols_density=0.05, numbers_density=0.3, include_previous_symbols=True, include_previous_numbers=True,
    max_number_length=3, max_letters_combination_length=4, **ignored):
    '''Create a KTouch lesson for the letters passed as input
    '''
    print('Processings letters:' + stripPositionMarkers(currentTxt))

    lettersIdx = letters.index(currentTxt)
    previousTxt = ''.join(letters[0:lettersIdx])
    previousLetters = stripPositionMarkers(''.join(re.findall('[^\W\d_]', previousTxt)))
    currentLetters = stripPositionMarkers(''.join(re.findall('[^\W\d_]', currentTxt)))

    #Find if in the currentLetters there is at least a real letter (a non-symbol)
    #and set the regular expression for picking the correct words from the dictionary.
    if currentLetters:
        expression = '[{0}{1}]*[{0}]+[{0}{1}]*$'.format(currentLetters, previousLetters)
    else:
        expression = '[{0}]+$'.format(previousLetters)

    lCount = 0  #Letter counter
    goodWords = []
    for w in words:
        if any(x.isupper() for x in currentLetters):
            #If any of the new letters is a capital one we capitalize the first letter of all the words
            w = w.title()
        if any(x.isupper() for x in previousLetters) and round(random()):
            #If any of the new letters is a capital one we capitalize the first letter of all the words
            w = w.title()
        #Select a word with at least MINWORDLENGTH letters that contains at least one of the
        #letters of the current lesson, and is made only by letters present in the past
        #lessons (beside the current one).
        #For symbols/numbers the words isn't required to contain them, because they are added after
        #so we only check against previousLetters.
        #The process stops when we select enough words to fill the lesson as specified by LETTERSPERLESSON
        #or when we exhausted the dictionary.
        if re.match(expression, w):
            if len(w) > min_word_length:
                lCount += len(w)
                goodWords.append(w)
                if lCount > letters_per_lesson:
                    break

    #For the first 2-3 lesson the previous block fails, so we need to generate the lesson as
    #combinations/permutations of letters
    if not goodWords:
        dicto = genCombPerm(currentLetters + previousLetters, max_letters_combination_length)
        while lCount < letters_per_lesson:
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
    if include_previous_symbols:
        lettersList = currentTxt + previousTxt
    else:
        lettersList = currentTxt
    symbols = re.findall('[\W_]', lettersList)
    if symbols:
        lSymbols = re.findall('LL([\W_])', lettersList)
        rSymbols = re.findall('RR([\W_])', lettersList)
        lrSymbols = re.findall('LR([\W_])', lettersList)
        aloneSymbols = set(symbols) - set( lSymbols + rSymbols + lrSymbols)

        symbolDensity = symbols_density/len(symbols) # Per symbols
        nSym = round(letters_per_lesson*symbolDensity)
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
    if include_previous_numbers:
        numbers = currentNumbers + previousNumbers
    else:
        numbers = currentNumbers
    if numbers:
        nNum = round(letters_per_lesson*numbers_density)
        numDictionary = genCombPerm(numbers, max_number_length)
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
        while len(''.join(goodWords)) < letters_per_lesson:
            #Scramble the cloned words to make it less repetitive
            shuffle(clonedWords)
            goodWords += clonedWords

    #Now convert the array to text and cut the lesson to the right size
    goodWordsText = ' '.join(goodWords)
    goodWordsText = re.sub('\S*$', '', goodWordsText[0:letters_per_lesson])

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
    wrappedLesson = '\n'.join(textwrap.wrap(goodWordsText, word_wrap))

    return wrappedLesson


def formatLesson(currentLetters, lessonText):
    out =  'New letters: {0}\n'.format(stripPositionMarkers(currentLetters))
    out += '------------------------------------------------------------\n'
    out += lessonText
    out += '\n\n'
    return out

if __name__ == '__main__':
    args = docopt(__doc__, version='1.0')
    args = Schema({
        '<letterslist>':  Use(str),#FIXME: Use file validator
        '<dictionary>': Or(None, Use(str)),#FIXME: Use file validator
        '--lesson-number': Or(None, Use(int)),
        '--word-wrap': Or(None, Use(int)),
        '--letters-per-lesson': Or(None, Use(int)),
        '--min-word-length': Or(None, Use(int)),
        '--symbols-density': Or(None, Use(float)),
        '--numbers-density': Or(None, Use(float)),
        '--max-number-length': Or(None, Use(int)),
        '--max-letters-combination-length': Or(None, Use(int)),
        str: bool, #don’t care
    }).validate(args)

    argoptions = dict()
    for k in args.keys():
        if '--' in k:
            argoptions[k.strip('--').replace('-', '_')] = args[k]
    #File containings the letters which should be learned every lesson (one lesson per line)

    #Dictionary file
    words = []
    if args['<dictionary>']:
        with open(args['<dictionary>']) as f:
            #Consider only first column, strip newlines, strip hypnetion information from some dictionaries, set to lower case
            words = [re.sub('/.*$', '', line.split(' ')[0].rstrip('\n').lower()) for line in f]
            #Shuffle words to avoid having all the variations of the same word in the
            shuffle(words)

    with open(args['<letterslist>']) as f:
        letters = [line.rstrip('\n') for line in f]

    #If we pass a line number (starting from zero) we create only the lesson for the specified letters
    #otherwise we create all the lessons
    #OUTPUT:
    #[letters].txt
    #or
    #ktouch-lessons.txt
    if args['--lesson-number']:
        lettersIdx = int(args['--lesson-number']) - 1
        letters = [letters[lettersIdx]]
        outFileName = stripPositionMarkers(letters[0]) + '.txt'
    else:
        outFileName = 'ktouch-lessons.txt'

    with open(outFileName, 'w') as f:
        #First lesson is for sure empty, so it won't be processed, but still we write it to file as placeholder
        for currentLetters in letters:
            wd = createLesson(currentLetters, words, **argoptions)
            #Write the lesson to file
            f.write(formatLesson(currentLetters, wd))
