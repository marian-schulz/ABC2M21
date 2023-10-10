
# ABC Elements

The following section shows images, how the translator creates music21 objects 
from abc elements. 
The abc fragments were converted into music21 streams and then used to generate images with musescore.

Example:
```
from ABC2M21 import ABCTranslator 
from music21 import converter, environment

abc_tune = """
X:1
T:Twinkle, Twinkle Little Star in C
M:C
K:C
L:1/4
vC C G G|A A G2|F F E E|D D C2|vG G F F|E E D2|
uG G F F|E E D2|vC C G G|A A G2|uF F E E|D D C2|]
"""

a = environment.Environment()
a['musescoreDirectPNGPath'] = '/path/to/musescore'

m21_stream = ABCTranslator(abc_tune)
xmlconv = converter.subConverters.ConverterMusicXML()
xmlconv.write(m21_stream, fmt='musicxml', fp="myfile.png", subformats=['png'])
```
![twinkle](images/twinkle.png)

## Pitches Across Various Octaves

Example:
```
X:1
T: Pitches Across Various Octaves
L:1/8
K:C
K:C
   C, D, E, F, G, A, B, C D E F G A B c d e f g a b c' d' e' f' g' a' b' |
w: C, D, E, F, G, A, B, C D E F G A B c d e f g a b c' d' e' f' g' a' b' 
```
![abc pitches over serval octave](images/pitch_octaves.png)

## Accidentals
In ABC notation, accidentals are written before the note using symbols such as ^ (sharp), = (natural), and _ (flat). 
Double sharps and flats are denoted by ^^ and __ respectively.
```
X:1
T: accidentals
L:1/8
K:C
^C _D =E ^^F __G
```
![abc pitches over serval octave](images/accidentals.png)

## Note duration
The note duration is relative to the `unit not length`.

```
X:1
T:Relative durations
L:1/4
M:none
K:C
   C4   C3   C2   C3/2  C    C/2  C//   C///  C////
w: 1/1  3/4  1/2  3/8   1/4  1/8  1/16  1/32  1/64 
```

![note durations](images/note_duration.png)

## Broken rhythm
In ABC notation, the symbols '>' and '<' represent specific rhythmic patterns. 
'>' signifies 'the previous note is dotted, the next note is halved,' while '<' 
indicates 'the previous note is halved, the next note is dotted.

Extending this logic, '>>' implies the first note is double dotted and the second 
is quartered, while '>>>' means the first note is triple dotted and the second note's 
length is divided by eight. The same pattern applies for '<<' and '<<<'. 

Note:
* It's important to note that using broken rhythm markers between notes of unequal lengths 
may yield undefined results and should be avoided.
* Also unclear is the result when a note is a part of broken rhythm on both its left and right sides.
* Broken rhythm markers without a left or right note are ignored.
* Grace notes are transparent for broken rhythm

Example:
```
X:0
L:1/4
T:Broken rhythm
M:C
K:C
>F>F A<A | G<<G B>>B | C>>>C D<<<D | [CEG]>E E<[EGB] |
[BDF]>[DFA] [BDF]<[DFA] | E>D [BDF]<D | E>{CEG2}D [BDF]<{CE>G}D | D> |
```
![broken rhythm](images/broken_rhythm.png)

## Rests
Rests in ABC notation can be represented using 'z' or 'x', and their length can be modified just like regular notes. 
'z' rests are visible in the sheet music, while 'x' rests are invisible and won't be shown when printed. 
For multi-measure rests, 'Z' (uppercase) is used followed by the number of measures, or 'X' for invisible multi-measure 
rests."

TODO:
* Remove the additional clef and meter symbols for multi measure rests

![rests](images/rests.png)

## User defined symbols
To provide a convenient shorthand for symbols without using the !symbol! for decorations, 
the letters H-W and h-w, as well as the symbol ~, can be designated using the U: field. 

Note:
* ABC2M21 is versatile and can handle multiple symbols and various types of symbols (not just decorations, 
but also fields in the inline form).
* The '.' symbol is a pre defined Symbol for '!staccato!' and is treated like a user-defined symbol, 
but cannot be overridden.

TODO:
* The ABC standard refers to the '~' symbol as an 'Irish roll', but I'm not quite sure what it represents.

Example:
```
X:1
T:User defined symbols
L:1/4
U:W = !trill!
U:U = !staccato!
U:V = !fermata!
K:C
WC UD VE .F
```

![user defined symbols](images/user_defined_symbols.png)

## Dynamics decoration
Dynamics in music refer to variations in loudness or intensity. 
They convey the volume or force with which a particular section of music is to be played. 
In ABC notation, dynamics are part of decorations, allowing notations like 'mf' for mezzo-forte (moderately loud) 
or 'p' for piano (soft).

```
X: 0
T: Dynamics
L: 1/4
K:C
!p!C !pp!C !ppp!C !pppp!C !f!C !ff!C !fff!C !ffff!C !mp!C !mf!C !sfz!C
```
![dynamics](images/dynamics.png)


## Decoration spanner
Crescendo, diminuendo, and trill decorations can be spanned across multiple notes using a spanner.

Notes:
* The trill spanner is a recent addition, but ABC2M21 is capable of grouping adjacent notes with trill decorations 
into a trill spanner. Isn't that cool?

```
X: 1
T:Decoration spanner
L:1/4
K:C
!<(!ABCD!<)! !>(!ABCD!>)! !trill(!ABCD!trill)!
```
![Decoration spanner](images/decoration_spanner.png)

## Expression decorations
ABC decorations encompass a variety of music21 concepts, including expressions.

Note:
* !pralltriller! is the same as !uppermordent!
* !lowermordent! is the same as !mordent!

```
X: 0
T: Expressions
L: 1/4
K:C
  !invertedfermata!C !trill!C !mordent!C !fermata!C !turn!C !arpeggio!'C !slide!C !uppermordent!C
w:!invertedfermata!  !trill!  !mordent!  !fermata!  !turn!  !arpeggio!   !slide!  !uppermordent! 
```
![Expressions](images/expressions.png)

## Articulation decorations
ABC decorations encompass a variety of music21 concepts, including articulations.

Note:
  * !marcato! is the same as !^!
  * !strongaccent! is the same as !^!
  * !straccent! is the same as !^!
  * !accent!  is the same as !>!
  * !emphasis! is the same as !>!
  * !plus! is the same as !+! (required for abc version 2.0)
  * !staccato! is also available as the shorthand symbol '.'
  * !+!, !snap!, !nail! are all Pizzicato variants and show no symbol in musescore

```
X: 0
T: Articulations
L: 1/4
K:C
  !staccato!C  | !>!C     | !downbow!C | !^!C | !breath!C |
w:!staccato!     !>!        !downbow!    !^!    !breath!
  !tenuto!C    | !upbow!C | !open!C    | !+!C | !snap!C   | !nail!C
w:!tenuto!       !upbow!    !open!       !+!    !snap!      !nail!
```
![Articulations](images/articulations.png)

## Repeat marker decorations
ABC decorations encompass a variety of music21 concepts, including repeat marker

```
X: 0
T: Repeat marker
L: 1/4
K:C
  !segno!C  | !coda!C | !fine!C | !D.S.!C | !D.S.alcoda!C | !D.S.alfine!C | !dacapo!C | !D.C.alcoda!C
w:!segno!     !coda!    !fine!    !D.S.!    !D.S.alcoda!    !D.S.alfine!    !dacapo!    !D.C.alcoda!
```
![Repeat marker](images/repeat_marker.png)

## Propagate accidentals directive
`I:propagate-accidentals not | octave | pitch`

* When set to 'not,' accidentals are exclusive to the individual notes they are attached to.
* When set to 'octave,' accidentals extend their influence to all notes of the same pitch within 
the same octave, spanning up to the end of the measure. 
* When set to 'pitch,' accidentals extend their influence to all notes of the same pitch 
across all octaves, reaching up to the end of the measure.
* The default value is 'pitch' for ABC version >= 2.0; otherwise, it is 'not'.

Note:
* MuseScore displays accidentals for the first note in all octaves, even if the Display Status is set to 'False'.

```
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
```
![propagate-accidentals directive](images/propagate_accidentals.png)


## Legacy chord and decoration
The ABC standard 2.0 initially introduced the '+...+' syntax to represent decorations instead 
of using '!...!'. However, this syntax was not widely adopted, and the latter '!' syntax became 
more common.

The '+' decoration syntax is now deprecated in favor of the '!' syntax.
Nevertheless, the '+...+' decoration syntax is still accessible using the 'I:decoration +' 
instruction and will detected by ABC2M21 if not disabled.

TODO:
* Show the power of legacy support
```
%abc-1.5 
X:1
T: legacy chord and decoration 
K:
+CEG+
I:decoration +  % Set '+' als decoration denotation symbol
+trill+C        % this is now a legal trill decoration
```
![legacy chord and decoration](images/legacy_chord_and_decoration.png)

# Show off

One of my favorit tunes from Franz Schubert

![Ave Marian (Schubert) (1)](images/ave_maria.png)
![Ave Marian (Schubert) (2)](images/ave_maria-2.png)
![Ave Marian (Schubert) (3)](images/ave_maria-3.png)


