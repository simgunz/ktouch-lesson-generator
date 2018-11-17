Ktouch lesson generator is a script that allows to generate automatically custom lessons for the typing tutor KTouch.

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

```
python ktouch-lesson-generator.py basic-symbols.txt english-dictionary.txt
```
