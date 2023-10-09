# ABC2M21
Converter for abc music notation to music21 streams and objects

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

      >>> from ABC2M21 import ABCTranslator
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
      >>> opus = ABCTranslator(abc_tune_book)
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
      >>> score = ABCTranslator(abc_tune)
      >>> score
      <music21.stream.Score X: 1>
      >>> score.metadata.title
      'single tune'
  
      Translate a single-voice ABC fragment to a stream.Part:
  
      >>> abc_fragment = '''
      ... ABCD | EFGA'''
      >>> isinstance(ABCTranslator(abc_fragment), stream.Part)
      True
  
      ABC Fragments with just some notes (and no bar lines) return a stream.Measure:
  
      >>> abc_fragment = '''
      ... ABCD'''
      >>> isinstance(ABCTranslator(abc_fragment), stream.Measure)
      True
  
      You may load your abc source from a file:
  
      >>> from pathlib import Path
      >>> tune_path = Path('tests/avemaria.abc')
      >>> score = ABCTranslator(tune_path)
      >>> score
      <music21.stream.Score X:1 (file='tests/avemaria.abc')>
      >>> score.metadata.title
      "Ave Maria (Ellen's Gesang III) - Page 1"
  
      However, music21 spanners are set in the Part object, so the following
      example, even if it consists of only a few notes, will return a Part object.
  
      >>> abc_fragment = '''
      ... !>(!ABCD!>)!'''
      >>> isinstance(ABCTranslator(abc_fragment), stream.Part)
      True


ABC Elements
============

The following section demonstrates, using images, how the translator creates music21 objects 
from abc elements. The abc fragments were converted into music21 streams and then used to generate images with Lilypond.

```
from ABC2M21.ABCParser import ABCTranslator 
from music21 import lily

abc_tune = """
X:1
T:Twinkle, Twinkle Little Star in C
M:C
K:C
L:1/4
vC C G G|A A G2|F F E E|D D C2|vG G F F|E E D2|
uG G F F|E E D2|vC C G G|A A G2|uF F E E|D D C2|]
"""

m21_stream = ABCTranslator(abc_tune)
lpc = lily.translate.LilypondConverter()
lpc.loadFromMusic21Object(m21_stream)
lpc.createPNG('abc_tune.png')
```
![twinkle](images/twinkle.png)

Pitches über verschiedene Oktaven
---------------------------------
```
X:1
T: abc pitches over serval octaves
L:1/8
K:C
C, D, E, F, G, A, B, x | C D E F G A B x | c d e f g a b x | c' d' e' f' g' a' b' x
w: C, D, E, F, G, A, B, | C D E F G A B | c d e f g a b | c' d' e' f' g' a' b' 
```
![abc pitches over serval octave](images/pitch_octaves.png)

Accidentals
-----------
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


Note duration
-------------

The note duration is relative to the `unit not length`.
![note durations](images/note_duration.png)
``