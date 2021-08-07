Ktouch lesson generator
=======================

A script for automatically generating custom lessons for the typing tutor KTouch.

Basic usage
-----------

The lessons to be generated are specified in the text file `<charslist>`
by writing in each line the new characters to be learned in each lesson.

In each lesson all the letters learned in the previous lessons are included.

The output is saved by default in a file called `ktouch-lessons.xml`. This file can be directly imported to KTouch
from the Course Editor. After importing the xml file, the title of the course can be edited to set it to something
meaningful and the keyboard layout MUST be selected in order for the course to show up on the main screen of KTouch when
that specific keyboard layout is selected.

By specifying the flag `--plain-text`
the lessons are saved to a plain text file called `ktouch-lessons.txt`.
Each lesson can then be copied manually into the KTouch editor.
This can be useful when we need to add new lessons to an existing course.

The following file generates a full course
to learn all the letters in the Italian alphabeth,
the extra five English letters, the Italian accented letters,
and the capital case version of all the letters.

italian.txt:

```
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

To generate the lessons with random permutations of the letters,
run the following command
(the lessons will be written to the file `ktouch-lessons.xml`)

```
python ktouch-lesson-generator.py italian.txt
```

If a dictionary file (containining one word per line) is specified,
the script generates the lessons using meaningful words.
The first few lessons are still generated with random permutations of letters,
given that there are not enough letters to pick meaningful words.

```
python ktouch-lesson-generator.py italian.txt dict-it.txt
```

Optionally we can generate a single lesson by specifying the corresponding line number
in the `<charslist>` file.
This will generate a file named with the characters of the selected lesson,
in this case `nt.txt`

```
python ktouch-lesson-generator.py -n 5 italian.txt dict-it.txt
```

If the generated lessons are too long, we can tune the length of each lesson as follows

```
python ktouch-lesson-generator.py --characters-per-lesson=1000 italian.txt dict-it.txt
```

Advanced usage
--------------

The script can also used to generate lessons to learn symbols instead of letters.
Given that some symbols
usually go in a certain position respect to a word,
we can specify the following specifiers in the lesson file:

- LL - The symbol can only go next to the left side of a word
  (e.g. LL[ -> [word )
- RR - The symbol can only go next to the right side of a word
  (e.g. RR: -> word: )
- LR - The symbol go next to a word either on the left or right side
  (e.g. LR" -> "word" )

It is possible to set the density of symbols with respect the number of words by setting `--symbols-density=<f>`,
with `<f>` between 0 and 1, where `1` means as many symbols as words.
In each lesson the symbols learned in the previous lessons are included by default in a proportion of
40% respect the total number of symbols. The amount can be changed by specifying it with the command line
argument `--previous-symbols-fraction=<f>`.

This mechanism applies to numbers as well.

Note that a limitation of this implementation
is that we cannot generate lessons with only symbols or numbers;
it is necessary to have some letters in the current or previous lessons.

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

When we generate lessons to learn symbols,
it is useful to have normal words in the middle of the text
to make the typing more natural,
but we may want to limit the length of the words to not waste time in typing letters
instead of symbols.
The maximum length of the words can be tuned by setting the parameter `--max-word-length=n`.

```
python ktouch-lesson-generator.py --max-word-length=7 symbols_extended.txt dict-en_uk.txt
```

It is possible to specify the command line options
directly in the `<charslist>` file.
The options in the first line are applied to all the lessons.
It is possible to fine tune each lesson
by specifying custom options in the lesson line.

The following is an example of `<charslist>` that uses shorter words for the lessons
for learning symbols and numbers,
in order to waste less time in typing letters
and focusing more on the symbols and numbers.
The lessons of the numbers exclude the symbols.
The last lesson does not include new characters (marked with `--`).

```
## balance-words, characters-per-lesson=1000, lesson-title-prefix=Lezione
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
ABCDEFGHIJKLMNOPQRSTUVWXYZ          ## max-word-length=8
RR,RR.                              ## max-word-length=7
RR:LR'                              ## max-word-length=7
RR?RR!                              ## max-word-length=7
LR"RR;                              ## max-word-length=7
RR@-                                ## max-word-length=7
10                                  ## max-word-length=7, previous-symbols-fraction=0
29                                  ## max-word-length=7, previous-symbols-fraction=0
38                                  ## max-word-length=7, previous-symbols-fraction=0
47                                  ## max-word-length=7, previous-symbols-fraction=0
56                                  ## max-word-length=7, previous-symbols-fraction=0
--                                  ## characters-per-lesson=2000
```

For a complete list of advanced options please refer to the help of the script.

Notes
-----

- The auto-generated lessons favour longer combination of letters
- The learning order of the new letters is important and different combinations need to be tried manually to optimize
the result. E.g. in Italian the letter ‘q’ is always followed by the letter ‘u’, so if we try
to learn the letter ‘q’ before ‘u’ the resulting lesson won’t contain any word including ‘q’. Another example is when in
a lesson we try to learn an Italian common letter like ‘z’ together with an uncommon one like ‘y’;
likely the resulting lesson will not contain any word including ‘y’. For this reason it is best to learn `y` and `z`
together. It is possible to mitigate this problem specifying the flag `--balance-words`.

License MIT
-----------

Project License can be found in [LICENSE.md](https://github.com/simgunz/ktouch-lesson-generator/blob/master/LICENSE.md).
