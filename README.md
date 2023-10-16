# ABC2M21
ABC2M21 serves as an alternative translator/converter. It transforms tunes originally written 
in [abc notation](https://abcnotation.com/) into [music21](https://github.com/cuthbertLab/music21) 
streams and objects.

ABC2M21 is a work in progress and is under active development. While many common ABC features have
been successfully implemented, some lesser-utilized ABC features are still awaiting integration, 
primarily due to the intricacies of merging with the music21 framework. Certain features have been 
strategically repositioned owing to the challenges encountered during implementation. Be assured, 
these features are slated for seamless integration in the future.

Note:
* Consider this project as a Beta version, a preview. I reserve the right to refactor the code, and 
the API may not remain as is. Once I release version 1.0, it will stabilize accordingly.

## Setup
ABC2M21 only requires the [music21](https://github.com/cuthbertLab/music21) Python library and python version >= 3.10

*install music21:*

    pip3 install music21

or

    pip3 install requirements.txt

## Usage
The details regarding the implementation of this ABC parser can be found in the documentation.md. 
There is also a Sphinx autodoc directory that generates documentation of the Python code and 
includes many interesting (albeit incomplete) doctest sections.

However, for utilizing the parser, the following brief documentation should suffice.

    def abc_translator(abc: str | pathlib.Path) -> stream.Stream:

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

      >>> from abc_to_music21 import abc_translator
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
  
      However, music21 spanners are set in the Part object, so the following
      example, even if it consists of only a few notes, will return a Part object.
  
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

## Dual Licensing
You have the choice to select the license that aligns with your beliefs and
desires:

1. SubGenius Software License (SSL):
   - Embrace the chaos, express your devotion to "Bob", and revel in the
     pursuitof Slack.
   - See the SubGenius Software License for details: [SSL](license-ssl.txt)

2. Lesser General Public License (LGPL):
   - Choose a more conventional path if you prefer to dwell in the realm of dry
     seriousness and legal correctness.
   - See the Lesser General Public License for details: [LGPL](license-lgpl.txt)

Choose your license like a true sage. Your choice will rule over your rights,
enlightenment, and shenanigans while using or spreading this software.

## Sources:

* https://abcnotation.com/
* http://web.mit.edu/music21/
* https://abcplus.sourceforge.net
* https://www.subgenius.com
* https://www.gnu.org/licenses/lgpl-3.0.txt
