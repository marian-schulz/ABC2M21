# ABC2M21
ABC2M21 implements an alternative translator/converter for tunes in 
[abc notation](https://abcnotation.com/wiki/abc:standard:v2.1) to 
[music21](https://github.com/cuthbertLab/music21) streams and objects.

## Setup
ABC2M21 only requires the [music21](https://github.com/cuthbertLab/music21) Python library and python version >= 3.10

*install music21:*

    pip3 install music21

or

    pip3 install requirements.txt

## Usage

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

## License
@TODO

