
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
L:1/1
K:C
   ^C     _D   =E      ^^F          __G
w: sharp  flat natural double~sharp double~flat
```
![abc pitches over serval octave](images/accidentals.png)

## Note duration
The note duration is relative to the `unit not length`.

```
X:1
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

```
X: 
L:1/4
M:C
K:
z z2 z/2 z/4 z/4 | x x2 x/2 x/4 x/4 | Z | X | Z2 | X2 |
```

![rests](images/rests.png)


## Barlines

|       Symbol       | Meaning                              |
|:------------------:|--------------------------------------|
|         \|         | bar line                             |
|        \|]         | thin-thick double bar line           |
|        \|\|        | thick-thin double bar line           |
|       [\| 	      | thick-thin double bar line           | 
|        \|:         | start of repeated section            |
|        :\|         | end of repeated section              |
| :: , :\|: , :\|\|: | start & end of two repeated sections |
|      [1 , \|1      | First repeat                         |  
|      [2 , \|2      | Second repeat                        |  

Note:
  * ::| mean the end of a section that is to be repeated three times. (one repeat for each :)

Todo:
  * Variant endings
  * Dotted Barline '.|'
  * An invisible bar line may be notated by putting the bar line in brackets: [|]

```
X: 2
M:4/4
L:1/4
K:C
|: EGBc [| cega :: CEGA ::|[1 de BA | defg :|[2 de dB || abcd |]
```
![barlines](images/repeat_bar_lines.png)

## Ties
Ties in music notation are used to link the duration of two or more notes of the same pitch, 
creating a seamless, extended sound.

```
X: 1
M: 4/4
L: 1/4
K: C
C-C-[CEG-]G-|[CEG]-[EGB]-B z |
```
![ties](images/simple_ties.png)

## Slurs
Slurs in music notation are used to indicate the grouping or legato playing of notes, typically denoting a 
smooth transition between them.

TODO:
* Dotted slur `.(` & `.)`
* Slurs starting/ending on chord notes

```
X: 1
M: 4/4
L: 1/4
K: C
C(DE)F|ABC(D|AB)([CEG]C)
```
![slur](images/slur.png)

## Grace notes
Grace notes in abc are represented within curly braces: `{ ... }`. Acciaccaturas are indicated by adding a forward slash 
after the opening brace `{/ ... }` to differentiate them from appoggiaturas.  Acciaccatura and appoggiatura, differ in 
their visual representation on the score too. Acciaccatura is typically notated  with a slash through the stem, 
distinguishing it from appoggiatura.

Notes:
* Musescore3 ignores the 'slash' attribut in xml imports.
* The parser requires a main note for grace notes
* The tune 'Athol Brose' demonstrates gracing on the Highland pipes. (tunes section)

Todo:
* Chords for grace notes
* Broken rhythm for grace notes
* Tuplets for grace notes

```
X: 1
L: 1/2
K: C
"^Appoggiatura"{g}E {GdGe}F | "^Acciaccatura"{/g}E {/GdGe}F |
```
![Grace notes](images/simple_grace.png)

## Tuplets (Duplets, triplets, quadruplets...)
Tuplets are rhythmic groupings where a specific number of notes are played in the time typically occupied by a 
different number of notes, adding rhythmic variety and complexity to the music. 

Tuplets can be denoted using the syntax (p:q:r), indicating `fitting p notes into the duration of q for the succeeding 
r notes`.

Example ```(3:2:4 G2A2Bc```:
![tuplets](images/extended_tuplet.png)

Tuplets can be expressed using a simplified notation like `(2ab` for a duplet, `(3abc` for a triplet, or `(4abcd` for a 
quadruplet, extending up to (9. 

| Symbol | Meaning                  |
|:------:|--------------------------|
|  (2 	  | 2 notes in the time of 3 |
|  (3 	  | 3 notes in the time of 2 |
|  (4 	  | 4 notes in the time of 3 |
|  (5 	  | 5 notes in the time of n |
|  (6 	  | 6 notes in the time of 2 |
|  (7 	  | 7 notes in the time of n |
|  (8 	  | 8 notes in the time of 3 |
|  (9 	  | 9 notes in the time of n |

If the time signature is compound (6/8, 9/8, 12/8) then n is three, otherwise n is two.
```
X:2
M:4/4
K:E
(3.c=c^c (5ccc=cc (6ccccc=f (7Bcc^^c=cc^f
(3.c2=c2^c2 (3.c2=c2^c2
(6c/c/c/c/c/=f/ (6B/c/c/^^c/c/^f/ z4
```
![simple tuplets](images/tuplets.png)

## Decorations
In ABC notation, decorations refer to symbols or annotations that modify the way a note is played or interpreted. 
These include dynamic markings, articulations, expressions, and more. Decorations enhance the musical expression and 
provide additional information to the performer, guiding them on how to play the piece with specific nuances and 
style.

A number of shorthand decoration symbols are available: 

| Symbol  | Meaning                          |
|:-------:|----------------------------------|
|    .    | staccato mark                    |
|    ~    | Irish roll (not implemented yet) |
|    H    | fermata                          |
|    L    | accent or emphasis               |
|    M    | lowermordent                     |
|    O    | coda                             |
|    P    | uppermordent                     |
|    S    | segno                            |
|    T    | trill                            |
|    u    | up-bow                           |
|    v    | down-bow                         |

Most of the characters above `~HLMOPSTuv`  are just short-cuts for commonly used decorations and can even be redefined.

Example:
```
(3.a.b.c    % staccato triplet
vAuBvA      % bowing marks (for fiddlers)
```
![shorthand decorations](images/shorthand_decorations.png)

Additionally, symbols can be inserted using the syntax `!symbol!`, which will be elaborated upon in the subsequent 
subchapters.

Note:
* The abc standard version 2.0 used instead the syntax +symbol+ - this dialect of abc is implemented.

Todo:
* The shorthand symbol `~` is not implemented. I don't know the 'irish roll'.

### Dynamics decoration
Dynamics in music refer to variations in loudness or intensity. 
They convey the volume or force with which a particular section of music is to be played. 
In ABC notation, dynamics are part of decorations, allowing notations like 'mf' for mezzo-forte (moderately loud) 
or 'p' for piano (soft).

```
X: 0
L: 1/4
K:C
!p!C !pp!C !ppp!C !pppp!C !f!C !ff!C !fff!C !ffff!C !mp!C !mf!C !sfz!C
```
![dynamics](images/dynamics.png)


### Decoration spanner
Crescendo, diminuendo, and trill decorations can be spanned across multiple notes using a spanner.

```
X: 1
L:1/4
K:C
!<(!ABCD!<)! !>(!ABCD!>)! !trill(!ABCD!trill)!
```
![Decoration spanner](images/decoration_spanner.png)


### Expression decorations
ABC decorations encompass a variety of music21 concepts, including expressions.

Note:
* !pralltriller! is the same as !uppermordent!
* !lowermordent! is the same as !mordent!

```
X: 0
L: 1/4
K:C
  !invertedfermata!C !trill!C !mordent!C !fermata!C !turn!C !arpeggio!'C !slide!C !uppermordent!C
w:!invertedfermata!  !trill!  !mordent!  !fermata!  !turn!  !arpeggio!   !slide!  !uppermordent! 
```
![Expressions](images/expressions.png)

#### Trills
The trill spanner is a recent addition, but ABC2M21 is capable of grouping adjacent notes with trill decorations 
into a music21 trill extension spanner.
```
X: 
L: 1/4
M:C
K:C
C TE T[CEG] TF | TE CEG |
```
![auto trill spanner](images/auto_trill_spanner.png)


### Articulation decorations
ABC decorations encompass a variety of music21 concepts, including articulations.

Note:
  * !marcato! is the same as !^!
  * !strongaccent! is the same as !^!
  * !straccent! is the same as !^!
  * !accent!  is the same as !>!
  * !emphasis! is the same as !>!
  * !plus! is the same as !+! (required for abc version 2.0)
  * !staccato! is also available as the shorthand symbol '.'
  * !+!, !snap!, !nail! are all Pizzicato variants but are ignored by musescore

```
X: 0
L: 1/4
K:C
  !staccato!C  | !>!C     | !downbow!C | !^!C | !breath!C |
w:!staccato!     !>!        !downbow!    !^!    !breath!
  !tenuto!C    | !upbow!C | !open!C    | !+!C | !snap!C   | !nail!C
w:!tenuto!       !upbow!    !open!       !+!    !snap!      !nail!
```
![Articulations](images/articulations.png)

### Repeat marker decorations
ABC decorations encompass a variety of music21 concepts, including repeat marker

```
X: 0
L: 1/4
K:C
  !segno!C  | !coda!C | !fine!C | !D.S.!C | !D.S.alcoda!C | !D.S.alfine!C | !dacapo!C | !D.C.alcoda!C
w:!segno!     !coda!    !fine!    !D.S.!    !D.S.alcoda!    !D.S.alfine!    !dacapo!    !D.C.alcoda!
```
![Repeat marker](images/repeat_marker.png)

### Fingering decorations
ABC decorations encompass a variety of music21 concepts, including fingering marker

```
X:0
L:1/4
M:C
K:C
!1!E !2!G !3!E !4!F !5!G 
```
![Fingering marker](images/fingerings.png)

## Symbol lines
When a piece of music has many symbols, it can become hard to read.  You can use a 'symbol line.' 
This is a line that has only symbols, chord names, or annotations (!...!).  A symbol line starts 
with 's:' and then has a line of symbols. The symbols line up with the notes, following the same 
rules as lyrics. But, symbols in a symbol line can't line up with grace notes, rests, or spacers.

Todo:
* Not implemented yet

## Redefinable symbols
To provide a convenient shorthand for symbols without using the !symbol! for decorations, 
the letters H-W and h-w, as well as the symbol ~, can be designated using the U: field. 

Note:
* ABC2M21 is versatile and can handle multiple symbols and various types of symbols (not just decorations, 
but also fields in the inline form).
* The '.' symbol is a pre-defined Symbol for '!staccato!' and is treated like a user-defined symbol, 
but cannot be overridden.

TODO:
* The ABC standard refers to the '~' symbol as an 'Irish roll', but I'm not quite sure what it represents.

Example:
```
X:1
L:1/4
U:W = !trill!
U:U = !staccato!
U:V = !fermata!
K:C
WC UD VE .F
```
![user defined symbols](images/user_defined_symbols.png)

## Chords
Chords are written by enclosing notes within square brackets []. 
Typically, all notes in a chord should have the same duration, but if not, the chord's duration matches
that of the first note. You can add prefixes and postfixes to a chord just like you would to a single 
note, except for accidentals which should be placed on individual notes within the chord. 

When combining length modifiers inside and outside the chord, multiply them. For instance,
`[C2E2G2]3` is equivalent to `[CEG]6`.

```
( "^I" !f! [CEG]- > [CEG] "^IV" [F=AC]3/2"^V"[GBD]/  H[CEG]2 )
```
![chords](images/chord_example.png)

### Unison
If a chord includes two notes of the same pitch, it's referred to as a unison and is depicted with a single stem 
and two note-heads.

Example: 

`[DD]`
![unison](images/unison.png)

### Chord dialect
In early versions of the abc standard (1.2 to 1.5), chords were indicated with + symbols. This dialect is recognized 
by ABC2M21 under certain conditions.

Note:
* In abc version 2.0, this chord dialect is disabled due to its usage of + for decorations.
* You can enable the + decoration dialect by using the directive/instruction `I:decoration +`, which will disable 
this chord dialect.
* The current ABC standard, version 2.1, recommends disabling the chord dialect even in version 2.1 and opting for a 
strict interpretation. However, ABC2M21 does not currently follow this recommendation.

Example:
```+CEG+```

![chord dialect](images/chord_dialect.png)


## Chord symbols
Chord symbols, like chords or bass notes, can be positioned below (or above) the melody line using double-quotation 
marks placed to the left of the note they correspond to

The chord is formatted as `<note><accidental><type><bass>`, where `<note>` can range from A-G, the optional 
`<accidental>` can be b or #, and the optional `<type>` consists of one or more characters of:
```
m or min        minor
maj             major
dim             diminished
aug or +        augmented
sus             suspended
7, 9 ...        7th, 9th, etc.
```

Todo:
* Alternate chords can be indicated for printing purposes (but not for playback) by enclosing them in parentheses inside 
the double-quotation marks after the regular chord, e.g., "G(Em)". 
* Software should also be able to recognise and handle appropriately the unicode versions of flat, natural and 
sharp symbols (♭, ♮, ♯) 

```
"A"A2 "Am"A2 "A7"A2 "Amaj7"A2 "A+"A2
```

![chord symbols](images/chord_symbols.png)

## Propagate accidentals
`I:propagate-accidentals not | octave | pitch`

or

`%% propagate-accidentals not | octave | pitch`

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
T:Propagate-accidentals
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

## Tunes
Here are some example of imported abc tunes.

### Atholl Brose
The tune 'Atholl Brose' demonstrates complex gracing on the Highland pipes.

![Atholl Brose](images/atholl_brose.png)

### Ave Maria (Franz Schubert)
One of my favorit tunes from Franz Schubert

![Ave Marian (Schubert) (1)](images/ave_maria.png)
![Ave Marian (Schubert) (2)](images/ave_maria-2.png)
![Ave Marian (Schubert) (3)](images/ave_maria-3.png)


