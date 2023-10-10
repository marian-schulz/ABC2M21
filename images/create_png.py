# Importing the module
import os
from pathlib import Path
from ABC2M21 import ABCTranslator
from music21 import lily, environment, musicxml, converter
a = environment.Environment()

musecores = ['/home/mschulz/Anwendungen/MuseScore-3.6.0.451381076-x86_64.AppImage',
             '/home/mschulz/Anwendungen/MuseScore-4.1.1.232071203-x86_64.AppImage',
             '/home/mschulz/local/bin/MuseScore-4.1.1','/home/mschulz/local/bin/MuseScore',
             '/usr/bin/musescore']

for musecore in musecores:
    if Path(musecore).is_file():
        a['musicxmlPath'] = musecore
        a['musescoreDirectPNGPath'] = musecore
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
T:Pitch octaves
L:1/1
K:C
   C, D, E, F, G, A, B, C D E F G A B c d e f g a b c' d' e' f' g' a' b' |
w: C, D, E, F, G, A, B, C D E F G A B c d e f g a b c' d' e' f' g' a' b'
"""

abc_accidentals = """
X:1
T: Accidentals
L:1/1
K:C
   ^C     _D   =E      ^^F          __G
w: sharp  flat natural double~sharp double~flat

"""

abc_note_duration = """
X:1
T:Relative durations
L:1/4
M:none
K:C
   C4   C3   C2   C3/2  C    C/2  C//   C///  C////
w: 1/1  3/4  1/2  3/8   1/4  1/8  1/16  1/32  1/64 
"""

abc_user_defined_symbols = """
X: 1
L: 1/4
T: User defined symbols
U: W = !trill!
U: U = !staccato!
U: V = !fermata!
K:C
WC UD VE .F
"""

abc_decoration_spanner = """
X: 1
T:Decoration spanner
L:1/4
K:C
!<(!ABCD!<)! !>(!ABCD!>)! !trill(!ABCD!trill)!|
"""

abc_propagate_accidentals = """
X:1
T:Propagate-accidentals directive
M:4/4
L:1/4
K:C
[V:1 name="octave"]
[I:propagate-accidentals octave]
   ^C C  D c | C ^C C  c |
w: C# C# D C | C C# C# C |
[V:2 name="pitch"]
[I:propagate-accidentals pitch]
   ^C C  D c   | C ^C C  c  |
w: C# C# D C#  | C C# C# C# |
[V:3 name="not"]
[I:propagate-accidentals not]
   ^C C  D c | C ^C C c |
w: C# C  D C | C C# C C |
"""

#s = ABCTranslator(abc_propagate_accidentals)
#s.show()
#exit()

# delete old pngs
for filename in os.listdir():
    if filename.endswith(".png"):
        os.remove(filename)

for name, abc_tune in dict(locals()).items():
    if not name.startswith('abc_'):
        continue

    m21_stream = ABCTranslator(abc_tune)
    #m21_stream.show()
    xmlconv = converter.subConverters.ConverterMusicXML()
    xmlconv.write(m21_stream, fmt='musicxml', fp=f"{name[4:]}.png", subformats=['png'])


# delete all except png and py files
for filename in os.listdir():
    if filename.endswith(".py"):
        continue
    if filename.endswith(".png"):
        if filename.endswith("-1.png"):
            os.rename(filename, f"{filename[:-6]}.png")
        continue

    os.remove(filename)
