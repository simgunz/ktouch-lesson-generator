#!/usr/bin/python
"""
Usage:
ktouch-lesson-generator.py [options] <charslist> [<dictionary>]

Generate a set of ktouch lessons, one for each line in <charslist> file.
If <dictionary> is not specified, it generates random combinations of letters instead of meaningful words.

Options:
-n --lesson-number=<n>                    Line number of <charslist> corresponding ro the lesson to be generated.
                                          If not specified all lessons are generated.
-o --output=<outputfile>                  Output file [default: ktouch-lessons.xml/txt]. If the lesson number is specified
                                          the file name will be the [selected characters].txt (e.g fj.xml/txt)
-p --plain-text                           Output the lessons in plain text instead of XML
-w --word-wrap=<n>                        Wrap lesson text at this length. [default: 60]
-l --characters-per-lesson=<n>            Number of characters in a lesson. [default: 2000]
    --min-word-length=<n>                 Minimum length a word must have to be included in the lesson. [default: 4]
    --max-word-length=<n>                 Maximum length a word must have to be included in the lesson. [default: 100]
    --symbols-density=<f>                 Fraction of symbols that should be put in the lesson respect the number
                                          of words. [default: 1]
    --numbers-density=<f>                 Fraction of numbers that should be put in the lesson respect the number
                                          of words. [default: 1]
    --previous-symbols-fraction=<f>       Fraction of symbols from the previous lessons respect the total number of
                                          symbols. Set to 0 to include only symbols from the current lesson. [default: 0.4]
    --previous-numbers-fraction=<f>       Fraction of numbers from the previous lessons respect the total number of
                                          numbers. Set to 0 to include only numbers from the current lesson. [default: 0.4]
    --include-previous-numbers            Set to 0 to include only numbers from the current lesson. [default: False]
    --max-number-length=<n>               Maximum length of the generated numbers. [default: 3]
    --max-letters-combination-length=<n>  Maximum length of the generated combinations of letter (for first 2-3
                                          lessons). [default: 4]
    --no-shuffle-dict                     Do not shuffle the dictionary file. Useful if the dictionary file is a
                                          frequency list and we want to prioritize picking the most common words
                                          on the top of the list. If the dictionary is sorted alphabetically shuffling
                                          the words allows avoiding picking all the variations of the same word. 
                                          [default: False]
-h --help                                 Show this screen.
-v --version                              Show version.

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

import itertools
import re
import textwrap
import uuid

from docopt import docopt
from math import floor, ceil
from random import shuffle, sample, random
from voluptuous import Schema, Coerce, Or, error

RE_POSITION_MARKERS = re.compile('(LL|RR|LR)')


def stripPositionMarkers(txt):
    return re.sub(RE_POSITION_MARKERS, '', txt)


def generateCharsCombinations(elements, maxLength):
    """Return an array of strings containing different permutations of combinations of the elements
    of different lengths up to the specified maximum length
    E.g. 'ab' -> ['a' 'b' 'aa' 'ab' 'ba' 'bb']
    """
    return list({''.join(p) for i in range(maxLength)
                for c in itertools.combinations_with_replacement(''.join(elements), i+1)
                for p in itertools.permutations(c)})


def linspace(a, b, n):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [diff * i + a  for i in range(n)]


def generateNsym(symbols, nSym, prefix=''):
    symb = list()
    for s in symbols:
        symString = '{0}{1}'.format(prefix, s)
        symb += [symString] * nSym
    return symb
        
        
def generateSymbols(characters, nWords, symbolDensity):
    symbols = re.findall(r'[\W_]', characters)
    if not symbols:
        return list()
    lSymbols = re.findall(r'LL([\W_])', characters)
    rSymbols = re.findall(r'RR([\W_])', characters)
    lrSymbols = re.findall(r'LR([\W_])', characters)
    aloneSymbols = set(symbols) - set(lSymbols + rSymbols + lrSymbols)

    # Number of symbols to insert (per-symbol)
    nSym = round(nWords*symbolDensity/len(symbols))
   
    symb = list()
    symb += generateNsym(aloneSymbols, nSym)
    symb += generateNsym(lSymbols, nSym, 'L')
    symb += generateNsym(rSymbols, nSym, 'R')
    symb += generateNsym(lrSymbols, floor(nSym/2), 'L')
    symb += generateNsym(lrSymbols, ceil(nSym/2), 'R')
    return symb
        
        
def addSymbols(characters, words, symbolDensity, previousCharacters='', previousSymbolsFraction=0):
    nWords = len(words)
    if not previousCharacters:
        previousSymbolsFraction = 0
    symb = generateSymbols(characters, nWords, (1-previousSymbolsFraction)*symbolDensity)
    symb += generateSymbols(previousCharacters, nWords, previousSymbolsFraction*symbolDensity)        
    shuffle(symb)
    
    idx = linspace(0, len(words), len(symb))
    for i, s in enumerate(symb):
        words.insert(round((1+symbolDensity)*idx[i]), s)
    return words


def createLesson(currentTxt, words, word_wrap=60, characters_per_lesson=2000, min_word_length=4, max_word_length=100,
                 symbols_density=0.05, numbers_density=0.3, previous_symbols_fraction=0.4,
                 include_previous_numbers=False, max_number_length=3, max_letters_combination_length=4, **ignored):
    """Create a KTouch lesson for the characters passed as input."""
    print('Processing: ' + stripPositionMarkers(currentTxt))

    lettersIdx = characters.index(currentTxt)
    previousTxt = ''.join(characters[0:lettersIdx])
    previousLetters = stripPositionMarkers(''.join(re.findall(r'[^\W\d_]', previousTxt)))
    currentLetters = stripPositionMarkers(''.join(re.findall(r'[^\W\d_]', currentTxt)))

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
            lCount += len(w)
            goodWords.append(w)

    goodWords = addSymbols(currentTxt, goodWords, symbols_density, previousTxt, previous_symbols_fraction)
    
    # Add the numbers
    previousNumbers = re.findall(r'\d', previousTxt)
    currentNumbers = re.findall(r'\d', currentTxt)
    if include_previous_numbers:
        numbers = currentNumbers + previousNumbers
    else:
        numbers = currentNumbers
    if numbers:
        nNum = round(characters_per_lesson*numbers_density)
        numDictionary = generateCharsCombinations(numbers, max_number_length)
        for i in range(nNum):
            # Sample some numbers
            n = numDictionary[sample(range(len(numDictionary)), 1)[0]]
            # If current numbers is empty any picked number is ok to include
            # otherwise check that the selected number contains currentNumbers
            if not currentNumbers or re.search('[{0}]'.format(''.join(currentNumbers)), n):
                goodWords.append(n)
        shuffle(goodWords)

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
        '--numbers-density': Or(None, Coerce(float)),
        '--previous-symbols-fraction': Or(None, Coerce(float)),
        '--previous-numbers-fraction': Or(None, Coerce(float)),
        '--max-number-length': Or(None, Coerce(int)),
        '--max-letters-combination-length': Or(None, Coerce(int)),
        str: bool  # Treat all other arguments as bool
    })
    args = schema(args)

    try:
        args = schema(args)
    except error.MultipleInvalid as ex:
        print("\n".join([e.msg for e in ex.errors]))

    argoptions = {k.strip('--').replace('-', '_'): args[k] for k in args.keys() if '--' in k}

    # Dictionary file
    words = []
    if args['<dictionary>']:
        with open(args['<dictionary>']) as f:
            # Consider only first column, strip newlines, strip hypnetion information from some dictionaries
            words = [re.sub('/.*$', '', line.split(' ')[0].rstrip('\n').lower()) for line in f]
        # Shuffle words to avoid picking all the variations of the same word
        if not args['--no-shuffle-dict']:
            shuffle(words)

    with open(args['<charslist>']) as f:
        characters = [line.rstrip('\n') for line in f]

    # If we pass a line number (starting from zero) we create only the lesson for the specified letters
    # otherwise we create all the lessons
    # OUTPUT:
    # [letters].txt/xml
    # or
    # ktouch-lessons.txt/xml
    if args['--lesson-number']:
        charsIdx = args['--lesson-number'] - 1
        selectedChars = characters[charsIdx]
        outFileName = stripPositionMarkers(selectedChars) + '.txt'
        selectedChars = [selectedChars]  # Make list to process with for
    else:
        selectedChars = characters
        outFileName = args['--output'].rsplit(".", 1)[0]
        if args['--plain-text']:
            outFileName += '.txt'
        else:
            outFileName += '.xml'

    formattedLesson = ''
    with open(outFileName, 'w') as f:
        # First lesson is for sure empty, so it won't be processed, but still we write it to file as placeholder
        for currentChars in selectedChars:
            if currentChars:
                wd = createLesson(currentChars, words, **argoptions)
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