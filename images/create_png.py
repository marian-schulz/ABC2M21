# Importing the module
import os
from pathlib import Path
from ABC2M21 import ABCTranslator
from music21 import lily, environment
a = environment.Environment()

musecores = ['/home/mschulz/Anwendungen/MuseScore-3.6.0.451381076-x86_64.AppImage',
             '/home/mschulz/Anwendungen/MuseScore-4.1.1.232071203-x86_64.AppImage',
             '/home/mschulz/local/bin/MuseScore','/home/mschulz/local/bin/MuseScore-4.1.1',
             '/usr/bin/musescore']

for musecore in musecores:
    if Path(musecore).is_file():
        a['musicxmlPath'] = musecore
        break

# Getting the current working directory
cwd = os.getcwd()

abc_twinkle = """
X:1
T:Twinkle, Twinkle Little Star in C
M:C
K:C
L:1/4
vC C G G|A A G2|F F E E|D D C2|vG G F F|E E D2|
uG G F F|E E D2|vC C G G|A A G2|uF F E E|D D C2|]
"""

abc_pitch_octaves = """X:1
L:1/8
K:
C, D, E, F, G, A, B, x | C D E F G A B x | c d e f g a b x | c' d' e' f' g' a' b' x
w: C, D, E, F, G, A, B, | C D E F G A B | c d e f g a b | c' d' e' f' g' a' b' 
"""

abc_accidentals = """
X:1
L:1/1
K:
^C | _D | =E | ^^F | __G
w: sharp | flat | natural | double sharp | double flat 
"""

abc_note_duration = """
X:1
L:1/4
M:none
K:C
   C4   C4   C3   C3/2 C3/   C    C/2  C/   C/4  C//   C/8  C///  C/16 C////
w: 1/1  1/2  3/4  3/8  -     1/4  1/8  -    1/16 -     1/32 -     1/64 -
"""
for name, abc_tune in dict(locals()).items():
    if not name.startswith('abc_'):
        continue

    m21_stream = ABCTranslator(abc_tune)
    #m21_stream.show()
    lpc = lily.translate.LilypondConverter()
    lpc.loadFromMusic21Object(m21_stream)
    lpc.createPNG(name[4:])


for filename in os.listdir(''):
    if filename.endswith(".py") or filename.endswith(".png"):
        continue
    os.remove(filename)
