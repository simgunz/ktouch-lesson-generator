Ktouch lesson generator is a script that allows to automatically generate custom lessons for the typing tutor KTouch.

```
Usage:
  ktouch-lesson-generator.py [options] <charslist> [<dictionary>]

  Generate a set of ktouch lessons, one for each line in <charslist> file.
  If <dictionary> is not specified, it generates random combinations of letters instead of meaningful words.

Options:
  -n --lesson-number=<n>                   Line number of <charslist> corresponding ro the lesson to be generated. 
                                           If not specified all lessons are generated.
  -o --output=<outputfile>                 Output file [default: ktouch-lessons.txt]. If the lesson number is specified
                                           the file name will be the [selected characters].txt (e.g fj.txt)
  -w --word-wrap=<n>                       Wrap lesson text at this length. [default: 60]
     --characters-per-lesson=<n>           Number of characters in a lesson. [default: 2000]
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
The lessons to be generated are specified in the text file `<charslist>` by writing in each line the new characters
to be learned in each lesson.

In each lesson are included all the letters learned in the previous lessons.

The output is saved by default in a file called `ktouch-lessons.txt`. The lessons then need to be copied manually
into KTouch as 
The following file generates a full course to learn all the letters in the Italian alphabeth, the extra five English letters, the Italian accented letters, and the capital case version of all the letters.



```
italian_extended.txt:
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

To generate the lessons with random permutations  of the letters run the following command
(the lessons will be written to the file `ktouch-lessons.txt`)
```
python ktouch-lesson-generator.py italian_extended.txt.txt
```

If a dictionary file (containining one word per line) is specified, the script generates the lessons
using meaningful words. The first few lessons are still generated with random permutations of letters
given that there are not enough letters to pick meaningful words.
```
python ktouch-lesson-generator.py italian_extended.txt.txt dict-it.txt
```

Optionally we can generate a single lesson by specifying the corresponding line number in the `<charslist>` file.
This will generate a file named with the characters of the selected lesson, in this case `nt.txt`
```
python ktouch-lesson-generator.py -n 5 italian_extended.txt.txt dict-it.txt
```

If the generated lessons are too long, we can tune the length of each lesson as follows
```
python ktouch-lesson-generator.py --characters-per-lesson=1000 italian_extended.txt.txt dict-it.txt
```

Advanced usage
--------------

The script can also used to generate lessons to learn symbols instead of letters. Given that some symbols
usually go in a certain position respect to a word, we can specify the following specifiers in the lesson file:

- LL - The symbol can only go next to the left side of a word (e.g. LL[ -> [word )
- RR - The symbol can only go next to the right side of a word (e.g. RR: -> word: )
- LR - The symbol go next to a word either on the left or right side (e.g. LR" -> "word" )

In each lesson the symbols learned in the previous lessons are not included by default, this can be changed by 
specifying the flag `--include-previous-symbols`. By default a new symbol is appended/prepended to each word. 
It is possible to set the probability to add a symbol to each word by setting `--symbols-density=f` with `f` 
between 0 and 1.

The following is an example of `<charslist>` for learning new symbols.

```
basic-symbols.txt:
abcdefghijklmnopqrstuvwxyzRR,RR.
+-
RR?RR!
RR:RR;
LR"LR'
LL(RR)
LL[RR]
LL{RR}
```

When we generate lessons to learn symbols, it is useful to have normal words in the middle of the text to make the
typing more natural, but we may want to limit the length of the words to not waste time in typing letters instead of
symbols. The maximum length of the words can be tuned by setting the parameter `--max-word-length=n`.
```
python ktouch-lesson-generator.py --max-word-length=6 basic-symbols.txt english-dictionary.txt
```

Notes
-----
- The auto-generated lessons favour longer combination of letters
- The learning order of the new letters is important and different combinations need to be tried manually to optimize 
the result. E.g. in Italian the letter ‘q’ is always followed by the letter ‘u’, so if we try 
to learn the letter ‘q’ before ‘u’ the resulting lesson won’t contain any word including ‘q’. Another example is when in 
a lesson we try to learn an Italian common letter like ‘z’ together with an uncommon one like ‘y’; 
likely the resulting lesson will not contain any word including ‘y’. For this reason it is best to learn `y` and `w` 
together.
