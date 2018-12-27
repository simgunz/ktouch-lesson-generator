#!/usr/bin/python
"""
Usage:
ktouch-lesson-generator.py [options] <charslist> [<dictionary>]

Generate a set of ktouch lessons, one for each line in <charslist> file.
If <dictionary> is not specified, it generates random combinations of letters instead of meaningful words.

Options:
-n --lesson-number=<n>                    Line number of <charslist> corresponding to the lesson to be generated.
                                          If not specified all lessons are generated.
-o --output=<outputfile>                  Output file name. If the lesson number is specified the file name will be the
                                          [selected characters].xml/txt (e.g fj.xml/txt). [default: ktouch-lessons.xml/txt]
-p --plain-text                           Output the lessons in plain text instead of XML
-w --word-wrap=<n>                        Wrap lesson text at this length. [default: 60]
-l --characters-per-lesson=<n>            Number of characters in a lesson. [default: 2000]
    --min-word-length=<n>                 Minimum length a word must have to be included in the lesson. [default: 4]
    --max-word-length=<n>                 Maximum length a word must have to be included in the lesson. [default: 100]
    --symbols-density=<f>                 Fraction of symbols that should be put in the lesson respect to the number
                                          of words. [default: 1]
    --previous-symbols-fraction=<f>       Fraction of symbols from the previous lessons respect the total number of
                                          symbols. Set to 0 to include only symbols from the current lesson. [default: 0.4]
    --numbers-density=<f>                 Fraction of numbers that should be put in the lesson respect to the number
                                          of words. [default: 1]                                          
    --exclude-previous-numbers            Include only numbers from the current lesson.
    --max-number-length=<n>               Maximum length of the generated numbers. [default: 3]
    --max-letters-combination-length=<n>  Maximum length of the generated combinations of letter (for first 2-3
                                          lessons). [default: 4]
    --no-shuffle-dict                     Do not shuffle the dictionary file. Useful if the dictionary file is a
                                          frequency list and we want to prioritize picking the most common words
                                          on the top of the list. If the dictionary is sorted alphabetically shuffling
                                          the words allows avoiding picking all the variations of the same word. 
-h --help                                 Show this screen.
-v --version                              Show version.

Format of <charslist> file:
<charslist> is a file containing the new letters of each lesson. Every line is a new lesson.
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

import itertools
import re
import textwrap
import uuid

from docopt import docopt
from math import floor, ceil
from random import shuffle, choices, sample, random
from voluptuous import Schema, Coerce, Or, error

RE_POSITION_MARKERS = re.compile(r'(LL|RR|LR)')
RE_SYMBOLS = re.compile(r'[\W_]')
RE_LEFT_SYMBOLS = re.compile(r'LL([\W_])')
RE_RIGHT_SYMBOLS = re.compile(r'RR([\W_])')
RE_LEFTRIGHT_SYMBOLS = re.compile(r'LR([\W_])')
RE_LETTERS = re.compile(r'[^\W\d_]')
RE_DIGITS = re.compile(r'\d')

def stripPositionMarkers(txt):
    return re.sub(RE_POSITION_MARKERS, '', txt)


def linspace(a, b, n):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [diff * i + a  for i in range(n)]


def insertUniformly(words, items):
    """Insert the items between the words in a equidistributed way"""
    symbolDensity = len(items)/len(words)
    idx = linspace(0, len(words)*round(1+symbolDensity), len(items))
    for i, s in enumerate(items):
        words.insert(idx[i], s)
        
        
def generateNPrefixedSymbols(symbols, nSym, prefix=''):
    symb = list()
    for s in symbols:
        symString = '{0}{1}'.format(prefix, s)
        symb += [symString] * nSym
    return symb
        
        
def generateSymbols(characters, nWords, symbolDensity):
    symbols = re.findall(RE_SYMBOLS, characters)
    if not symbols:
        return list()
    lSymbols = re.findall(RE_LEFT_SYMBOLS, characters)
    rSymbols = re.findall(RE_RIGHT_SYMBOLS, characters)
    lrSymbols = re.findall(RE_LEFTRIGHT_SYMBOLS, characters)
    unmarkedSymbols = set(symbols) - set(lSymbols + rSymbols + lrSymbols)

    # Number of symbols to insert (per-symbol)
    nSym = round(nWords*symbolDensity/len(symbols))
   
    symb = list()
    symb += generateNPrefixedSymbols(unmarkedSymbols, nSym)
    symb += generateNPrefixedSymbols(lSymbols, nSym, 'L')
    symb += generateNPrefixedSymbols(rSymbols, nSym, 'R')
    symb += generateNPrefixedSymbols(lrSymbols, floor(nSym/2), 'L')
    symb += generateNPrefixedSymbols(lrSymbols, ceil(nSym/2), 'R')
    return symb
        

def addSymbols(words, characters, symbolDensity, previousCharacters='', previousSymbolsFraction=0):
    nWords = len(words)
    if not previousCharacters:
        previousSymbolsFraction = 0
    symb = generateSymbols(characters, nWords, (1-previousSymbolsFraction)*symbolDensity)
    symb += generateSymbols(previousCharacters, nWords, previousSymbolsFraction*symbolDensity)        
    shuffle(symb)
    words = insertUniformly(words, symb)


def generateCharsCombinations(elements, maxLength):
    """Return an array of strings containing different permutations of combinations of the elements
    of different lengths up to the specified maximum length
    E.g. 'ab' -> ['a' 'b' 'aa' 'ab' 'ba' 'bb']
    """
    return list({''.join(p) for i in range(maxLength)
                for c in itertools.combinations_with_replacement(''.join(elements), i+1)
                for p in itertools.permutations(c)})


def addNumbers(words, characters, numberDensity, previousCharacters, 
               excludePreviousNumbers=True, max_number_length=3):
    # Add the numbers
    previousNumbers = re.findall(RE_DIGITS, previousCharacters)
    currentNumbers = re.findall(RE_DIGITS, characters)
    if excludePreviousNumbers:
        numbers = currentNumbers
    else:
        numbers = currentNumbers + previousNumbers
    if not numbers:
        return
    
    nNum = round(len(words)*numberDensity)
    numDictionary = generateCharsCombinations(numbers, max_number_length)
    if currentNumbers:
        RE_CURRENT_NUMBERS = '[{0}]'.format(''.join(currentNumbers))
        numDictionary = [x for x in numDictionary if re.search(RE_CURRENT_NUMBERS, x)]
    selectedNumbers = choices(numDictionary, k=nNum)
    insertUniformly(words, selectedNumbers)
        
        
def createLesson(lessonIdx, lessonsChars, words, word_wrap=60, characters_per_lesson=2000, min_word_length=4, max_word_length=100,
                 symbols_density=0.05, numbers_density=0.3, previous_symbols_fraction=0.4,
                 exclude_previous_numbers=False, max_number_length=3, max_letters_combination_length=4, **ignored):
    """Create a KTouch lesson for the characters passed as input."""
    currentChars = lessonsChars[lessonIdx]
    previousChars = ''.join(lessonsChars[0:lessonIdx])
    previousLetters = stripPositionMarkers(''.join(re.findall(RE_LETTERS, previousChars)))
    currentLetters = stripPositionMarkers(''.join(re.findall(RE_LETTERS, currentChars)))

    print('Processing: ' + stripPositionMarkers(currentChars))

    # Find if in the currentLetters there is at least a real letter (a non-symbol)
    # and set the regular expression for picking the correct words from the dictionary.
    if currentLetters:
        expression = '[{0}{1}]*[{0}]+[{0}{1}]*$'.format(currentLetters, previousLetters)
    else:
        expression = '[{0}]+$'.format(previousLetters)

    lCount = 0
    goodWords = []
    for w in words:
        if any(x.isupper() for x in currentLetters):
            # If any of the new letters is a capital one we capitalize the first letter of all the words
            w = w.title()
        if any(x.isupper() for x in previousLetters) and round(random()):
            # If any of the new letters is a capital one we capitalize the first letter of all the words
            w = w.title()
        # Select a word with at least MINWORDLENGTH letters that contains at least one of the
        # letters of the current lesson, and is made only by letters present in the past
        # lessons (beside the current one).
        # For symbols/numbers the words isn't required to contain them, because they are added after
        # so we only check against previousLetters.
        # The process stops when we select enough words to fill the lesson as specified by LETTERSPERLESSON
        # or when we exhausted the dictionary.
        if re.match(expression, w):
            if len(w) > min_word_length and len(w) < max_word_length:
                lCount += len(w)
                goodWords.append(w)
                if lCount > characters_per_lesson:
                    break

    # For the first 2-3 lesson the previous block fails, so we need to generate the lesson as
    # combinations/permutations of letters
    if currentLetters and not goodWords:
        RE_CURRENT_LETTERS = re.compile('[{0}]'.format(''.join(currentLetters)))

        letterCombDict = generateCharsCombinations(currentLetters + previousLetters, max_letters_combination_length)
        letterCombDict = [w for w in letterCombDict if re.search(RE_CURRENT_LETTERS, w)]
        while lCount < characters_per_lesson:
            # Pick a word randonly from the generated dictionary
            w = letterCombDict[sample(range(len(letterCombDict)), 1)[0]]
            if any(x.isupper() for x in currentLetters):
                # If any of the new letters is a capital one we capitalize the first letter of all the words
                w = w.title()
            if any(x.isupper() for x in previousLetters) and round(random()):
                # If any of the new letters is a capital one we capitalize the first letter of all the words
                w = w.title()
            lCount += len(w)
            goodWords.append(w)

    addSymbols(goodWords, currentChars, symbols_density, previousChars, previous_symbols_fraction)
    
    addNumbers(goodWords, currentChars, numbers_density, previousChars, exclude_previous_numbers, max_number_length)

    # If the array is non empty, check that the lesson is long enough otherwise extend it by duplicating the words
    if goodWords:
        clonedWords = list(goodWords)
        while len(''.join(goodWords)) < characters_per_lesson:
            # Scramble the cloned words to make it less repetitive
            shuffle(clonedWords)
            goodWords += clonedWords

    # Now convert the array to text
    goodWordsText = ' '.join(goodWords)

    # Position the symbols to the right place
    # Remove loose symbols at the begin or end of the text
    goodWordsText = re.sub(r'^[LR][\W_]\s*', '', goodWordsText)
    goodWordsText = re.sub(r'[LR][\W_]\s*$', '', goodWordsText)
    # Remove the postion markers L and R and the corresponding space to position the symbol
    goodWordsText = re.sub(r'L(\W) ', r'\1', goodWordsText)
    goodWordsText = re.sub(r' R(\W)', r'\1', goodWordsText)

    # Cut the lesson to the right size
    goodWordsText = goodWordsText[:characters_per_lesson]
    goodWordsText = re.sub(r'\S*$', '', goodWordsText)
    
    # Wrap the text to WORDWRAP characters (KTouch required wrapping at 60)
    wrappedLesson = '\n'.join(textwrap.wrap(goodWordsText, word_wrap))

    return wrappedLesson


def formatLessonPlainText(currentChars, lessonText):
    lesson = 'New characters: {0}\n'.format(stripPositionMarkers(currentChars))
    lesson += '------------------------------------------------------------\n'
    lesson += lessonText
    lesson += '\n\n'
    return lesson


def lessonXMLHeader():
    uniqueid = str(uuid.uuid4())
    return textwrap.dedent("""\
        <?xml version="1.0"?>
        <course>
            <id>{{{id}}}</id>
            <title>KTouch-Generator-{shortid}</title>
            <description></description>
            <keyboardLayout></keyboardLayout>
            <lessons>\
    """).format(id=uniqueid, shortid=uniqueid[:8])


def lessonXMLFooter():
    return textwrap.dedent("""
        </lessons>
        </course>
    """)


def replaceInvalidXMLCharacters(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    return text


def formatLessonXML(currentChars, lessonText):
    lessonText = replaceInvalidXMLCharacters(lessonText)
    currentChars = replaceInvalidXMLCharacters(currentChars)
    currentChars = stripPositionMarkers(currentChars)
    lesson = """
    <lesson>
        <id>{{{id}}}</id>
        <title>{newChars}</title>
        <newCharacters>{newChars}</newCharacters>
        <text>{lessonText}</text>
    </lesson>\
    """.format(id=uuid.uuid4(), newChars=currentChars, lessonText=lessonText)
    return lesson


if __name__ == '__main__':
    # Parse docopt using schema to cast to correct type
    args = docopt(__doc__, version='1.0')
    schema = Schema({
        '<charslist>':  str,  # FIXME: Use IsFile to check if file exists
        '<dictionary>': Or(None, str),
        '--lesson-number': Or(None, Coerce(int)),
        '--output': Or(None, str),
        '--word-wrap': Or(None, Coerce(int)),
        '--characters-per-lesson': Or(None, Coerce(int)),
        '--min-word-length': Or(None, Coerce(int)),
        '--max-word-length': Or(None, Coerce(int)),
        '--symbols-density': Or(None, Coerce(float)),
        '--previous-symbols-fraction': Or(None, Coerce(float)),
        '--numbers-density': Or(None, Coerce(float)),
        '--max-number-length': Or(None, Coerce(int)),
        '--max-letters-combination-length': Or(None, Coerce(int)),
        str: bool  # Treat all other arguments as bool
    })
    args = schema(args)

    try:
        args = schema(args)
    except error.MultipleInvalid as ex:
        print("\n".join([e.msg for e in ex.errors]))
    # Create an argument list from docopt to pass it easily to createLesson
    argoptions = {k.strip('--').replace('-', '_'): args[k] for k in args.keys() if '--' in k}

    # Acquire the dictionary file
    words = []
    if args['<dictionary>']:
        with open(args['<dictionary>']) as f:
            # Consider only first column, strip newlines, strip hypnetion information from some dictionaries
            words = [re.sub('/.*$', '', line.split(' ')[0].rstrip('\n').lower()) for line in f]
        if not args['--no-shuffle-dict']:
            # Shuffle words to avoid picking all the variations of the same word
            shuffle(words)

    # Acquire the list of characters corresponding to lessons
    with open(args['<charslist>']) as f:
        lessonsChars = [line.rstrip('\n') for line in f if line]

    # If we pass a line number (starting from one) create only the corresponding lesson 
    # otherwise create all the lessons
    if args['--lesson-number']:
        lessonIdx = args['--lesson-number'] - 1
        selectedChars = lessonsChars[lessonIdx]
        outFileName = stripPositionMarkers(selectedChars) + '.txt'
        selectedChars = [selectedChars]  # Make list to process with for
    else:
        selectedChars = lessonsChars
        outFileName = args['--output'].rsplit(".", 1)[0]
        if args['--plain-text']:
            outFileName += '.txt'
        else:
            outFileName += '.xml'

    formattedLesson = ''
    with open(outFileName, 'w') as f:
        # First lesson is for sure empty, so it won't be processed, but still we write it to file as placeholder
        for lessonIdx, currentChars in enumerate(selectedChars):
            wd = createLesson(lessonIdx, selectedChars, words, **argoptions)
            # Write the lesson to file
            if args['--plain-text']:
                formattedLesson += formatLessonPlainText(currentChars, wd)
            else:
                formattedLesson += formatLessonXML(currentChars, wd)
        if args['--plain-text']:
            f.write(formattedLesson)
        else:
            f.write(lessonXMLHeader())
            f.write(formattedLesson)
            f.write(lessonXMLFooter())
