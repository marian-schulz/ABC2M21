# ABC2M21
ABC2M21 serves as an implementation acting as an alternative translator/converter. It transforms tunes originally 
written in abc notation into music21 streams and objects.

ABC2M21 is a work in progress and is under active development. While many common ABC features have been successfully 
implemented, some lesser-utilized ABC features are still awaiting integration, primarily due to the intricacies of 
merging with the music21 framework. Certain features have been strategically repositioned owing to the challenges 
encountered during implementation. Be assured, these features are slated for seamless integration in the future.

* A special thank you to Michael Scott Cuthbert, the creator of music21.
* Thanks are also due to the MuseScore teams for their valuable open-source contributions.
* I express my gratitude to all the composers and transcribers who have enriched us with tens of thousands of ABC tunes.
* A special note of appreciation is extended to ChatGPT for its invaluable assistance in translating and proofreading 
the English sentences.

## About this Document

This document provides an overview of **ABC2M21**'s implementation, adhering to the 
[ABC standard 2.1](https://abcnotation.com/wiki/abc:standard:v2.1) with inclusive support for older versions. Several 
chapters are sourced directly from the [ABC standard 2.1](https://abcnotation.com/wiki/abc:standard:v2.1) description.

The following chapters showcases the translation process using images, depicting how the translator transforms ABC 
elements into music21 objects. The ABC tunes and fragments are initially converted into music21 streams and then used 
to generate visuals with the aid of [MuseScore](https://musescore.org), an open-source music notation program. 
MuseScore features a WYSIWYG editor, facilitating note input and providing playback functionalities.

Example:

    from ABC2M21 import abc_translator 
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
    
    m21_stream = abc_translator(abc_tune)
    xmlconv = converter.subConverters.ConverterMusicXML()
    xmlconv.write(m21_stream, fmt='musicxml', fp="myfile.png", subformats=['png'])

![twinkle](images/twinkle.png)

## Setup
ABC2M21 only requires the [music21](https://github.com/cuthbertLab/music21) Python library and python version >= 3.10

Note: 
* ABC2M21 is developed and tested with music21-9.1. Older versions might work, or they might not.

**install music21:**

    pip3 install music21

or

    pip3 install requirements.txt


## Usage
To use ABC2M21, usually, only the following method is required.
        
    def ABCTranslator(abc: str | pathlib.Path) -> stream.Stream:
        
        Translate ABC notation to a music21 stream.
        
        This function translates ABC notation, which can be a tune book,
        a single tune, or an incomplete ABC fragment, into a music21 stream object.
        The resulting object can be a stream.Opus, a single stream.Score, a stream.Part,
        or just a stream.Measure.
        
        Parameters:
        - abc: The input ABC notation as a string or a path to an ABC file.
        
        Returns: A music21 stream object representing the parsed ABC content.
        
        Examples:
        
        Translate a tune book from ABC notation to an opus:
        
        >>> from ABC2M21 import abc_translator
        >>> abc_tune_book = '''
        ... %abc-2.1
        ... X:1
        ... T:tune 1
        ... K:
        ... EGB
        ... X: 2
        ... T:tune 2
        ... K:
        ... CEG'''
        >>> opus = abc_translator(abc_tune_book)
        >>> opus
        <music21.stream.Opus string>
        >>> len(opus.scores)
        2
        
        Translate a single tune from ABC notation to stream.Score:
        
        >>> abc_tune = '''
        ... X: 1
        ... T:single tune
        ... K: G
        ... CEG'''
        >>> score = abc_translator(abc_tune)
        >>> score
        <music21.stream.Score X: 1>
        >>> score.metadata.title
        'single tune'
        
        Translate a single-voice ABC fragment to a stream.Part:
        
        >>> abc_fragment = '''
        ... ABCD | EFGA'''
        >>> isinstance(abc_translator(abc_fragment), stream.Part)
        True
        
        ABC Fragments with just some notes (and no bar lines) return a stream.Measure:
        
        >>> abc_fragment = '''
        ... ABCD'''
        >>> isinstance(abc_translator(abc_fragment), stream.Measure)
        True
        
        You may load your abc source from a file:
        
        >>> from pathlib import Path
        >>> tune_path = Path('tests/avemaria.abc')
        >>> score = abc_translator(tune_path)
        >>> score
        <music21.stream.Score X:1 (file='tests/avemaria.abc')>
        >>> score.metadata.title
        "Ave Maria (Ellen's Gesang III) - Page 1"
        
        However, music21 spanners are set in the part stream, so the following
        example, even if it consists of only a few notes, will return a part object.
        
        >>> abc_fragment = '''
        ... !>(!ABCD!>)!'''
        >>> isinstance(abc_translator(abc_fragment), stream.Part)
        True

## Configuration
Sometimes, it's necessary to disable or configure certain features of ABC2M21.

For instance, the images in this document were created using MuseScore3. Unfortunately, MuseScore's musicxml 
import is not flawless. In such cases, if possible, ABC2M21 provides a workaround.

```
from ABC2M21 import ABC2M21_CONFIG

# Convert complex meters into an equivalent of a simple meter
ABC2M21_CONFIG['simplifiedComplexMeter'] = True
```

# ABC Dokumentation

## ABC fields

### Unit note length
The **Unit Note Length** sets the fundamental duration of an ABC note. 

If no `L:` field is provided, the default unit note length is determined based on the length of the 
meter's bar duration:

* If the length is less than 0.75, the default unit note length is a sixteenth note.
* If the length is 0.75 or greater, it defaults to an eighth note.
* If no meter is defined, it also defaults to an eighth note

Example:
```abc:unit_note_length
[L:1/1] C [L:1/2] C [L:1/4] C [L:1/8] C [L:1/16] C [L:1/32] C
```
![unit note length](images/unit_note_length.png)

### Meter
The `M:` field in ABC notation indicates the **meter** of the music. Common meters like 6/8 or 4/4 are 
represented as `M:6/8` or `M:4/4`. Additionally, `M:C` represents common time (4/4), and `M:C|` represents 
cut time (2/2). Using `M:none` omits specifying the meter, indicating free meter.

Complex meters can be defined, such as `M:(2+3+2)/8`. However, certain applications like Musescore may 
struggle to handle complex meters. To address this, you can ask **ABC2M21** to simplify complex meter by 
setting the `simplifiedComplexMeter` property in the **ABC2M21 Configuration**. 
```
ABC2M21_CONFIG['simplifiedComplexMeter'] = True
```

Example:
```abc:meter
X:0
L:1/8
M:6/8
K:C
CDEFGA|[M:4/4]CDEFGABc|[M:C]CDEFGABc|[M:C|]CDEFGABc|[M:(2+3+2)/8]CDEFGAB
```
![Meter](images/meter.png)

### Tempo
The `Q:` field in ABC notation sets the tempo as beats per minute, for instance, `Q:1/2=120` 
means 120 half-note beats per minute. The tempo definition can include an optional text string 
in quotes before or after it. 
Additionally, there are deprecated older syntax variants specifying how many unit note lengths 
to play per minute, for instance `Q:120` or `Q:C=120` means play 120 unit note-lengths per minute.

Example:
```abc:tempo
L:1/1
[Q:1/2=120]E | [Q:"Allegro" 1/4=120]F | [Q: 3/8=50 "Slowly"]G | [Q:"Andante"]A | [Q:120]B | 
```
![Tempo](images/tempo.png)

### Part
The P: field in the tune header is used to define the sequence in which the different parts of a tune 
are played, such as P:ABABCDCD. Inside the tune body, you can mark each part using P:A or P:B. 

In the tune header, you can specify repeating a part by appending a number, like P:A3 meaning repeat 
part A three times, similar to P:AAA. Sequences can be made to repeat using parentheses, for example, 
P:(AB)3 is equivalent to P:ABABAB. 

Nested parentheses are allowed, and dots within the P: field enhance readability, although they are 
ignored by computer programs, like P:((AB)3.(CD)3)2.

Note:
 * In abc a **part** refers to a section of the tune, not a voice in multi-voice music.
```abc:part
X:1
L:1
P:((AB)2.C2D)2
M:C
I:linebreak $
K:C
[P:A]A |
[P:B]B |
[P:C]C |
[P:D]D |$
```
![part](images/part.png)

### Titel, Composer, Area, Origin, Transcription

Historically, the A: field has been used to contain area information. However this field 
is now deprecated and it is recommended that such information be included in the O: field. 

Note:
* The "Area" (A:) field is treated like the "Origin" (O:) field.
```
>>> abc_fragment = '''
... T:Ave Maria
... C:Johann Sebastian Bach
... C:Charles Gounod
... O:Germany
... A:France
... Z:John Smith, <j.s@mail.com>
... Z:abc-transcription John Smith, <j.s@mail.com>, 1st Jan 2010
... Z:abc-edited-by Fred Bloggs, <f.b@mail.com>, 31st Dec 2010
... Z:abc-copyright &copy; John Smith
... '''
>>> score = abc_translator(abc_fragment)
>>> score.metadata.composer
'Johann Sebastian Bach and Charles Gounod'
>>> score.metadata.localeOfComposition
'Germany, France'
>>> score.metadata.contributors
(<music21.metadata.primitives.Contributor composer:Johann Sebastian Bach>,
 <music21.metadata.primitives.Contributor composer:Charles Gounod>,
 <music21.metadata.primitives.Contributor abc-transcription:John Smith, <j.s@mail.com>>,
 <music21.metadata.primitives.Contributor abc-transcription : John Smith, <j.s@mail.com>, 1st Jan 2010>,
 <music21.metadata.primitives.Contributor abc-edited-by : Fred Bloggs, <f.b@mail.com>, 31st Dec 2010>,
 <music21.metadata.primitives.Contributor abc-copyright : © John Smith)
```

### Clefs and transposition
Clef and transposition information may be provided in the `K:` key and `V:' voice fields. 
The general syntax is: 

```
[clef=]<clef name>[<line number>][+8 | -8] [middle=<pitch>] [transpose=<semitones>] [octave=<number>] [stafflines=<lines>]
```

### transposition

```abc:octave_transposition
X:1
L:1/2
M:C
K:C
[V:A]E [V:A octave=-1]e |
[V:B bass octave=-2]E [V:B octave=-3]e |
```
![abc octave transposition](images/octave_transposition.png)

## ABC music code

### Pitches Across Various Octaves

Example:
```abc:pitches
X:1
L:1/1
K:C
   C, D, E, F, G, A, B, C D E F G A B c d e f g a b c' d' e' f' g' a' b' |
w: C, D, E, F, G, A, B, C D E F G A B c d e f g a b c' d' e' f' g' a' b' 
```
![abc pitches](images/pitches.png)

### Accidentals
In ABC notation, accidentals are written before the note using symbols such as `^` (sharp), `=` (natural), and `_` (flat). 
Double sharps and flats are denoted by `^^` and `__` respectively.

Note:
* The decoration !courtesy! is a feature defined in the ABC 2.2 draft.

```abc:accidentals
L:1/1
"_sharp"^C "_flat"_D  "_natural"=E  "_double sharp"^^F  "_double flat"__G "_!courtesy!"!courtesy!^C
```
![abc accidentals](images/accidentals.png)

### Note duration
The note duration is relative to the `unit not length`.

```abc:durations
L:1/4
C4   C3   C2   C3/2  C    C/2  C//   C///  C////
```

![abc durations](images/durations.png)

### Broken rhythm
In ABC notation, the symbols `>` and `<` represent specific rhythmic patterns. 
`>` signifies 'the previous note is dotted, the next note is halved, while `<` 
indicates the previous note is halved, the next note is dotted.

Extending this logic, `>>` implies the first note is double dotted and the second 
is quartered, while `>>>` means the first note is triple dotted and the second note's 
length is divided by eight. The same pattern applies for `<<` and `<<<`. 

Note:
* It's important to note that using broken rhythm markers between notes of unequal lengths 
may yield undefined results and should be avoided.
* Also unclear is the result when a note is a part of broken rhythm on both its left and right sides.
* Broken rhythm markers without a left or right note are ignored.
* Grace notes are transparent for broken rhythm

Example:
```abc:broken_rhythm
L:1/4
>F>F A<A | G<<G B>>B | C>>>C D<<<D | [CEG]>E E<[EGB] |
[BDF]>[DFA] [BDF]<[DFA] | E>D [BDF]<D | E>{CEG2}D [BDF]<{CE>G}D | D> |
```
![broken rhythm](images/broken_rhythm.png)

### Rests
Rests in ABC notation can be represented using `z` or `x`, and their length can be modified just like regular notes. 
`z` rests are visible in the sheet music, while `x` rests are invisible and won't be shown when printed. 
For multi-measure rests, `Z` (uppercase) is used followed by the number of measures, or `X` for invisible multi-measure 
rests."

TODO:
* Remove the additional clef and meter symbols for multi measure rests

```abc:rests
L:1/4
M:C
z z2 z/2 z/4 z/4 | x x2 x/2 x/4 x/4 | Z | X | Z2 | X2 |
```
![rests](images/rests.png)

### Bar lines

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
  * Dotted bar line '.|'
  * An invisible bar line may be notated by putting the bar line in brackets: [|]

```abc:bar_lines
X:1
M:4/4
L:1/4
K:C
|: EGBc [| cega :: CEGA ::|[1 de BA | defg :|[2 de dB || abcd |]
```
![barlines](images/bar_lines.png)

### Ties
Ties in music notation are used to link the duration of two or more notes of the same pitch, 
creating a seamless, extended sound.

Todo:
* Dotted ties `.-`

```abc:ties
X: 1
M: 4/4
L: 1/4
K: C
C-C-[CEG-]G-|[CEG]-[EGB]-B z |
```
![ties](images/ties.png)

### Slurs
Slurs in music notation are used to indicate the grouping or legato playing of notes, typically denoting a 
smooth transition between them.

Note:
* MuseScore didn't recognize the dotted slur attribute.

Todo:
* Slurs starting/ending on chord notes

```abc:slur
M: 4/4
L: 1/4
C(DE)F|ABC(D|AB)([CEG]C)
```
![slur](images/slur.png)

### Grace notes
Grace notes in abc are represented within curly braces: `{ ... }`. Acciaccaturas are indicated by adding a forward slash 
after the opening brace `{/ ... }` to differentiate them from appoggiaturas.  Acciaccatura and appoggiatura, differ in 
their visual representation on the score too. Acciaccatura is typically notated  with a slash through the stem, 
distinguishing it from appoggiatura.

Notes:
* Musescore3 ignores the 'slash' attribut in xml imports.
* The parser requires a main note for grace notes

Todo:
* Chords for grace notes
* Broken rhythm for grace notes
* Tuplets for grace notes

```abc:grace
X: 1
L: 1/2
K: C
"^Appoggiatura"{g}E {GdGe}F | "^Acciaccatura"{/g}E {/GdGe}F |
```
![Grace notes](images/grace.png)

### Tuplets (Duplets, triplets, quadruplets...)
Tuplets are rhythmic groupings where a specific number of notes are played in the time typically occupied by a 
different number of notes, adding rhythmic variety and complexity to the music. 

Tuplets can be denoted using the syntax (p:q:r), indicating `fitting p notes into the duration of q for the succeeding 
r notes`.

Example:
```abc:tuplet
(3:2:4 G2A2Bc
```
![tuplets](images/tuplet.png)

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
```abc:tuplets
X:2
M:4/4
K:E
(3.c=c^c (5ccc=cc (6ccccc=f (7Bcc^^c=cc^f
(3.c2=c2^c2 (3.c2=c2^c2
(6c/c/c/c/c/=f/ (6B/c/c/^^c/c/^f/ z4
```
![tuplets](images/tuplets.png)

### Decorations
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

Most of the characters above `~HLMOPSTuv` are just short-cuts for commonly used decorations and can even be redefined.

Example:
```abc:shorthand_decorations
[L:1/4] (3.a.b.c vAuBvA T[DFA]
```
![shorthand decorations](images/shorthand_decorations.png)

Additionally, symbols can be inserted using the syntax `!symbol!`, which will be elaborated upon in the subsequent 
subchapters.

Note:
* The abc standard version 2.0 used instead the syntax +symbol+ - this dialect of abc is implemented.

Todo:
* The shorthand symbol `~` is not implemented. I don't know the 'irish roll'.

#### Dynamics decoration
Dynamics in music refer to variations in loudness or intensity. 
They convey the volume or force with which a particular section of music is to be played. 
In ABC notation, dynamics are part of decorations, allowing notations like 'mf' for mezzo-forte (moderately loud) 
or 'p' for piano (soft).



```abc:dynamics
[L:1/4] !p!C !pp!C !ppp!C !pppp!C !f!C !ff!C !fff!C !ffff!C !mp!C !mf!C !sfz!C
```
![dynamics](images/dynamics.png)


#### Decoration spanner
Crescendo, diminuendo, and trill decorations can be spanned across multiple notes using a spanner.

```abc:decoration_spanner
X: 1
L:1/4
K:C
!<(!ABCD!<)! !>(!ABCD!>)! !trill(!ABCD!trill)!
```
![Decoration spanner](images/decoration_spanner.png)

The trill spanner is a recent addition, but ABC2M21 is capable of grouping adjacent notes with trill decorations 
into a music21 trill extension spanner.

```abc:auto_trill_spanner
X:
L:1/4
M:C
K:C
C TE T[CEG] TF | TE CEG |
```
![auto trill spanner](images/auto_trill_spanner.png)

#### Expression decorations
ABC decorations encompass a variety of music21 concepts, including expressions.

Note:
* !pralltriller! is the same as !uppermordent!
* !lowermordent! is the same as !mordent!

```abc:expressions
L:1/4
K:C
  !invertedfermata!C !trill!C !mordent!C !fermata!C !turn!C !arpeggio!'C !slide!C !uppermordent!C
w:!invertedfermata!  !trill!  !mordent!  !fermata!  !turn!  !arpeggio!   !slide!  !uppermordent! 
```
![Expressions](images/expressions.png)


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

```abc:articulations
L:1/4
K:C
!staccato!C  !>!C       !downbow!C !^!C |
!tenuto!C    !upbow!C   !open!C    !+!C |
!breath!C    !snap!C    !nail!C    !doit!C |
!thumb!C     !cesura!C
```
![Articulations](images/articulations.png)

### Repeat marker decorations
ABC decorations encompass a variety of music21 concepts, including repeat marker

```abc:repeat_marker
L:1/4
K:C
  !segno!C  | !coda!C | !fine!C | !D.S.!C | !D.S.alcoda!C | !D.S.alfine!C | !dacapo!C | !D.C.alcoda!C |
w:!segno!     !coda!    !fine!    !D.S.!    !D.S.alcoda!    !D.S.alfine!    !dacapo!    !D.C.alcoda!
```
![Repeat marker](images/repeat_marker.png)

### Fingering decorations
ABC decorations encompass a variety of music21 concepts, including fingering marker

```abc:fingerings
!1!E !2!G !3!E !4!F !5!G 
```
![Fingering marker](images/fingerings.png)

### Decoration dialect
The ABC standard 2.0 initially introduced the `+...+` syntax to represent decorations instead 
of using `!...!`. However, this syntax was not widely adopted, and the latter `!...!` syntax became 
more common.

The `+...+` decoration syntax is now deprecated in favor of the `!...!` syntax.
Nevertheless, the `+...+` decoration syntax is still accessible using the `I:decoration +` 
instruction or using the abc version 2.0.

Note:
* By activating the `+...+` decoration dialect ABC2M21 will deactivate the `+...+` chord dialect.
* Activating the `+...+` decoration dialect for tunes using the `+...+` chord dialect may lead to undefined results

```abc:decoration_dialect
%abc-1.5 
K:
+CEG+           % ABC2M21 will detect this as chord
I:decoration +  % Set '+' als decoration denotation symbol
+trill+C        % this is now a legal trill decoration
```
![abc decoration dialect](images/decoration_dialect.png)


## Symbol lines
When a piece of music has many symbols, it can become hard to read.  You can use a 'symbol line.' 
This is a line that has only symbols, chord names, or annotations (!...!).  A symbol line starts 
with `s:` and then has a line of symbols. The symbols line up with the notes, following the same 
rules as lyrics. But, symbols in a symbol line can't line up with grace notes, rests, or spacers.

Todo:
* Not implemented yet

## Redefinable symbols
To provide a convenient shorthand for symbols without using the !symbol! for decorations, 
the letters H-W and h-w, as well as the symbol ~, can be designated using the U: field. 

Note:
* ABC2M21 is versatile and can handle multiple symbols and various types of symbols (not just decorations, 
but also fields in the inline form).
* The `.` symbol is a pre-defined Symbol for `!staccato!` and is treated like a user-defined symbol, 
but cannot be overridden.

TODO:
* The ABC standard refers to the `~` symbol as an 'Irish roll', but I'm not quite sure what it represents.

Example:
```abc:user_defined_symbols
X:1
L:1/4
U:W = !trill!
U:U = !staccato!
U:V = !fermata!
K:C
WC UD VE .F
```
![abc user defined symbols](images/user_defined_symbols.png)

## Chords
Chords are written by enclosing notes within square brackets []. 
Typically, all notes in a chord should have the same duration, but if not, the chord's duration matches
that of the first note. You can add prefixes and postfixes to a chord just like you would to a single 
note, except for accidentals which should be placed on individual notes within the chord. 

When combining length modifiers inside and outside the chord, multiply them. For instance,
`[C2E2G2]3` is equivalent to `[CEG]6`.

```abc:chords
( "^I" !f! [CEG]- > [CEG] "^IV" [F=AC]3/2"^V"[GBD]/  H[CEG]2 )
```
![chords](images/chords.png)

### Unison
If a chord includes two notes of the same pitch, it's referred to as a unison and is depicted with a single stem 
and two note-heads.

Example: 

```abc:unison
[DD]
```
![abc unison](images/unison.png)

### Chord dialect
In early versions of the abc standard (1.2 to 1.5), chords were indicated with + symbols. This dialect is recognized 
by ABC2M21 under certain conditions.

Note:
* In abc version 2.0, this chord dialect is disabled due to its usage of `+` for decorations.
* You can enable the `+...+` decoration dialect by using the directive/instruction `I:decoration +`, which will disable 
this chord dialect.
* Using the `+...+` chord dialect for tunes with `+...+` chord dialect (abc-2.0) may lead to undefined results
* The current ABC standard, version 2.1, recommends disabling the chord dialect even in version 2.1 and opting for a 
strict interpretation. However, ABC2M21 does not currently follow this recommendation.

Example:
```abc:chord_dialect
+CEG+2
```

![abc chord dialect](images/chord_dialect.png)


### Chord symbols
Chord symbols can be positioned below (or above) the melody line using double-quotation marks placed to the left 
of the note they correspond to.

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

```abc:chord_symbols
"A"A2 "Am"A2 "A7"A2 "Amaj7"A2 "A+"A2
```

![abc chord symbols](images/chord_symbols.png)

### Annotations
Text annotations are placed in quotation marks and provide additional textual information related to the melody.
The first character of the annotation source string indicates the placement of the annotation relative to the next note.

| Symbol | Placement Explanation              |
|:------:|------------------------------------|
|   `^`  | Above the note                     |
|   `_`  | Below the note                     |
|   `<`  | Left of the note                   |
|   `>`  | Right of the note                  |
|   `@`  | Indicate a free placement position |

```abc:annotations
"^Above"C "_Below"D "<Left"E ">Right"F "@Free placement"G 
```
![Annotations](images/annotations.png)

## Lyrics
The `w:` field in the tune body allows for the addition of **lyrics** that match syllable by syllable with the notes 
in the current voice that precede them.

| Symbol | Meaning                                                       |
|:------:|---------------------------------------------------------------|
|  `-`   | Break between syllables within a word                         |
|  `_`   | Previous syllable is held for an extra note                   |
|  `*`   | One note is skipped (equivalent to a blank syllable)          |
|  `~`   | Appears as a space; aligns multiple words under one note      |
|  `\-`  | appears as a hyphen; aligns multiple syllables under one note |
|  `\|`  | advances to the next bar                                      |

Todo:

* The W: information field (uppercase W) can be used for lyrics to be printed separately below the tune.
* add support for abc 2.0 lyric dialect.
* Some more testing and tuning is required.

Example: The following two examples are equivalent. 
```abc:lyrics_1
I:linebreak $
C D E F|
w: doh re mi fa
G A B c|
w: sol la ti doh
```
![Lyrics example 1](images/lyrics_1.png)

In the second example, a new feature (introduced in abc 2.1) allows **lyrics** to be placed anywhere in the tune, not 
just immediately after the corresponding notes. This provides flexibility to position lyrics at the end of the tune if 
needed.
```abc:lyrics_2
C D E F|
G A B c|
w: doh re mi fa sol la ti doh
```
![Lyrics example 2](images/lyrics_2.png)

However, the extension of the alignment rules is not fully backwards compatible with abc 2.0 

When there are more notes than lyrics, any extra notes have no associated **lyrics** (blank syllables). Therefore, the 
presence of a `w:` field links all preceding notes to a syllable, whether it's a real syllable or a blank one.
For instance, in the next example, the empty `w:` field indicates that the four G notes do not have any **lyrics** 
associated with them.
```abc:lyrics_3
C D E F|
w: doh re mi fa
G G G G|
w:
F E F C|
w: fa mi re doh
```
![Lyrics example 3](images/lyrics_3.png)

```abc:lyrics_4
gf|e2dc B2A2|B2G2 E2D2|
.G2.G2 GABc|d4 B2
w: Sa-ys my au-l' wan to your aul' wan,
+: Will~ye come to the Wa-x-ies dar-gle?
```
![Lyrics example 4](images/lyrics_4.png)


### Verses
A music line can be accompanied by multiple consecutive `w:` fields, each representing different verses. The first 
`w:` field corresponds to the initial rendition of that part, followed by the second and so forth.

Examples: The subsequent examples, both equivalent, demonstrate the presence of two verses.
```abc:verses_1
CDEF FEDC|
w: these are the lyr-ics for verse one
w: these are the lyr-ics for verse two
```
![abc verses example 1](images/verses_1.png)

```abc:verses_2
CDEF FEDC|
w: these are the lyr-ics
+:  for verse one
w: these are the lyr-ics
+:  for verse two  
```
![abc verses example 2](images/verses_2.png)

### Numbering
VOLATILE: The following syntax may be extended to include non-numeric "numbering".
If the first word of a w: line starts with a digit, this is interpreted as numbering of a stanza. Typesetting programs 
should align the corresponding note with the first letter that occurs. This can be used in conjunction with the ~ symbol 
mentioned in the table above to create a space between the digit and the first letter.
Example: In the following, the 1.~Three is treated as a single word with a space created by the ~, but the fact that 
the w: line starts with a number means that the first note of the corresponding music line is aligned to Three.

Todo:
 * not implemented yet

```
   w: 1.~Three blind mice
```

## Typesetting

### score line-break
The primary method for typesetting score line breaks (printed in the score) involves using code line breaks. 
Typically, one line of music code in the tune body corresponds to one line of printed music. To prevent a 
score line break due to a end of line in the music code, a backslash (\) can be used. ABC2M21 recognizes the 
backslash both at the end of a line and before a comment

Note:
* Line breaks and line continuation are among the most intricate small features of ABC, 
as there are numerous divergent approaches to them across different ABC versions. Addressing 
all these variations requires careful consideration of many subtle details by the translator.
* It is not possible with music21 to create a score linebreak in the mittle of a measure.

```abc:suppress_score_linebreak
abc cba|\ % Backslash before the comment
abc cba| % Backslash at the end of the line \
abc cba|
```
![suppress score linebreak](images/suppress_score_linebreak.png)

It is possible to continue a music code line over abc fields, comments and directives.
```abc:music_code_line_continue
abc cab|\
%%setbarnb 10
M:9/8
%comment
abc cba abc|
```
![line continue over comments](images/music_code_line_continue.png)

```abc:score_line_break_symbols
abc cba|$abc cba|!abc cba|
```
![score linebreak symbols](images/score_line_break_symbols.png)


#### Instruction 'linebreak'
Over time, in response to changes in ABC standards and extensions introduced by popular typesetting programs, 
ABC standard 2.1 has evolved. One significant addition is a new line-breaking instruction `I:linebreak`, providing 
control over score line breaks. This instruction accommodates different line-breaking preferences and offers four 
distinct values, allowing users to tailor line breaks according to their specific needs.

* `I:linebreak $`: Indicates that the $ symbol is used in the tune body to typeset a score line-break.
* `I:linebreak !`: Indicates that the ! symbol is used in the tune body to typeset a score line-break.
* `I:linebreak <EOL>`: indicates that the newline will typeset a score line-break.
* `I:linebreak <none>`: indicates that all line-breaking is to be carried out automatically and any code line-breaks 
are ignored for typesetting purposes.

The values <EOL>, $ and ! may also be combined so that more than one symbol can indicate a score line-break.
ABC2M21 starts per default with this line-break settings:
```
I:linebreak <EOL> $ !
```
Note:
* Contrary to the recommendations of the ABC standard, `linebreak !` can be used simultaneously with `!...!` for 
decorations. This implementation detail may change if issues arise in the interpretation or if a strict interpretation 
is required.
* ABC2M21 will also evaluate `I:linebreak` instructions in the tune body even it is not recommended.


## Accidental directives

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

```abc:propagate_accidentals
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

