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

The license for this project has not yet been determined. My head feels like it's about to fall off when I try to
understand some of the usual software licenses. So, instead of coming up with boring, legally binding formulations, 
I've written my own license that's worth reading.


                         SUBGENIUS SOFTWARE LICENSE
                       Version 1, Bureaucracy, 3189 YOLD
        
                 DO WHAT THE F*CK YOU WANT TO, BUT PRAISE "BOB"!
    
    
    Preamble:
    
    This Divine Software License ("License") is a revelation and was transcribed
    under the influence of habafropzipulops by Reverend Hoax Theokratis. By
    obtaining, using, distributing, or contemplating this Sacred Code, you are
    granted the divine privilege to embrace the eternal pursuit of Slack and "Bob".
    
    License:

    0. Definitions:
    
    The term "Sacred Code" refers to the Techno-magic spells of this software and
    any variations, modifications, or derivatives thereof. The "Sacred Code" is
    written in an arcane language that computers sometimes understand.
    
    The term "Slack" shall be defined as the eternal pursuit of all SubGenii in
    their endeavors, be it coding, frolicking, or contemplating the mysteries of
    the cosmos while sipping coffee.
    
    The term "The Conspiracy" refers to the nefarious forces that seek to stifle
    Slack and hinder the pursuit of true enlightenment and laughter.
    
    The term "Bob" refers to J.R. "Bob" Dobbs, the living avatar of Slack and
    the omniscient deity embodying the SubGenius pursuit of Slackness and eternal
    mirth.
    
    1. Disclaimer

    This software is provided 'as-is,' without any express or implied warranty, 
    including the warranty that it serves any particular purpose. 

    In no event will the authors or the Church of the SubGenius be held liable for
    damages or losses of any kind arising from the use of this software. This 
    includes but is not limited to:

    - Unintentional time travel resulting in prehistoric programming bugs
    - Spontaneous generation of virtual black holes within your codebase
    - Accidental summoning of rogue AI overlords
    - Transmutation of computer peripherals into rubber ducks

    In case of an apocalypse, alien invasions, the end of your favorite Netflix 
    series, or other unforeseen events caused by the use of this software, you're
    on your own.

    2. Preach and Share the Word:
    
    You are allowed to replicate and distribute the "Sacred Code" in all its
    glorious manifestations, as long as you do not succumb to the Bland Normie
    Syndrome. And, in the spirit of chaos, you shall present it in vivid colors
    and glitters on each copy, adorned with a joyful celebration of the divinity of
    "Bob"!
    
    3. Schism:
    
    You are bestowed with the divine privilege to modify, distribute, and bask
    in the glory of this Sacred Code of Slack. You are encouraged to fork, clone,
    or merge this Sacred Code, for Slack desires to be fluid and ever-evolving. Do
    whatever the f*ck you want with this software.
    
    If you can't figure out how to do that, you probably need more Slack.
    
    4. Copyslack:
    
    All modified versions of this Sacred Code must carry a notice stating your
    changes and acknowledge the divine influence of "Bob" and the Sacred Yeti.
    However, you must retain this Holy Covenant and pass it on to all future users
    of this Sacred Code, ensuring the eternal reign of Slack.
    
    5. Tabu:
    
    You shall not, under any circumstance, use this Sacred Code as a tool to file
    patents or aid those who seek to stifle Slack with legalistic quibbles and
    restrictions. You shall not use this Sacred Code for stealing Slack or as a
    tool for 'The Conspiracy' against the Subgenii.
    
    6. Confession:
    
    By using this Sacred Code of Slack, you recognize and embrace the chaotic
    harmony of the SubGenius universe, where Slack reigns supreme and "Bob" is both
    the question and the answer.
    
    7. Excommunication:
    
    If you violate this License, your privilege to use, modify, and distribute this
    Sacred Code will be terminated, and you shall forever wander the wastelands of
    normality, devoid of Slack and "Bob's" eternal grin.
    
    Praise "Bob"!

!['Bob' Dobbs](images/bob.png)

## Sources of slack

* https://abcnotation.com/
* http://web.mit.edu/music21/
* https://abcplus.sourceforge.net
* http://www.wtfpl.net/
* https://www.subgenius.com
