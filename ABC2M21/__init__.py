# -------------------------------------------------------------------------------
# Name:         ABC2M21/__init__.py
# Purpose:      This file serves as the initialization for the ABC2M21 package.
#
# Authors:      Marian Schulz
#
# Copyslack:    Copyright © 2023, Marian Schulz
# License:      SSL - SUBGENIUS SOFTWARE LICENSE
# -------------------------------------------------------------------------------
"""
*ABC* is a user-friendly music notation system that utilizes a simple text-based format,
making it easily understandable for both humans and computers. Comprising letters, digits,
and punctuation marks, *ABC* allows music to be notated on paper or within computer files

The *ABC2M21* package are focused on the task of converting ABC notation into `music21
<https://web.mit.edu/music21/>`_ representation. Typically, users dealing with *ABC* data may not
require the majority of methods and classes available in this package. To transform ABC notation
from Python text or a file path into a :class:`~music21.stream.Stream` object, the recommended
approach is to utilize the :func:`~abc_translator` function within this module.

*ABC2M21*, while not strictly adhering to all recommendations and definitions of the
abc standard v2.1, follows them to a considerable extent, aiming to maintain compatibility
and coherence with the standards outlined in the `abc:standard:v2.1 documentation
<https://abcnotation.com/wiki/abc:standard:v2.1>`_. *ABC2M21* takes into account some extensions
that are not part of the ABC standard, particularly considering that many available ABC tunes
may have been created or edited using `EasyABC <https://sourceforge.net/projects/easyabc/>`_ or
the tools from `abcplus <https://abcplus.sourceforge.net>`_.
"""

__all__ = [
    'abc_translator', 'tokenize', 'Field', 'Token', 'ABC2M21_CONFIG', 'ABCVersion',
]

import re
from pathlib import Path
from music21 import stream, environment
from ABC2M21.Parser import ABC2M21_CONFIG, ABCException, FileHeader, TuneHeader, TuneBody
from ABC2M21.ABCToken import tokenize, Field, Token, DEFAULT_VERSION, ABCVersion

# Some regular expressions to split the abc data
ABC_TUNE_BOOK_SPLIT = re.compile(r'(^X:.*$)', flags=re.MULTILINE).split
ABC_VERSION_SPLIT = re.compile(r'[ \n]*(%abc-\d+.*)\n', flags=re.MULTILINE).split
RE_MACRO = re.compile(r'^m:.*\n|\[m:[^\]]*\]', flags=re.MULTILINE)


def apply_macros(src: str, macros: dict[str, str] | None = None) -> (str, dict[str, str]):
    """
    Apply macros to the source string.

    Args:
        src (str): The source string to apply macros to.
        macros (dict[str, str] | None): A dictionary containing macros and their replacements.

    Returns:
        Tuple[str, dict[str, str]]: A tuple containing the modified source string and the
                                    updated macros.
    """

    # Start position of the current match
    start_pos = 0

    # List to store sections between macro definitions
    sections = []
    macros: dict[str, str] = {} if macros is None else dict(macros)

    def replace(t: str):
        for pattern, replacement in macros.items():
            t = t.replace(pattern, replacement)
        return t

    # Iterate over the found matches
    for match in RE_MACRO.finditer(src):
        sections.append(replace(src[start_pos:match.start()]))
        k, v = match.group().lstrip('[').rstrip(']').strip('m:').strip().split('=')
        macros[k.strip()] = replace(v).strip()
        start_pos = match.end()

    # Add the remaining text at the end
    sections.append(replace(src[start_pos:]))
    return "".join(sections), macros


def split_abc_data(src: str) -> (str, list[str], ABCVersion):
    """
    Split ABC data into the abc file header, individual ABC tunes and
    extract the abc version.

    Parameters:
    src (str): The ABC data.

    Returns:
    Tuple[str, List[str], ABCVersion]: A tuple containing the remaining source
    (after extracting tunes), a list of individual ABC tunes, and the ABC version.
    """
    src, *abc_tunes = ABC_TUNE_BOOK_SPLIT(src)
    # The ABC version string if set is the first line of an ABC file.
    try:
        _, version, src = ABC_VERSION_SPLIT(src, maxsplit=1)
        version = [int(d) for d in version.split('-', maxsplit=1)[1].split('.', maxsplit=2)]
        version = ABCVersion(version + (3 - len(version)) * [0])
    except ValueError:
        # no %%abc-.. Version found, use a default version ?
        version = DEFAULT_VERSION

    return src, abc_tunes, version


def abc_translator(src: str | Path) -> stream.Stream:
    """
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
    >>> tune_path = Path('../abc/avemaria.abc')
    >>> score = abc_translator(tune_path)
    >>> score
    <music21.stream.Score X:1 (file='../abc/avemaria.abc')>
    >>> score.metadata.title
    "Ave Maria (Ellen's Gesang III) - Page 1"

    However, music21 spanners are set in the Part object, so the following
    example, even if it consists of only a few notes, will return a Part object.

    >>> abc_fragment = '''
    ... !>(!ABCD!>)!'''
    >>> isinstance(abc_translator(abc_fragment), stream.Part)
    True
    """
    if isinstance(src, str):
        source_type = "string"
    elif isinstance(src, Path):
        source_type = f"{src}"
        with src.open() as f:
            src = f.read()
    else:
        raise ABCException("Illegal abc input, chose a pathlib.Path or str")

    src, abc_tunes, version = split_abc_data(src)
    if abc_tunes:
        # Evaluate and apply macros on the file header
        src, file_header_macros = apply_macros(src)
        parser = FileHeader(version)
        parser.process(tokenize(src, version))

        scores = []
        abc_tunes = iter(abc_tunes)
        while True:
            try:
                abc_ref_number = next(abc_tunes).split('%', maxsplit=1)[0].strip()
                src = next(abc_tunes, "")
            except StopIteration:
                break

            # Evaluate and apply macros on the tunes
            src = apply_macros(src, file_header_macros)[0].lstrip('\n')
            tokens = tokenize(src)
            # tokens = list(tokens)
            # HeaderParser will process tokens until the header ends with Field 'K:'
            parser = TuneHeader(file_header=parser, abc_version=version)
            parser.process(tokens)
            # tokens = list(tokens)
            # BodyParser will process all remaining tokens
            score = TuneBody(tune_header=parser).process(tokens)
            # if score.metadata:
            score.metadata.number = abc_ref_number

            if source_type == "string":
                score.id = abc_ref_number
            else:
                score.id = f"{abc_ref_number} (file='{source_type}')"

            scores.append(score)

        if len(scores) > 1:
            opus = stream.Opus(id=source_type)
            opus.append(scores)
            return opus
        return scores[0]

    # no, it is not a tune book just an abc fragment
    src = src.strip('\n') + '\n'

    parser = TuneHeader(abc_version=version)
    tokens = tokenize(src, abc_version=version)
    tokens = list(tokens)
    m21_stream = TuneBody(tune_header=parser).process(tokens)
    if len(m21_stream.parts) == 1:
        m21_stream = m21_stream.parts[0]
        if len(m21_stream.elements) == 1:
            measures = list(m21_stream.getElementsByClass(stream.Measure))
            if len(measures) == 1:
                return measures[0]
        return m21_stream
    return m21_stream


if __name__ == '__main__':
    import doctest

    us = environment.UserSettings()
    us['debug'] = True
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
