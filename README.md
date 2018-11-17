Ktouch lesson generator is a script that allows to generate automatically custom lessons for the typing tutor KTouch.

```
Usage:
  ktouch_lesson_generator [options] <letterslist> [<dictionary>]

  Generate a set of ktouch lessons, one for each line in <letterslist> file.
  If dictionary is not specified generates random combinations of letters instead of meaningful words.

Options:
  -n --lesson-number=<n>                   Line number of the lesson to be generated. If not specified all lessons are
                                           generated.
  -o --output=<outputfile>                 Output file [default: ktouch-lessons.txt]. If the lesson number is specified
                                           the file name will be the [selected letters].txt (e.g fj.txt)
  -w --word-wrap=<n>                       Wrap lesson text at this length. [default: 60]
     --letters-per-lesson=<n>              Number of letters in a lesson. [default: 2000]
     --min-word-length=<n>                 Minimum length a word must have to be included in the lesson. [default: 4]
     --max-word-length=<n>                 Maximum length a word must have to be included in the lesson. [default: 100]
     --symbols-density=<f>                 Amount of symbols that should be put in the lesson. [default: 1]
     --numbers-density=<f>                 Amount of numbers that should be put in the lesson. [default: 0.3]
     --include-previous-symbols            Set to 0 to include only symbols from the current lesson. [default: False]
     --include-previous-numbers            Set to 0 to include only numbers from the current lesson. [default: False]
     --max-number-length=<n>               Maximum length of the generated numbers. [default: 3]
     --max-letters-combination-length=<n>  Maximum length of the generated combinations of letter (for first 2-3 
                                           lessons). [default: 4]
  -h --help                                Show this screen.
  -v --version                             Show version.

```

Basic usage
-----------
The lessons to be generated are specified in a text file <letterslist> by writing in each line the new letters
to be learned in each lesson.

In each lesson are included all the letters learned in the previous lessons.

The following file generates a full course to learn all the letters in the Italian alphabeth, the extra five English letters, the Italian accented letters, and the capital case version of all the letters.

italian-extended-letters.txt

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
wx
zy
èé
éì
òà
ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

To generate the lessons, which will be written to the file ktouch-lessons.txt, with random permutations 
of the letters run:
```
python ktouch-lesson-generator.py italian-extended-letters.txt
```

If a dictionary file (containining one word per line) is specified, the script generates the lessons
using meaningful words. The first few lessons are still generated with random permutations of letters
given that there are not enough letters to pick meaningful words.
```
python ktouch-lesson-generator.py italian-extended-letters.txt italian-dictionary.txt
```

Optionally we can generate a single lesson by specifying the corresponding line number. This will generate
a file named with the letters of the selected lesson, in this case nt.txt
```
python ktouch-lesson-generator.py -n 5 italian-extended-letters.txt italian-dictionary.txt
```

If the generated lessons are too long, we can tune the length of each lesson as follows
```
python ktouch-lesson-generator.py --letters-per-lesson=1000 italian-extended-letters.txt italian-dictionary.txt
```

Advanced usage
--------------

The script can also used to generate lessons to learn symbols instead of letters. Given that some symbols
usually go in a certain position respect to a word, we can specify the following specifiers in the lesson file:

- LL - The symbol can only go next to the left side of a word
- RR - The symbol can only go next to the right side of a word
- LR - The symbol go next to a word either on the left or right side

In each lesson the symbols learned in the previous lessons are not included by default, this can be changed by 
specifying the flag `--include-previous-symbols`. By default a new symbol is appended/prepended to each word. 
Tt is possible to set how often the symbols appears by setting `--symbols-density=f` with f between 0 and 1

The following is an example of letters file for learning new symbols.

basic-symbols.txt```
abcdefghijklmnopqrstuvwxyzRR,RR.
+-
RR?RR!
RR:RR;
LR"LR'
LL(RR)
LL[RR]
LL{RR}
```

When we generate lessons to learn symbols it is useful to have normal words in the middle of the text to make the
typing more natural, but we may want to limit the length of the words to not waste time in typing letters instead of
symbols. The maximum length of the words can be tuned setting the parameter `--max-word-length=n`.
```
python ktouch-lesson-generator.py --max-word-length=6 basic-symbols.txt english-dictionary.txt
```
