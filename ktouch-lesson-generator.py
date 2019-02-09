#!/usr/bin/python
"""
Usage: ktouch-lesson-generator.py [options] <charslist> [<dictionary>]

Generate a set of ktouch lessons, one for each line in <charslist> file.
If <dictionary> is not specified, it generates random combinations of letters instead of meaningful words.

Options:
  -n NUM, --lesson-number NUM                Line number of <charslist> corresponding to the lesson to be generated.
                                             If not specified all lessons are generated.
  -o FILE, --output FILE                     Output file name. If the lesson number is specified the file name will
                                             be the[selected characters].xml/txt (e.g fj.xml/txt).
                                             [default: ktouch-lessons.xml/txt]
  -p, --plain-text                           Output the lessons in plain text instead of XML
  -w NUM, --word-wrap NUM                    Wrap lesson text at this length. [default: 60]
  -l NUM, --characters-per-lesson NUM        Number of characters in a lesson. [default: 2000]
      --exclude-previous-letters             Exclude letters from the previous lessons
      --max-letters-combination-length NUM   Maximum length of the generated combinations of letter (for first 2-3
                                             lessons). [default: 4]
      --min-word-length NUM                  Minimum length a word must have to be included in the lesson. [default: 1]
      --max-word-length NUM                  Maximum length a word must have to be included in the
                                             lesson. [default: 100]
      --symbols-density NUM                  Fraction of symbols that should be put in the lesson respect to the number
                                             of words. [default: 1]
      --previous-symbols-fraction NUM        Fraction of symbols from the previous lessons respect the total number of
                                             symbols. Set to 0 to include only symbols from the current lesson.
                                             [default: 0.4]
      --numbers-density NUM                  Fraction of numbers that should be put in the lesson respect to the number
                                             of words. [default: 1]
      --exclude-previous-numbers             Include only numbers from the current lesson.
      --max-number-length NUM                Maximum length of the generated numbers. [default: 3]
      --no-shuffle-dict                      Do not shuffle the dictionary.
      --crop-dict NUM                        Keep only the first NUM words from the dictionary. (If zero keep them
                                             all.) [default: 0]
      --lesson-title-prefix PREFIX           Prefix for the name of the lesson. [default: Lesson]
      --balance-words                        Try to collect words with rare letters when the lesson contain a rare and
                                             frequent letter (e.g 'zy' in Italian will likely pick only words with 'z')
  -h, --help                                 Show this screen.
  -v, --version                              Show version.

Format of <charslist> file:
<charslist> is a file containing the new letters of each lesson. Every line is a new lesson.
A position for the symbols can be specified as:
LL: Next to the left word boundary
RR: Next to the right word boundary
LR: Next to the left or right word boundary

Example characters.txt:
jf
èy
ABCDEFGHIJKLMNOPQRSTUVWXYZ
LR"$
LL(RR)

It is possible to specify the command line options inside the <charslist> file as follow:
- Add global options in the first line after ## starting at the beginning of the line
- Add per-lesson option adding ## and the options after the lesson new characters

To create a lesson without new characters add a double dash (--) in the lesson line

Example characters.txt (with options):
## characters-per-lesson=1000, balance-words
jf
èy
ABCDEFGHIJKLMNOPQRSTUVWXYZ  ## balance-words=false
LR"$
LL(RR)
10                          ## max-word-length=7, previous-symbols-fraction=0
29                          ## max-word-length=7, previous-symbols-fraction=0
--                          ## characters-per-lesson=1500
"""

import itertools
import re
import textwrap
import uuid
import warnings

from docopt import docopt
from math import floor, ceil
from random import shuffle, choices, sample, random
from voluptuous import Schema, Coerce, Or, error, Boolean

RE_POSITION_MARKERS = re.compile(r'(LL|RR|LR)')
RE_SYMBOLS = re.compile(r'[\W_]')
RE_LEFT_SYMBOLS = re.compile(r'LL([\W_])')
RE_RIGHT_SYMBOLS = re.compile(r'RR([\W_])')
RE_LEFTRIGHT_SYMBOLS = re.compile(r'LR([\W_])')
RE_LETTERS = re.compile(r'[^\W\d_]')
RE_DIGITS = re.compile(r'\d')

NO_NEW_CHARS = '--'


def argsSchema(args):
    """Convert the argument values from text to the correct type"""
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
        '--lesson-title-prefix': Or(None, str),
        '--crop-dict': Or(None, Coerce(int)),
        str: Boolean()  # Treat all other arguments as bool
    })
    try:
        args = schema(args)
    except error.MultipleInvalid as ex:
        print("\n".join([e.msg for e in ex.errors]))
    return args


def args2options(args):
    """Parse the command line args by stripping the -- and replacing - with _"""
    return {k.strip('--').replace('-', '_'): args[k] for k in args.keys() if '--' in k}


def charsToPrint(chars):
    """Return a string that identifies the new characters"""
    if chars == '':
        return 'No new characters'
    else:
        return chars


def parseLessonLine(line):
    """Return the characters of the lesson and the lesson custom options"""
    options = dict()
    line_tokens = line.split('##')
    chars = line_tokens[0].strip()
    chars = chars.replace(NO_NEW_CHARS, '')
    if len(line_tokens) > 1:
        args = line_tokens[1].split(',')
        for arg in args:
            temp = arg.split('=')
            key = '--{0}'.format(temp[0].strip())
            if len(temp) > 1:
                value = temp[1].strip()
            else:
                value = True
            options[key] = value
    options = argsSchema(options)
    return chars, args2options(options)


def generateCharsCombinations(elements, maxLength):
    """Return an array of strings containing different permutations of combinations of the elements
    of different lengths up to the specified maximum length
    E.g. 'ab' -> ['a' 'b' 'aa' 'ab' 'ba' 'bb']
    """
    return list({''.join(p) for i in range(maxLength)
                for c in itertools.combinations_with_replacement(''.join(elements), i+1)
                for p in itertools.permutations(c)})


def stripPositionMarkers(txt):
    return re.sub(RE_POSITION_MARKERS, '', txt)


def linspace(a, b, n):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [diff*i + a for i in range(n)]


def insertUniformly(words, items):
    """Insert the items between the words in a equidistributed way"""
    symbolDensity = len(items)/len(words)
    idx = linspace(0, len(words)*round(1+symbolDensity), len(items))
    for i, s in enumerate(items):
        words.insert(round(idx[i]), s)


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
    if not re.search(RE_SYMBOLS, previousCharacters):
        previousSymbolsFraction = 0
    symb = generateSymbols(characters, nWords, (1-previousSymbolsFraction)*symbolDensity)
    symb += generateSymbols(previousCharacters, nWords, previousSymbolsFraction*symbolDensity)
    shuffle(symb)
    words = insertUniformly(words, symb)


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


def createLesson(lessonIdx, lessons, words, word_wrap=60, characters_per_lesson=2000,
                 exclude_previous_letters=False, min_word_length=1, max_word_length=100,
                 symbols_density=1, numbers_density=1, previous_symbols_fraction=0.4,
                 exclude_previous_numbers=False, max_number_length=3, max_letters_combination_length=4,
                 balance_words=False, no_shuffle_dict=False,  **ignored):
    """Create a KTouch lesson for the characters passed as input."""
    currentChars = parseLessonLine(lessons[lessonIdx])[0]
    previousChars = ''.join([parseLessonLine(l)[0] for l in lessons[0:lessonIdx]])
    previousLetters = stripPositionMarkers(''.join(re.findall(RE_LETTERS, previousChars)))
    currentLetters = stripPositionMarkers(''.join(re.findall(RE_LETTERS, currentChars)))

    print('Processing: {0}'.format(stripPositionMarkers(charsToPrint(currentChars))))

    # Find if in the currentLetters there is at least a real letter (a non-symbol)
    # and set the regular expression for picking the correct words from the dictionary.
    RE_MATCHED_WORD = ''
    if currentLetters:
        if exclude_previous_letters:
            RE_MATCHED_WORD = '[{0}]+$'.format(currentLetters)
        else:
            RE_MATCHED_WORD = '[{0}{1}]*[{0}]+[{0}{1}]*$'.format(currentLetters, previousLetters)
    elif not exclude_previous_letters and previousLetters:
        RE_MATCHED_WORD = '[{0}]+$'.format(previousLetters)

    if not no_shuffle_dict:
        # Shuffle words to avoid picking all the variations of the same word
        # and to avoid having the same words in different lessons
        shuffle(words)

    selectedWords = []
    if RE_MATCHED_WORD:
        lCount = 0
        lCountPerLetter = dict()
        for x in currentLetters:
            lCountPerLetter[x] = 0
        for w in words:
            if any(x.isupper() for x in currentLetters):
                # If any of the new letters is a capital one we capitalize the first letter of all the words
                w = w.title()
            elif any(x.isupper() for x in previousLetters) and round(random()):
                # If any of the previous letters is a capital one we capitalize the first letter of half the words
                w = w.title()
            # Select a word with at least MINWORDLENGTH letters that contains at least one of the
            # letters of the current lesson, and is made only by letters present in the past
            # lessons (beside the current one).
            # For symbols/numbers the words isn't required to contain them, because they are added after
            # so we only check against previousLetters.
            # The process stops when we select enough words to fill the lesson as specified by LETTERSPERLESSON
            # or when we exhausted the dictionary.
            if re.match(RE_MATCHED_WORD, w):
                if len(w) >= min_word_length and len(w) <= max_word_length:
                    # Try to collect also words containing not frequent letters
                    # The result can still be imbalanced but at least there will be some words
                    # with the less frequent letter
                    if balance_words:
                        dropWord = False
                        for x in currentLetters:
                            if re.search(x, w):
                                if lCountPerLetter[x] > characters_per_lesson/len(currentLetters):
                                    dropWord = True
                                    break
                                lCountPerLetter[x] += len(w)
                        if dropWord:
                            continue
                    lCount += len(w)
                    selectedWords.append(w)
                    if lCount > characters_per_lesson:
                        break

    # For the first 2-3 lesson the previous block fails, or it is skipped if exclude_previous_letters
    # is True so we need to generate the lesson as combinations/permutations of letters
    if not selectedWords:
        letters = ''
        if currentLetters:
            letters += currentLetters
        if not exclude_previous_letters:
            letters += previousLetters
        if letters:
            letterCombDict = generateCharsCombinations(letters, max_letters_combination_length)
            if currentLetters:
                RE_CURRENT_LETTERS = re.compile('[{0}]'.format(''.join(currentLetters)))
                letterCombDict = [w for w in letterCombDict if re.search(RE_CURRENT_LETTERS, w)]
            while lCount < characters_per_lesson:
                # Pick a word randonly from the generated dictionary
                w = letterCombDict[sample(range(len(letterCombDict)), 1)[0]]
                if any(x.isupper() for x in currentLetters):
                    # If any of the new letters is a capital one we capitalize the first letter of all the words
                    w = w.title()
                elif any(x.isupper() for x in previousLetters) and round(random()):
                    # If any of the previous letters is a capital one we capitalize the first letter of half the words
                    w = w.title()
                lCount += len(w)
                selectedWords.append(w)

    if selectedWords:
        shuffle(selectedWords)
        addSymbols(selectedWords, currentChars, symbols_density, previousChars, previous_symbols_fraction)
        addNumbers(selectedWords, currentChars, numbers_density, previousChars,
                   exclude_previous_numbers, max_number_length)
        # Check that the lesson is long enough otherwise extend it by duplicating the words
        clonedWords = list(selectedWords)
        while len(''.join(selectedWords)) < characters_per_lesson:
            # Scramble the cloned words to make it less repetitive
            shuffle(clonedWords)
            selectedWords += clonedWords

    # Convert the array to text
    goodWordsText = ' '.join(selectedWords)
    # Remove loose symbols at the begin or end of the text
    goodWordsText = re.sub(r'^[LR][\W_]\s*', '', goodWordsText)
    goodWordsText = re.sub(r'[LR][\W_]\s*$', '', goodWordsText)
    # Remove the postion markers L and R and the corresponding space to position the symbol
    goodWordsText = re.sub(r'L(\W) ', r'\1', goodWordsText)
    goodWordsText = re.sub(r' R(\W)', r'\1', goodWordsText)
    # Cut the lesson to the right size
    goodWordsText = goodWordsText[:characters_per_lesson]
    # Remove trailing spaces
    goodWordsText = re.sub(r'\S*$', '', goodWordsText)

    # Wrap the text (KTouch required wrapping at 60)
    wrappedLesson = '\n'.join(textwrap.wrap(goodWordsText, word_wrap))

    # Issue warnings if the generated lesson is empty
    if not wrappedLesson:
        warnMsg = 'Empty lesson generated for "{0}". '.format(stripPositionMarkers(currentChars))
        if exclude_previous_letters:
            warnMsg += 'Try without the --exclude_previous_letters flag.'
        else:
            warnMsg += 'Try generating a lesson with letters before those with numbers or symbols.'
        warnings.warn(warnMsg)

    return wrappedLesson


def formatLessonPlainText(currentChars, lessonText):
    lesson = 'New characters: {0}\n'.format(stripPositionMarkers(charsToPrint(currentChars)))
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
        <lessons>""").format(id=uniqueid, shortid=uniqueid[:8])


def lessonXMLFooter():
    return textwrap.dedent("""
        </lessons>
        </course>""")


def replaceInvalidXMLCharacters(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    return text


def formatLessonXML(currentChars, lessonText, lessonNumber='', lessonPrefix='Lesson'):
    lessonText = replaceInvalidXMLCharacters(lessonText)
    currentChars = replaceInvalidXMLCharacters(currentChars)
    currentChars = stripPositionMarkers(currentChars)
    lessonTitle = '{prefix} {number} - {newChars}'.format(
        prefix=lessonPrefix, number=lessonNumber, newChars=charsToPrint(currentChars))
    lesson = """
    <lesson>
    <id>{{{id}}}</id>
    <title>{title}</title>
    <newCharacters>{newChars}</newCharacters>
    <text>{lessonText}</text>
    </lesson>""".format(id=uuid.uuid4(), title=lessonTitle, newChars=currentChars, lessonText=lessonText)
    return lesson


if __name__ == '__main__':
    # Parse docopt using schema to cast to correct type
    args = docopt(__doc__, version='1.0')
    args = argsSchema(args)
    # Create an argument list from docopt to pass it easily to createLesson
    argoptions = args2options(args)

    # Acquire the dictionary file
    words = []
    if args['<dictionary>']:
        with open(args['<dictionary>']) as f:
            # Consider only first column, strip newlines, strip hypnetion information from some dictionaries
            words = [re.sub('/.*$', '', line.split(' ')[0].rstrip('\n').lower()) for line in f]
            if args['--crop-dict']:
                words = words[:args['--crop-dict']]

    # Acquire the list of characters corresponding to lessons
    with open(args['<charslist>']) as f:
        lessons = [line.rstrip('\n') for line in f if line.rstrip('\n')]

    if lessons[0].startswith('##'):
        _, customOptions = parseLessonLine(lessons[0])
        argoptions.update(customOptions)
        del(lessons[0])

    # If we pass a line number (starting from one) create only the corresponding lesson
    # otherwise create all the lessons
    if argoptions['lesson_number']:
        lessonIdx = argoptions['lesson_number'] - 1
        selectedLessons = lessons[lessonIdx]
        outFileName = stripPositionMarkers(selectedLessons)
        selectedLessons = [selectedLessons]  # Make list to process with for
    else:
        selectedLessons = lessons
        outFileName = argoptions['output'].rsplit(".", 1)[0]
    if argoptions['plain_text']:
        outFileName += '.txt'
    else:
        outFileName += '.xml'

    formattedLesson = ''
    with open(outFileName, 'w') as f:
        # First lesson is for sure empty, so it won't be processed, but still we write it to file as placeholder
        for lessonIdx, currentLesson in enumerate(selectedLessons):
            currentArgoptions = dict(argoptions)
            currentChars, customOptions = parseLessonLine(currentLesson)
            currentArgoptions.update(customOptions)
            wd = createLesson(lessonIdx, selectedLessons, words, **currentArgoptions)
            # Write the lesson to file
            if argoptions['plain_text']:
                formattedLesson += formatLessonPlainText(currentChars, wd)
            else:
                formattedLesson += formatLessonXML(currentChars, wd, lessonIdx + 1, argoptions['lesson_title_prefix'])
        if argoptions['plain_text']:
            f.write(formattedLesson)
        else:
            f.write(lessonXMLHeader())
            f.write(formattedLesson)
            f.write(lessonXMLFooter())
