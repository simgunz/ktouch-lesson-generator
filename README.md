Ktouch lesson generator is a script for automatically generating custom lessons for the typing tutor KTouch.

```
Usage: ktouch-lesson-generator.py [options] <charslist> [<dictionary>]

Generate a set of ktouch lessons, one for each line in <charslist> file.
If <dictionary> is not specified, it generates random combinations of letters instead of meaningful words.rslist> file.

Options:
  -n --lesson-number=<n>                    Line number of <charslist> corresponding to the lesson to be generated.
                                            If not specified all lessons are generated.harslist> corresponding to the lesson to be generated.
  -o --output=<outputfile>                  Output file name. If the lesson number is specified the file name will be theall lessons are generated.
                                            [selected characters].xml/txt (e.g fj.xml/txt). [default: ktouch-lessons.xml/txt] If the lesson number is specified the file name will be the
  -p --plain-text                           Output the lessons in plain text instead of XMLers].xml/txt (e.g fj.xml/txt). [default: ktouch-lessons.xml/txt]
  -w --word-wrap=<n>                        Wrap lesson text at this length. [default: 60]s in plain text instead of XML
  -l --characters-per-lesson=<n>            Number of characters in a lesson. [default: 2000]at this length. [default: 60]
      --exclude-previous-letters            Exclude letters from the previous lessonsers in a lesson. [default: 2000]
      --max-letters-combination-length=<n>  Maximum length of the generated combinations of letter (for first 2-3rom the previous lessons
                                            lessons). [default: 4] the generated combinations of letter (for first 2-3
      --min-word-length=<n>                 Minimum length a word must have to be included in the lesson. [default: 4]t: 4]
      --max-word-length=<n>                 Maximum length a word must have to be included in the lesson. [default: 100]word must have to be included in the lesson. [default: 4]
      --symbols-density=<f>                 Fraction of symbols that should be put in the lesson respect to the numberword must have to be included in the lesson. [default: 100]
                                            of words. [default: 1]ls that should be put in the lesson respect to the number
      --previous-symbols-fraction=<f>       Fraction of symbols from the previous lessons respect the total number oft: 1]
                                            symbols. Set to 0 to include only symbols from the current lesson. [default: 0.4]ls from the previous lessons respect the total number of
      --numbers-density=<f>                 Fraction of numbers that should be put in the lesson respect to the number to include only symbols from the current lesson. [default: 0.4]
                                            of words. [default: 1]                                          rs that should be put in the lesson respect to the number
      --exclude-previous-numbers            Include only numbers from the current lesson.t: 1]                                          
      --max-number-length=<n>               Maximum length of the generated numbers. [default: 3]ers from the current lesson.
      --no-shuffle-dict                     Do not shuffle the dictionary file. Useful if the dictionary file is a the generated numbers. [default: 3]
                                            frequency list and we want to prioritize picking the most common wordse dictionary file. Useful if the dictionary file is a
                                            on the top of the list. If the dictionary is sorted alphabetically shufflingd we want to prioritize picking the most common words
                                            the words allows avoiding picking all the variations of the same word.  list. If the dictionary is sorted alphabetically shuffling
      --lesson-title-prefix=<prefix>        Prefix for the name of the lesson. [default: Lesson]
      --balance-words                       Try to collect words with rare letters when the lesson contain a rare and frequent letter
                                            (e.g 'zy' in Italian will likely pick only words with 'z')
  -h --help                                 Show this screen.avoiding picking all the variations of the same word. 
  -v --version                              Show version.

```

Basic usage
-----------
The lessons to be generated are specified in the text file `<charslist>` by writing in each line the new characters
to be learned in each lesson.

In each lesson all the letters learned in the previous lessons are included.

The output is saved by default in a file called `ktouch-lessons.xml`. This file can be directly imported to KTouch 
from the Course Editor. After importing the cml file, the title of the course can be edited to set it to something
meaningful and the keyboard layout MUST be selected in order for the course to show up on the main screen of KTouch when
that specific keyboard layout is selected.

By specifying the flag `--plain-text` the lessons are saved to a plain text file called `ktouch-lessons.txt`.
Each lesson can then be copied manually into the KTouch editor. This can be useful when we need to add new lessons to
an existing course.

The following file generates a full course to learn all the letters in the Italian alphabeth, the extra five English letters, the Italian accented letters, and the capital case version of all the letters.

```
italian.txt:
jf
kd
ls
ca
nt
iv
me
hr
go
bp
qu
wxy
z
èù
éì
òà
àèéìòù
ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

To generate the lessons with random permutations  of the letters run the following command
(the lessons will be written to the file `ktouch-lessons.xml`)
```
python ktouch-lesson-generator.py italian.txt
```

If a dictionary file (containining one word per line) is specified, the script generates the lessons
using meaningful words. The first few lessons are still generated with random permutations of letters
given that there are not enough letters to pick meaningful words.
```
python ktouch-lesson-generator.py italian.txt dict-it.txt
```

Optionally we can generate a single lesson by specifying the corresponding line number in the `<charslist>` file.
This will generate a file named with the characters of the selected lesson, in this case `nt.txt`
```
python ktouch-lesson-generator.py -n 5 italian.txt dict-it.txt
```

If the generated lessons are too long, we can tune the length of each lesson as follows
```
python ktouch-lesson-generator.py --characters-per-lesson=1000 italian.txt dict-it.txt
```

Advanced usage
--------------
The script can also used to generate lessons to learn symbols instead of letters. Given that some symbols
usually go in a certain position respect to a word, we can specify the following specifiers in the lesson file:

- LL - The symbol can only go next to the left side of a word (e.g. LL[ -> [word )
- RR - The symbol can only go next to the right side of a word (e.g. RR: -> word: )
- LR - The symbol go next to a word either on the left or right side (e.g. LR" -> "word" )

It is possible to set the density of symbols with respect the number of words by setting `--symbols-density=<f>` 
 with `<f>` between 0 and 1, where  means as many symbols as words.
In each lesson the symbols learned in the previous lessons are included by default in a proportion of
40% respect the total number of symbols. The amount can be changed by specifying it with the command line 
argument `--previous-symbols-fraction=<f>`.

This mechanism applies to numbers as well.

Note that a limitation of this implementation is that we cannot generate lessons with only symbols or
numbers, but it is necessary to have some letters in the current or previous lessons.

The following is an example of `<charslist>` for learning new symbols.

```
symbols_extended.txt:
abcdefghijklmnopqrstuvwxyzRR,RR.
RR?RR!
RR:$
LR"*
LL(RR)
LL[RR]
LL{RR}
+&
=~
LR`\
/RR@
^RR;
%-
LL#LR'
_|
<>
```

When we generate lessons to learn symbols, it is useful to have normal words in the middle of the text to make the
typing more natural, but we may want to limit the length of the words to not waste time in typing letters instead of
symbols. The maximum length of the words can be tuned by setting the parameter `--max-word-length=n`.
```
python ktouch-lesson-generator.py --max-word-length=7 symbols_extended.txt dict-en_uk.txt
```

Notes
-----
- The auto-generated lessons favour longer combination of letters
- The learning order of the new letters is important and different combinations need to be tried manually to optimize 
the result. E.g. in Italian the letter ‘q’ is always followed by the letter ‘u’, so if we try 
to learn the letter ‘q’ before ‘u’ the resulting lesson won’t contain any word including ‘q’. Another example is when in 
a lesson we try to learn an Italian common letter like ‘z’ together with an uncommon one like ‘y’; 
likely the resulting lesson will not contain any word including ‘y’. For this reason it is best to learn `y` and `w` 
together. It is possible to mitigate this problem specifying the flag `--balance-words`.

License MIT
-----------
Project License can be found [here](https://github.com/simgunz/ktouch-lesson-generator/blob/master/LICENSE.md).
