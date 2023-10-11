import copy
import pathlib
import re
from copy import deepcopy
from fractions import Fraction
from typing import Iterator, NamedTuple, TypeAlias
from abc import abstractmethod
from dataclasses import dataclass
import music21
from music21 import duration, spanner, dynamics, common, tie, instrument, clef
from music21 import expressions, articulations, harmony, style, environment
from music21 import key, pitch, stream, metadata, bar, tempo, layout
from music21 import note, chord, repeat, meter

from ABC2M21.ABCToken import DEFAULT_VERSION, ABCVersion, Field, Token, tokenize

ABC2M21_ENVIRONMENT = environment.Environment('ABC2M21')
ABC2M21_CONFIG = {'simplifiedComplexMeter': False }


Syllables: TypeAlias = list[str]

# Regular expressions for parsing ABC Fields
ABC_MIDI_1_RE = re.compile(r'voice\s+(?P<voice>[A-Za-b0-9]*)\s*instrument\s*=\s*(?P<program>[0-9]+)')
ABC_MIDI_2_RE = re.compile(r'program\s+(?P<channel>[0-9]+)\s+(?P<program>[0-9]+)')
ABC_MIDI_3_RE = re.compile(r'program\s+(?P<program>[0-9]+)')

ABC_CLEF_RE = re.compile(
    r'(?P<name>clef\s*=\s*\S+(?!\S))' +
    r'|(?P<octave>octave=[+\-]?[0-9](?!\S))' +
    r'|(?P<transpose>t(ranspose)?\s*=\s*[+\-]?[0-9]+(?!\S))' +
    r'|(?P<unamed>\S+)', re.MULTILINE
)
# Regular expression for extracting abc voice field properties
ABC_VOICE_RE = re.compile(
    r'(?P<name>(name|nm)\s*=\s*(".*?"|\S+)(?!\S))' +
    r'|(?P<subname>(subname|snm|sname)\s*=\s*(".*?"|\S+)(?!\S))'
    r'|(?P<stem>(stem)\s*=\s*(".*?"|\S+)(?!\S))')

ABC_RE_TEMPO = re.compile(r'\s*("[^"]*")?\s*([0-9/ C]+\s*=\s*[0-9]+|[0-9]+)?\s*("[^"]*")?')
ABC_RE_ABC_NOTE = re.compile(r'([\^_=]*)([A-Ga-g])([\',]*)([0-9/]*)([\-]*)')

ABC_RE_voices = re.compile(r'[/(/)]|\d+|[A-Z]')
ABC_TUNE_BOOK_SPLIT = re.compile(r'(^X:.*$)', flags=re.MULTILINE).split
ABC_VERSION_SPLIT = re.compile(r'[ \n]*(%abc-\d+.*)\n', flags=re.MULTILINE).split

# <tonic> exp <accidentals>
ABC_KEY_EXP_RE = re.compile(
    r'(?P<tonic>([A-G][#b]?))\s+exp(?P<accidentals>(\s+[\^_=]+[a-g])+)'
)
# <tonic><mode><accidentals>
ABC_KEY_MODE_RE = re.compile(
    r'(?P<tonic>([A-G][#b]?))\s*(?P<mode>([aAmMlLdDpPiI][A-Za-z]*)?)(?P<accidentals>(\s*[\^_=]+[a-g])*)'
)

ABC_MODES = {v[:3]: v for v in ['major', 'minor', 'locrian', 'dorian', 'lydian',
                                'phrygian', 'ionian', 'aeolian', 'mixolydian']}

RE_MACRO = re.compile(r'^m:.*\n|\[m:[^\]]*\]', flags=re.MULTILINE)

# Mappings from abc decorations to music21 Articulations
M21_ARTICULATIONS = {
    '>': articulations.Accent,
    '^': articulations.StrongAccent,
    '+': articulations.Pizzicato,
    'staccato': articulations.Staccato,
    'marcato': articulations.StrongAccent,
    'accent': articulations.Accent,
    'emphasis': articulations.Accent,
    'strongaccent': articulations.StrongAccent,
    'straccent': articulations.StrongAccent,
    'tenuto': articulations.Tenuto,
    'upbow': articulations.UpBow,
    'downbow': articulations.DownBow,
    'breath': articulations.BreathMark,
    'open': articulations.OpenString,
    'plus': articulations.Pizzicato,
    'snap': articulations.SnapPizzicato,
    'nail': articulations.NailPizzicato,
    'doit': articulations.Doit,
    'thumb': articulations.StringThumbPosition,
    'cesura': articulations.Caesura
}

# Mapping from abc decorations to music21 RepeatMark
M21_REPEATS = {
    'segno': repeat.Segno,
    'fine': repeat.Fine,
    'coda': repeat.Coda,
    'D.S.': repeat.DalSegno,
    'D.S.alcoda': repeat.DalSegnoAlCoda,
    'D.S.alfine': repeat.DalSegnoAlFine,
    'dacapo': repeat.DaCapo,  # @TODO:  'dacoda' the word "Da" followed by a Coda sign
    'D.C.alcoda': repeat.DaCapoAlCoda,
    'D.C.alfine': repeat.DaCapoAlFine,
}


# Mapping from abc decorations to music21 Expressions
def upright_fermata() -> expressions.Fermata:
    """
    Creates and returns a music21 Fermata object with the type 'upright'.
    """
    f = expressions.Fermata()
    f.type = 'upright'
    return f


M21_EXPRESSIONS = {
    'invertedfermata': expressions.Fermata,
    'trill': expressions.Trill,
    'invertedmordent': expressions.InvertedMordent,
    'lowermordent': expressions.Mordent,
    'uppermordent': expressions.InvertedMordent,
    'pralltriller': expressions.InvertedMordent,
    'mordent': expressions.Mordent,
    'fermata': upright_fermata,
    'turn': expressions.Turn,
    'invertedturn': expressions.InvertedTurn,
    'slide': expressions.Schleifer,
    'arpeggio': expressions.ArpeggioMark,
    'tremolo': expressions.Tremolo
}

# Mapping from abc spanner (decorations) to music21 Spanner
M21_OPEN_SPANNER = {
    'trill(': expressions.TrillExtension,
    'diminuendo(': dynamics.Diminuendo,
    '>(': dynamics.Diminuendo,
    'crescendo(': dynamics.Crescendo,
    '<(': dynamics.Crescendo,
}

# Tuple of ABC Dynamics
M21_DYNAMICS = ('pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'ffff', 'sfz')

# Tuple of abc close spanner decorations
M21_CLOSE_SPANNER = ('diminuendo)', 'crescendo)', 'trill)', '<)', '>)')


class ABCException(Exception):
    pass


class ABCObject:

    def abc_error(self, message: str, token: Token = None, exception=None):
        """
        Loggt eine Fehlermeldung im ABC-Parser.

        Args:
            message (str): Die Fehlermeldung.
            token (Token): Das betroffene Token (optional).
            exception (Exception): Die zugehörige Exception (optional).
        """

        messages = [f"{self.__class__.__name__}: {message}"]
        if token:
            messages.append(f'\n{token}')
        if exception:
            messages.append(f'\n{exception}')

        ABC2M21_ENVIRONMENT.printDebug(messages)


class ScoreInstruction(NamedTuple):
    """
    Represents instructions extracted from a Score directive in the ABC
    notation.

    Attributes:
        order (List[str]): The order of voices.
        brace (List[List[str]]): Staff groups enclosed in braces.
        bracket (List[List[str]]): Staff groups enclosed in brackets.
        square (List[List[str]]): Staff groups enclosed in square brackets.
        floating (List[Tuple[str, str]]): Floating staff groups
        continued_bar_lines (List[List[str]]): Bar lines continuation in staff
        groups.
    """

    order: list[str]
    brace: list[list[str]]
    bracket: list[list[str]]
    square: list[list[str]]
    floating: list[tuple[str, str]]
    continued_bar_lines: list[list[str]]


def join_voices(voices: list[stream.Part]) -> stream.Part:

    new_part = deepcopy(voices[0])
    for part in voices[1:]:
        # At first, we copy all spanners into the new part
        for sp in part.getElementsByClass(spanner.Spanner):
            new_part.insert(0, sp)

        for t_measure, s_measure in zip(new_part.getElementsByClass(stream.Measure),
                                        part.getElementsByClass(stream.Measure)):
            for voice in s_measure.getElementsByClass(stream.Voice):
                t_measure.append(0, voice)

    return new_part


def apply_macros(src: str, macros: dict[str, str] | None = None) -> (str, dict[str, str]):
    # Startposition der aktuellen Übereinstimmung
    start_pos = 0
    # Liste zur Speicherung von Teilen
    voices = []
    macros: dict[str, str] = {} if macros is None else dict(macros)

    def replace(t: str):
        for pattern, replacement in macros.items():
            t = t.replace(pattern, replacement)
        return t

    # Iteriere über die gefundenen Übereinstimmungen
    for match in RE_MACRO.finditer(src):
        voices.append(replace(src[start_pos:match.start()]))
        k, v = match.group().lstrip('[').rstrip(']').strip('m:').strip().split('=')
        macros[k.strip()] = replace(v).strip()
        start_pos = match.end()

    # Füge den verbleibenden Text am Ende hinzu
    voices.append(replace(src[start_pos:]))
    return "".join(voices), macros


def fix_measures(score: stream.Score):
    """
    Apply the same bar lines and meter to all synchronized measures of the
    voices in this Score.

    This function collects the most recent meter and bar lines
    of each measure in each voice and assigns them to all synchronized
    measures. This is particularly useful when dealing with repeat bar lines
    or irregular bar lines to ensure consistency within the voices.

    The method iterates through each voice and measure, collecting the
    most recent left and right bar lines that are not regular (indicating
    special bar lines). Then, it assigns these special bar lines to all
    synchronized measures within each voice.

    This ensures that special bar lines are consistently applied across
    synchronized measures in all voices.
    """
    # Create a list to store the most recent left and right bar lines for
    # each measure.

    try:
        max_len = max(len(part.getElementsByClass(stream.Measure))
                      for part in score.getElementsByClass(stream.Part))
    except ValueError:
        raise ABCException('Tune is complete empty')

    bar_lines = [None] * max_len * 2
    meters = [list() for _ in range(max_len)]

    # Iterate through each voice and measure to collect the most recent
    # irregular bar lines.
    for part in score.parts:
        for number, measure in enumerate(part.getElementsByClass(stream.Measure)):
            mtimesig: meter.TimeSignature = measure.timeSignature
            if mtimesig and mtimesig.barDuration.quarterLength == measure.highestTime:
                meters[number].append(mtimesig)

            # Check for irregular left bar lines and store them in the
            # 'bar_lines' list.
            if (bar_line := measure.leftBarline) and bar_line.type != 'regular':
                bar_lines[number * 2] = bar_line
            # Check for irregular right bar lines and store them in the
            # 'bar_lines' list.
            if (bar_line := measure.rightBarline) and bar_line.type != 'regular':
                bar_lines[number * 2 + 1] = bar_line

            measure.number = number

    # Assign the stored special bar lines to all synchronized measures
    # within each voice.
    for part in score.parts:
        for bar_num, measure in enumerate(part.getElementsByClass(stream.Measure)):
            _meter = meters[bar_num]
            if _meter:
                measure.time_signature = _meter[-1]

            measure.leftBarline = bar_lines[bar_num * 2]
            measure.rightBarline = bar_lines[bar_num * 2 + 1]



class ABCParser(ABCObject):
    """
    Base class for token processors implements the abc_token method.
    """

    def __init__(self, abc_version: ABCVersion = DEFAULT_VERSION):
        """
        Initialize a new ABC Processor.

        Args:
            abc_version (ABCVersion): The ABC version for processing.
        """
        self.abc_version: ABCVersion = abc_version

    def abc_token(self, token: Token):
        # If a token is returned while processing the current token the token
        # is not necessarily the same token.

        abc_method = getattr(self, f'abc_{token.type}', None)
        if abc_method is None:
            self.abc_error(f"No abc_method 'abc_{token.type}'.", token)
        else:
            return abc_method(token)

class FileHeader(ABCParser):
    """
    A processor for handling ABC file header information.

    This class inherits from `aProcessor` and is specifically designed to handle
    ABC file header tokens and extract relevant information from them.

    """

    FIELD_METADATA = {'D': 'discography', 'B': 'book', 'H': 'history', 'N': 'notes', 'F': 'file', 'S': 'source',
                      'R': 'rhythm', 'G': 'groups'}

    # The default dictionary for user-defined symbols.
    DEFAULT_USER_DEF_SYMBOLS: dict[str, list[Token]] = {
        '.': list(tokenize('!staccato!')),
        'H': list(tokenize('!fermata!')),
        'L': list(tokenize('!accent!')),
        'M': list(tokenize('!lowermordent!')),
        'O': list(tokenize('!coda!')),
        'P': list(tokenize('!uppermordent!')),
        'S': list(tokenize('!segno!')),
        'T': list(tokenize('!trill!')),
        'k': list(tokenize('!straccent!')),
        'K': list(tokenize('!accent!')),
        'u': list(tokenize('!upbow!')),
        'v': list(tokenize('!downbow!'))
    }

    def __init__(self, abc_version: ABCVersion = DEFAULT_VERSION):
        super().__init__(abc_version)
        self.metadata: metadata.Metadata = metadata.Metadata()
        self.quarter_length: float | None = None
        self.time_signature: meter.TimeSignature | None = None
        self.user_defined: dict[str, list[Token]] = dict(
            FileHeader.DEFAULT_USER_DEF_SYMBOLS)

        self.accidental_mode: str = 'not' if abc_version < (2, 0, 0) \
            else 'pitch'

        self.is_legacy_abc_decoration: bool = abc_version == (2, 0, 0)
        self.is_legacy_abc_chord: bool = (abc_version != (2, 0, 0)
                                          and not self.is_legacy_abc_decoration)
        self.linebreak = ['<EOL>', '$', '!']

        self.midi = {}
        self.staves: None | ScoreInstruction = None

    def abc_unit_note_length(self, token: Field):
        """
        Process a token for the unit note length according to the abc standart.
        The quarter length of a crotchet (1/4) is 1.0

        Examples:

        >>> from ABC2M21 import Field
        >>> fh = FileHeader()

        Commonly used valuee for unit note length area crotchet (1/4)

        >>> fh.abc_unit_note_length(Field('UnitNoteLength', 'L:1/4'))
        1.0

        Or quaver (1/8)

        >>> fh.abc_unit_note_length(Field('UnitNoteLength', 'L:1/8'))
        0.5

        But L:1 (or L:1/1), L:1/2, L:1/16, L:1/32 down to L:1/512 are available

        >>> fh.abc_unit_note_length(Field('UnitNoteLength', 'L:1'))
        4.0
        >>> fh.abc_unit_note_length(Field('UnitNoteLength', 'L:1/2'))
        2.0
        >>> fh.abc_unit_note_length(Field('UnitNoteLength', 'L:1/16'))
        0.25
        >>> fh.abc_unit_note_length(Field('UnitNoteLength', 'L:1/32'))
        0.125
        >>> fh.abc_unit_note_length(Field('UnitNoteLength', 'L:1/512'))
        0.0078125
        """
        try:
            self.quarter_length = float(4 * Fraction(token.data))
            return self.quarter_length
        except Exception as e:
            self.abc_error(f"Illegal abc UnitNoteLength.", token, e)
            return None

    def abc_unknown_token(self, token: Field):
        """
        Process an unknown token, print a debug message and discard the token
        """
        self.abc_error(f"Unknown Token", token)

    def abc_meter(self, token: Field) -> meter.TimeSignature:
        """
        Represents a token for the Meter / TimeSignature. Meter fields specify
        the time signature of the music and define the rhythm structure.

        Args:
            token (Field): The meter token to process

        Examples:

        >>> from ABC2M21 import Field
        >>> fh = FileHeader()

        Apart from standard meters, e.g. M:6/8 or M:4/4

        >>> fh.abc_meter(Field('Meter', 'M:6/8'))
        <music21.meter.TimeSignature 6/8>
        >>> fh.abc_meter(Field('Meter', 'M:4/4'))
        <music21.meter.TimeSignature 4/4>

        The symbols M:C and M:C| give common time and cut time

        >>> fh.abc_meter(Field('Meter', 'M:C'))
        <music21.meter.TimeSignature 4/4>
        >>> fh.abc_meter(Field('Meter', 'M:C|'))
        <music21.meter.TimeSignature 2/2>

        It is also possible to specify a complex meter

        >>> fh.abc_meter(Field('Meter', 'M:(2+3+2)/8'))
        <music21.meter.TimeSignature 2/8+3/8+2/8>
        """
        meter_str = token.data

        if not meter_str or meter_str == 'none':
            self.time_signature = None
        elif meter_str == 'C' or meter_str == 'common':
            self.time_signature = meter.TimeSignature('common')
        elif meter_str == 'C|' or meter_str == 'cut':
            self.time_signature = meter.TimeSignature('cut')
        else:
            denominator: int = 1
            voices = meter_str.split('/', 1)
            if num := voices[0].strip():
                numerators = [int(n) for n in ("".join(
                    c for c in num if c.isdigit() or c == '+').split('+'))]
            else:
                numerators = [1]

            try:
                denominator = int("".join(
                    c for c in voices[1].strip() if c.isdigit()))
            except ValueError as e:
                self.abc_error('Failed to calculate denominator of the meter token', token, e)

            if len(numerators) > 1:
                if ABC2M21_CONFIG.get('simplifiedComplexMeter', False):
                    meter_str = "+".join([f"{sum(numerators)}/{denominator}"])
                else:
                    meter_str = "+".join([f"{n}/{denominator}" for n in numerators])

                self.time_signature = meter.TimeSignature(meter_str)
            else:
                self.time_signature = meter.TimeSignature(f"{sum(numerators)}/{denominator}")

        return self.time_signature

    def abc_meta_data(self, token: Field):
        """
        Process a metadata token, updating the tune's metadata accordingly.
        Metadta token are abc fields without relevance for the interpretation
        of the tune and stored in the score metadata object.
        Fields without corespending value in the music21 metadata object are
        stored in a custom field.

        Args:
            token (Field): The metadata token to process

        Examples:

        >>> from ABC2M21 import Field
        >>> fh = FileHeader()
        >>> fh.abc_meta_data(Field('MetaData', 'B:WTC I'))
        >>> fh.abc_meta_data(Field('MetaData', 'C:J.S. Bach'))
        >>> fh.abc_meta_data(Field('MetaData', 'O:Eisenach'))
        >>> fh.abc_meta_data(Field('MetaData', 'T:Prelude No.1 in C major'))
        >>> fh.metadata.composer
        'J.S. Bach'
        >>> fh.metadata.localeOfComposition
        'Eisenach'
        >>> fh.metadata.getCustom('book')
        (<music21.metadata.primitives.Text WTC I>,)

        Title is not an abc field for the ABCFileHeader

        >>> fh.metadata.title is None
        True
        """
        md = self.metadata

        match token.tag:
            case 'T':
                if type(self) == FileHeader:
                    self.abc_error("Ignore titel (T:) field.", token)
                else:
                    md.title = token.data
            case 'C':
                if md.composers:
                    md.composers = md.composers + (token.data,)
                else:
                    md.composers = [token.data]
            case 'O' | 'A':
                if md.localeOfComposition:
                    md.localeOfComposition += f", {token.data}"
                else:
                    md.localeOfComposition = token.data

            case 'Z':
                c = metadata.Contributor()
                for trans_key in ['abc-transcription ',
                                  'abc-edited-by ',
                                  'abc-copyright ']:
                    if token.data.startswith(trans_key):
                        c.name = token.data.lstrip(trans_key.strip())
                        c.role = trans_key
                        break
                else:
                    c.name = token.data
                    c.role = 'abc-transcription'
                md.addContributor(c)

            case _:
                if name := FileHeader.FIELD_METADATA.get(token.tag, None):
                    custom = md.getCustom(name)
                    if isinstance(custom, list):
                        custom.append(token.data)
                    else:
                        md.addCustom(name, [token.data])
                else:
                    self.abc_error(f"Ignore ABC field '{token.tag}'.", token)

    def abc_user_def(self, token: Field):
        """
        Process user-defined symbol tokens and store them in the 'U' field.
        The letters H-W and h-w and the symbol ~ can be assigned with the U:
        field. In ABC notation, user-defined symbols are commonly used for
        abbreviating decorations, but this method can store any (not just
        decorations) and multible tokens for a user-defined symbols

        Args:
          token (Field): The user-defined symbol token to be
          processed.

        Examples:

        To assign the letter T to represent the trill, you can write:

        >>> processor = FileHeader()
        >>> processor.abc_user_def(Field('UserDef', 'U: T = !trill!'))
        >>> processor.user_defined['T']
        [<decoration: '!trill!' (pos=1)>]
        """
        try:
            symbol, token_str = token.data.split('=', maxsplit=1)
            symbol = symbol.strip()
            if symbol.upper() not in "HIJKLMNOPQRSTUVW~":
                self.abc_error(f"User defined symbol {symbol} is not in [H-Wh-w~]", token)
                return

            self.user_defined[symbol] = list(tokenize(token_str))
        except Exception as e:
            self.abc_error(f"Error while parsing definition of an user-defined symbol", token, e)

    def abc_midi_instruction(self, token: Field):
        """
        Processes a MIDI instruction token.
        Currently, there is support for three MIDI directives:

        - I:MIDI program <n>
        - I:MIDI program <c> <n>
        - I:MIDI voice <id> instrument=<n>

        Args:
            token (Field): The MIDI instruction token to process.

        Examples:

        The following syntax, defined by the ABC standard, assigns a MIDI instrument
        to the ABC voice with the id 'Tb'

        >>> fh = FileHeader()
        >>> token = Field('Instruction', 'I: MIDI voice Tb instrument=59')
        >>> fh.abc_midi_instruction(token)
        >>> fh.midi
        {'Tb': 59}

        Although not defined by the ABC standard, this syntax is often used in
        ABC notations converted from MIDI files or created by popular ABC
        software. Using this syntax, MIDI channels are assigned to ABC voices
        in the order they appear in the ABC tune. (MIDI channel 1 => first ABC voice)

        >>> token = Field('Instruction', 'I: MIDI program 1 54')
        >>> fh.abc_midi_instruction(token)
        >>> fh.midi
        {'Tb': 59, 1: 54}

        The next MIDI instruction (`I:MIDI program <n>`) will assign the MIDI
        program to the recent voice and all following voices until another MIDI
        instruction. However, it's important to note that this MIDI instruction
        type will be overridden by any explicit instrument assignments made for
        the respective voices using the more specific instructions mentioned above.

        >>> token = Field('Instruction', 'I: MIDI program 23')
        >>> fh.abc_midi_instruction(token)
        >>> fh.midi
        {'Tb': 59, 1: 54, None: 23}
        """

        try:
            instruction_str = token.src[2:].split(maxsplit=1)[1]
        except Exception as e:
            self.abc_error('Unknown midi instruction.', token, e)
            return

        if match := ABC_MIDI_1_RE.match(instruction_str):
            gd = match.groupdict()
            self.midi[gd['voice'][:20].strip()] = int(gd['program'].strip())
        elif match := ABC_MIDI_2_RE.match(instruction_str):
            gd = match.groupdict()
            self.midi[int(gd['channel'].strip())] = int(gd['program'].strip())
        elif match := ABC_MIDI_3_RE.match(instruction_str):
            gd = match.groupdict()
            self.midi[None] = int(gd['program'].strip())
        else:
            self.abc_error(f'Unknown midi instruction.', token)

    def abc_linebreak_instruction(self, token: Field):
        """
        Processes a linebreak instruction token to controll layout linebreaks
        in the score. To allow for all line-breaking preferences, the
        "I:linebreak" instruction may be used, together with four possible values,
        to control score line-breaking.

        - "I:linebreak $": Indicates that the $ symbol is used in the tune body
                           to typeset a score line-break. Any newlines in the
                           music code are ignored for typesetting purposes.

        - "I:linebreak !": Indicates that the ! symbol is used in the tune body
                           to typeset a score line-break. Any newlines in the
                           music code are ignored for typesetting purposes.

        - "I:linebreak <EOL>": indicates that the newline token/charakter is
                               used to typeset a score line-break. This the
                               default behavour

        - "I:linebreak <none>": indicates that all line-breaking is to be
                                carried out automatically and any code
                                line-breaks are ignored for typesetting
                                purposes.

        Contrary to the recommendations of the ABC standard, 'linebreak !' can be
        used simultaneously with '!...!' for decorations. This implementation
        detail may change if issues arise in the interpretation or if a strict
        interpretation is required

        Args:
            token (Field): The instruction token to process.

        Examples:

        The values <EOL>, $ and ! may also be combined so that more than one
        symbol can indicate a score line-break.

        >>> fh = FileHeader()
        >>> token = Field('Instruction', 'I:linebreak <EOL> $')
        >>> fh.abc_linebreak_instruction(token)
        >>> fh.linebreak
        ['<EOL>', '$']

        The second I:linebreak instruction overrides the first.

        >>> token = Field('Instruction', 'I:linebreak !')
        >>> fh.abc_linebreak_instruction(token)
        >>> fh.linebreak
        ['!']

        This I:linebreak instruction will disable all code linebreak

        >>> token = Field('Instruction', 'I:linebreak <none>')
        >>> fh.abc_linebreak_instruction(token)
        >>> fh.linebreak
        []
        """
        try:
            instruction_str = token.src[2:].split(maxsplit=1)[1]
        except Exception as e:
            self.abc_error('Unknown linebreak instruction.', token, e)
            return

        linebreaks = []
        for linebreak in instruction_str.split():
            if linebreak in ('<EOL>', '$', '!'):
                if linebreak not in linebreaks:
                    linebreaks.append(linebreak)
            elif linebreak == '<none>':
                linebreaks = []
            else:
                self.abc_error(f"Ignore unknown linebreak value '{linebreak}'.", token)

        self.linebreak = linebreaks

    def abc_stave_instruction(self, token: Field):
        """
        Parse the abc score directive/instruction acording
        `abc:standard:v2.1:voice_grouping
        <https://abcnotation.com/wiki/abc:standard:v2.1#voice_grouping>`_

        The "I:score" or "I:staves" instruction determines how voices are
        displayed in the musical score.

        Voices in parentheses () share a staff, forming a voice group. Voices
        without parentheses have separate staves. Curly braces {} connect
        staves visually, creating a voice block. Square brackets [] also form
        a voice block, connecting the staves.

        Using "|" between blocks or groups draws continued bar lines, indicating
        musical relationships.

        Args:
            token (Field): The SCORE instruction token to process.

        >>> fh = FileHeader()
        >>> token = Field('Instruction',
        ...                        'I:score Solo [(S A) (T B)] {RH | (LH1 LH2)}')
        >>> fh.abc_stave_instruction(token)

        The order propertie define the order the voices are set in the score

        >>> fh.staves.order
        ['Solo', 'S', 'A', 'T', 'B', 'RH', 'LH1', 'LH2']

        >>> fh.staves.brace
        [['RH', 'LH1', 'LH2']]

        >>> fh.staves.bracket
        [['S', 'A'], ['T', 'B'], ['LH1', 'LH2']]

        >>> fh.staves.square
        [['S', 'A', 'T', 'B']]

        >>> fh.staves.continued_bar_lines
        [['RH', 'LH1', 'LH2']]

        """
        try:
            instruction_str = token.src[2:].split(maxsplit=1)[1]
        except Exception as e:
            self.abc_error('Unknown score instruction.', token, e)
            return

        # Regular expressions for various patterns
        _RE_BAR_LINES = re.compile(r'[(][^)]+[)]|'
                                   r'[\[][^]]+[]]|'
                                   r'[{][^}]+[}]|'
                                   r'[^{}\[\]()\s]+')

        _RE_BRACKETS = re.compile(r'[(\[{)\]}|]')

        # List of voice identifiers in the order they should appear in
        # the score. Extract all voices using regular expressions
        order: list[str] = re.findall(r'([^\s()\[\]{}|]+)', instruction_str)
        floating: list[tuple[str, str]] = []
        for prev, recent in zip(order, order[1:]):
            if recent.startswith('*'):
                floating.append((prev, recent.strip('*')))

        order = [v.strip('*') for v in order]

        # List of voice groups with continued bar lines between the
        # associated staves.
        continued_bar_lines: list[list[str]] = []

        # Extract brace groups using regular expressions
        bracket: list[list[str]] = [_RE_BRACKETS.sub(' ', m).split()
                                    for m in re.findall(r'\([^)]+\)', instruction_str)]
        bracket = [[v for v in group if '*' not in v] for group in bracket]

        # Extract curly groups using regular expressions
        brace: list[list[str]] = [_RE_BRACKETS.sub(' ', m).split()
                                  for m in re.findall(r'\{[^}]+}', instruction_str)]
        brace = [[v for v in group if '*' not in v] for group in brace]

        # Extract square groups using regular expressions
        square: list[list[str]] = [_RE_BRACKETS.sub(' ', m).split()
                                   for m in re.findall(r'\[[^]]+]', instruction_str)]
        square = [[v for v in group if '*' not in v] for group in square]

        # Find voice blocks or voice groups separated from each other by a | character
        voices = instruction_str.split('|')
        continued = []
        for i in range(1, len(voices)):
            left = ' '.join(voices[:i])
            if left := _RE_BAR_LINES.findall(left):
                left = _RE_BRACKETS.sub('', left[-1]).split()
                right = ' '.join(voices[i:])
                if right := _RE_BAR_LINES.findall(right):
                    new_group = left + _RE_BRACKETS.sub('', right[0]).split()
                    if continued and continued[-1][-1] == new_group[0]:
                        continued[-1].extend(new_group[1:])
                    else:
                        continued.append(new_group)

        # Removes any group in 'continued_bar_lines' that are subsets
        # of other groups in 'continued_bar_lines'
        for sublist in sorted(continued, key=len, reverse=True):
            if not any(set(sublist).issubset(other_list) for other_list in continued_bar_lines):
                continued_bar_lines.append(sublist)

        if not order:
            self.abc_error('No ABC voices found in SCORE instruction', token)
        else:
            self.staves = ScoreInstruction(order=order, brace=brace, bracket=bracket,
                                           floating=floating, square=square,
                                           continued_bar_lines=continued_bar_lines)

    def abc_propagate_accidentals_instruction(self, token: Field):
        """

        Args:
            token (Field): The propagate-accidentals instruction token
                                    to process.

        Examples:

        Set the accidental mode to 'not', 'octave', or 'pitch'

        >>> fh = FileHeader()
        >>> fh.accidental_mode
        'not'
        >>> token = Field('instruction', 'I:propagate-accidentals octave')
        >>> fh.abc_propagate_accidentals_instruction(token)
        >>> fh.accidental_mode
        'octave'
        >>> token = Field('instruction', 'I:propagate-accidentals pitch')
        >>> fh.abc_propagate_accidentals_instruction(token)
        >>> fh.accidental_mode
        'pitch'
        """
        try:
            instruction_str = token.data.split(maxsplit=1)[1].lower()
        except Exception as e:
            self.abc_error('Unknown propagate-accidentals instruction.',
                           token, e)
            return

        if instruction_str not in ('not', 'octave', 'pitch'):
            self.abc_error(f"Unknown accidental mode.", token)
            return

        self.accidental_mode = instruction_str

    def abc_continueall_instruction(self, token: Field):
        """
        Process a continueall instruction token. The '%%continueall true'
        directive is replaced by "I:linebreak !" in abc 2.1

        Args:
            token (Field): The continueall instruction token to
                                    process.

        Examples:

        >>> fh = FileHeader()
        >>> token = Field('Instruction', 'I:continueall yes')
        >>> fh.abc_instruction(token)
        >>> fh.linebreak
        ['!']
        """
        try:
            instruction_str = token.src[2:].split(maxsplit=1)[1].lower()
        except Exception as e:
            self.abc_error('Unknown continueall instruction token.',
                           token, e)
            return

        if instruction_str.lower() in ('1', 'true', 'yes'):
            self.linebreak = ['!']
        else:
            self.abc_error(f"Illegal continueall value '{instruction_str}'.",
                           token)

    def abc_decoration_instruction(self, token: Field):
        """
        Process a decoration instruction token.

        Decorations are enclosed by "!" symbols. The use of "+" for decorations
        is deprecated.

        To use "+" for decorations, add "I:decoration +" in the file or tune
        header. All "+" decorations will be treated as corresponding "!" decorations.

        The "I:decoration !", allowing to overide a "I:decoration +" in the tune header
        set in the file header.

        - Contrary to the ABC standard, it is also possible to decorate using
          '!' symbols even when 'I:decoration +' has been set. This
          implementation detail may change if issues arise in the interpretation
          of ABC tunes or if a strict interpretation is required.

        >>> fh = FileHeader(abc_version=(1, 5, 0))
        >>> fh.is_legacy_abc_chord
        True
        >>> fh.is_legacy_abc_decoration
        False

        Setting the decoration symbol to '+' will disable the legacy chords.

        >>> token = Field('Instruction', 'I:decoration +')
        >>> fh.abc_instruction(token)
        >>> fh.is_legacy_abc_chord
        False
        >>> fh.is_legacy_abc_decoration
        True
        """
        try:
            instruction_str = token.src[2:].split(maxsplit=1)[1].lower()
        except Exception as e:
            self.abc_error('Unknown decoration instruction token.',
                           token, e)
            return

        if instruction_str == '+':
            # enable the legacy decoration symbol '+'
            self.is_legacy_abc_decoration = True
            # but disable the legacy chord symbol '+'
            self.is_legacy_abc_chord = False
        else:
            self.abc_error(f"Unknown decoration dialect '{instruction_str}'.", token)

    def abc_instruction(self, token: Field):
        """
        Process an instruction token. Any directives are mapped to
        instructions. In most cases the token will be passed to a more
        specific instruction processing method

        Implemented Instructions:

        - I:linebreak
        - I:score | staves
        - I:propagate-accidentals
        - I:decoration
        - I:continueall
        - I:midi

        Args:
            token (Field): The instruction token to process.

        Examples:

            >>> fh = FileHeader()
            >>> token = Field('Instruction', 'I:linebreak <EOL> $')
            >>> fh.abc_instruction(token)
            >>> fh.linebreak
            ['<EOL>', '$']

        """
        try:
            instruction_type = token.data.split(maxsplit=1)[0].upper()
        except Exception as e:
            self.abc_error('Illegal instruction token', token, e)
            return

        match instruction_type:
            case 'SCORE' | 'STAVES':
                self.abc_stave_instruction(token)
            case 'PROPAGATE-ACCIDENTALS':
                self.abc_propagate_accidentals_instruction(token)
            case 'CONTINUEALL':
                self.abc_continueall_instruction(token)
            case 'MIDI':
                self.abc_midi_instruction(token)
            case 'LINEBREAK':
                self.abc_linebreak_instruction(token)
            case 'DECORATION':
                self.abc_decoration_instruction(token)
            case _:
                self.abc_error(f"Unsupported instruction '{instruction_type}'.", token)

    def process(self, token_generator: Iterator[Token]):
        """
        Process a sequence of tokens, extracting relevant information.

        Args:
          token_generator (Iterator[Token]): An iterator of ABC tokens.

        Examples:

        >>> abc_file_fragment = '''
        ... C:Johann Sebastian Bach
        ... M:C
        ... X:
        ... '''
        >>> processor = FileHeader()
        >>> token_generator = tokenize(abc_file_fragment)
        >>> processor.process(token_generator)
        >>> processor.metadata.composer
        'Johann Sebastian Bach'

        >>> processor.time_signature
        <music21.meter.TimeSignature 4/4>

        """
        for token in token_generator:
            # End the generator at the first X: Field. We will lose the X: token,
            # but this is okay as we don't need them anyway.
            if token.src.startswith('X:'):
                return
            self.abc_token(token)


@dataclass
class VoiceInfo:
    """
    Data class representing information about an abc voice.

    Attributes:
        name (str | None): The name of the part.
        sub_name (str | None): The abbreviation of the part.
        stem (str | None): The stem information for the part.
        m21_clef (clef.Clef | None): The clef associated with the part.
        octave (int | None): The octave information for the part.
    """
    voice_id: str = None
    name: str | None = None
    sub_name: str | None = None
    stem: str | None = None
    m21_clef: clef.Clef | None = None
    octave: int | None = None


class TuneHeader(FileHeader):
    """
    Initialize a TuneHeaderProcessor.

    This class inherits from `aProcessor` and is specifically designed to
    handle ABC tune header tokens and extract relevant information from them.

    The `TuneHeaderProcessor` will copy the metadata and field from the
    `FileHeaderProcessor`.

    Args:
        file_header (`FileHeader`): The file header processor containing
            metadata and fields from the file header.
        abc_version (`Token`): The ABC version associated with the
            tune.

    """

    def __init__(self,
                 file_header: FileHeader | None = None,
                 abc_version: ABCVersion = DEFAULT_VERSION):

        super().__init__(abc_version)

        # We need to deepcopy mutable values
        if file_header:
            self.metadata = deepcopy(file_header.metadata)
            self.quarter_length = file_header.quarter_length
            self.time_signature = file_header.time_signature
            self.user_defined = deepcopy(file_header.user_defined)
            self.linebreak = deepcopy(file_header.linebreak)
            self.midi = deepcopy(file_header.midi)
            self.accidental_mode = file_header.accidental_mode
            self.is_legacy_abc_decoration = file_header.is_legacy_abc_decoration
            self.is_legacy_abc_chord = file_header.is_legacy_abc_chord
            self.staves = file_header.staves

        self.key_signature: key.KeySignature | None = None
        self.clef: clef.Clef | None = None
        self.octave: int = 0
        self.tempo: tempo.MetronomeMark | None = None
        self.section_sequence: str = ''
        self.voice_info = {}
        self.token_generator = None

    def process(self, token_generator: Iterator[Token]):
        """
        Process a sequence of tokens, extracting relevant information from the
        tune header.

        The tune header processing ends after encountering the first 'K:' field, as
        the tune body begins at that point.

        Args:
            token_generator (Iterator[Token]): An iterator of ABC tokens.

        Example:

        >>> abc_file = '''
        ... C:John Doe
        ... L:1/4
        ... X:1
        ... T:Hello
        ... Q:1/4=26 "slow"
        ... P:AB2C
        ... C:Max Mustermann
        ... V:Violine clef="treble" name="First Violine"
        ... K:C
        ... '''
        >>> tokenizer = tokenize(abc_file)
        >>> fh = FileHeader()
        >>> fh.process(tokenizer)
        >>> th = TuneHeader(fh)
        >>> th.process(tokenizer)
        >>> th.metadata.composers
        ('John Doe', 'Max Mustermann')
        >>> th.metadata.title
        'Hello'
        >>> th.quarter_length
        1.0
        >>> th.key_signature
        <music21.key.Key of C major>
        >>> th.section_sequence
        'ABBC'
        >>> th.tempo
        <music21.tempo.MetronomeMark slow Quarter=26>
        >>> th.voice_info['Violine']
        VoiceInfo(voice_id='Violine', name='First Violine', sub_name=None, stem=None, \
m21_clef=<music21.clef.TrebleClef>, octave=None)
        """

        self.token_generator = token_generator
        for token in token_generator:
            self.abc_token(token)
            # The tune header ends and the tune body begins after the first
            # 'K:' Field
            if token.type == 'key':
                return

    def abc_clef(self, token: Field) -> tuple[clef.Clef | None, int | None]:
        """
        Parse a clef for key signatures according to the `abc:standard:v2.1:clefs
        <https://abcnotation.com/wiki/abc:standard:v2.1#clefs_and_transposition>`_

        This class is a subclass of Token and is used to represent a clef. Clef symbols
        indicate the pitch range and name of a staff.

        The clef definition in abc is part of the voice (V:) or key (K:) field.

        >>> from ABC2M21 import Field
        >>> th = TuneHeader()
        >>> m21_clef, octave = th.abc_clef(
        ...         Field("Voice", "V:1 clef=treble octave=-2"))
        >>> m21_clef
        <music21.clef.TrebleClef>
        >>> octave
        -2
        >>> th.abc_clef(Field('key', "K:C clef=bass"))
        (<music21.clef.BassClef>, None)
        >>> th.abc_clef(Field("Voice","V:1 octave=2"))
        (None, 2)
        """

        _NAMES = ['treble', 'treble8vb', 'treble8va', 'bass', 'bass8va',
                  'bass8vb', 'mezzosoprano', 'soprano', 'c baritone', 'alto',
                  'tenor', 'percussion', 'g1', 'g2', 'f3', 'f4', 'f5', 'c1',
                  'c2', 'c3', 'c4']

        _ALIAS = {
            'perc': 'percussion',
            'treble-8': 'treble8vb',
            'treble+8': 'treble8va',
            'bass-8': 'bass8vb',
            'bass+8': 'bass8va',
            'alto1': 'soprano',
            'alto2': 'mezzosoprano',
            'bass3': 'c baritone',
        }
        octave: int | None = None

        name = None
        unamed = []
        for m in ABC_CLEF_RE.finditer(token.data):
            k = m.lastgroup
            v = m.group()
            match k:
                case 'name':
                    name = v.split('=', maxsplit=1)[1].strip('"').strip()
                case 'octave':
                    octave = int(v.split('=', maxsplit=1)[1])
                case 'unamed':
                    unamed.append(v.lower().strip())

        # To support legacy usage:
        # The clef= prefix may be omitted for named clefs (e.g. treble, bass, alto)
        # although its use is recommended for clarity.
        if name is None:
            for tag in unamed:
                if tag in _NAMES:
                    name = tag
                elif tag in _ALIAS:
                    name = _ALIAS[tag]

        if name in _ALIAS:
            name = _ALIAS[name]
        elif name not in _NAMES:
            name = None

        if name:
            return clef.clefFromString(name), octave
        else:
            return None, octave

    def default_unit_note_length(self) -> float:
        ts = self.time_signature
        if ts is None or (ts.barDuration.quarterLength / ts.denominator) >= 0.75:
            return 0.5
        else:
            return 0.25

    def abc_tempo(self, token: Field) -> tempo.MetronomeMark | None:
        """
        Process a tempo field token according to the `abc:standard:v2.1:tempo
        <https://abcnotation.com/wiki/abc:standard:v2.1#qtempo>`_

        Tempo fields specify the tempo and beats per minute for a section of the music.

        Args:
            token (Field): The instruction token to process.

        Examples:

        Q:1/2=120 means 120 half-note beats per minute.

        >>> from ABC2M21 import Field
        >>> th = TuneHeader()
        >>> th.abc_tempo(Field('tempo', 'Q:1/2=120'))
        <music21.tempo.MetronomeMark Half=120>

        There may be up to 4 beats in the definition

        >>> th.abc_tempo(Field('tempo', 'Q:1/4 3/8 1/4 3/8=40'))
        <music21.tempo.MetronomeMark Whole tied to Quarter (5 total QL)=40>

        The tempo definition may be preceded or followed by an optional text
        string, enclosed by quotes

        >>> th.abc_tempo(Field('tempo', 'Q: "Allegro" 1/4=120'))
        <music21.tempo.MetronomeMark Allegro Quarter=120>
        >>> th.abc_tempo(Field('tempo', 'Q: 3/8=50 "Slowly"'))
        <music21.tempo.MetronomeMark Slowly Dotted Quarter=50>

        It is acceptable to provide a string without specifying an explicit tempo

        >>> th.abc_tempo(Field('tempo', 'Q:"Allegro"'))
        <music21.tempo.MetronomeMark Allegro Quarter=132>

        Earlier versions of the standard allowed two now deprecated syntax
        variants specifying the number of unit note lengths to play per minute.

        >>> th.abc_unit_note_length(Field('unit_note_length', 'L:1/4'))
        1.0
        >>> th.abc_tempo(Field('tempo', 'Q:120'))
        <music21.tempo.MetronomeMark Quarter=120>

        >>> th.abc_tempo(Field('tempo', 'Q:C=120'))
        <music21.tempo.MetronomeMark Quarter=120>

        >>> th.abc_tempo(Field('tempo', 'Q:C3=120'))
        <music21.tempo.MetronomeMark Dotted Half=120>
        """
        from fractions import Fraction
        text: str = ''
        referent: float = 0.0
        number: int = 0

        data = token.data
        if m := ABC_RE_TEMPO.match(data):
            for group in m.groups():
                if not group:
                    continue
                if group.startswith('"'):
                    text = group.strip('"')
                elif group.isdigit():
                    try:
                        number = int(data)
                        referent = self.quarter_length if self.quarter_length \
                            else self.default_unit_note_length()
                    except ValueError:
                        self.abc_error(f'Illegal abc tempo field syntax.', token)
                else:
                    _text, _number = group.split('=')
                    number = int(_number)
                    if _text.startswith('C'):
                        referent = self.quarter_length if self.quarter_length \
                            else self.default_unit_note_length()

                        if len(_text) > 1:
                            if _text[1:].isdigit():
                                referent *= int(_text[1:])
                            else:
                                self.abc_error(f'Illegal abc tempo field syntax.', token)
                    else:
                        referent = float(sum([Fraction(f) for f in _text.split()])) * 4
        else:
            self.abc_error(f'Illegal abc tempo field syntax.', token)

        try:
            if referent and number:
                tempo_mark = tempo.MetronomeMark(text=text, number=number, referent=referent)
            elif text:
                tempo_mark = tempo.MetronomeMark(text=text)
            else:
                return

            # Fix the placement of the metronome mark and tempo text.
            tempo_mark.placement = 'above'
            tempo_mark.style.fontStyle = 'italic'
            if tempo_mark._tempoText:
                tempo_mark._tempoText._textExpression.placement = 'above'
            self.tempo = tempo_mark
            return tempo_mark
        except Exception as e:
            self.abc_error(f'Cannot create music21 MetronomeMark', token, e)

    def abc_key(self, token: Field) -> \
            (key.KeySignature | None, clef.Clef | None, int | None):
        """
        Parse a token for key signatures according to the `abc:standard:v2.1:key
        <https://abcnotation.com/wiki/abc:standard:v2.1#kkey>`_

        Key signatures indicate the set of accidentals used in the piece, and
        may also include information about the clef and octave transposition.

        Returns:  Tuple containing the following elements:
            - Key signature as a music21.key.KeySignature object or None if not present.
            - Clef information as a music21.clef.Clef object or None if not present.
            - Octave transposition as an integer or None if not present.

        Examples:

        >>> from ABC2M21 import Field
        >>> th = TuneHeader()

        The processing of the 'key' token will consistently return a tuple
        containing information about the key signature, the clef specified, and
        the octave transposition. The handling of clef and octave details within
        this token mirrors that in the voice field.

        >>> th.abc_key(Field('key', 'K:C major treble octave=1'))
        (<music21.key.Key of C major>, <music21.clef.TrebleClef>, 1)

        The following tokens would all produce a signature with no sharps or
        flats.

        >>> ks = th.abc_key(Field('key', 'K:C major'))[0]
        >>> ks.alteredPitches
        []
        >>> ks = th.abc_key(Field('key', 'K:A minor'))[0]
        >>> ks.alteredPitches
        []
        >>> ks = th.abc_key(Field('key', 'K:C ionian'))[0]
        >>> ks.alteredPitches
        []
        >>> ks = th.abc_key(Field('key', 'K:A aeolian'))[0]
        >>> ks.alteredPitches
        []
        >>> ks = th.abc_key(Field('key', 'K:G mixolydian'))[0]
        >>> ks.alteredPitches
        []
        >>> ks = th.abc_key(Field('key', 'K:D dorian'))[0]
        >>> ks.alteredPitches
        []
        >>> ks = th.abc_key(Field('key', 'K:E phrygian'))[0]
        >>> ks.alteredPitches
        []
        >>> ks = th.abc_key(Field('key', 'K:F lydian'))[0]
        >>> ks.alteredPitches
        []
        >>> ks = th.abc_key(Field('key', 'K:B locrian'))[0]
        >>> ks.alteredPitches
        []

        The spaces can be left out, capitalisation is ignored for the modes and
        only the first three letters of each mode are parsed.

        >>> th.abc_key(Field('key', 'K:F# mixolydian'))[0]
        <music21.key.Key of F# mixolydian>
        >>> th.abc_key(Field('key', 'K:F#Mix'))[0]
        <music21.key.Key of F# mixolydian>
        >>> th.abc_key(Field('key', 'K:F#MIX'))[0]
        <music21.key.Key of F# mixolydian>

        As a special case, minor may be abbreviated to m.

        >>> th.abc_key(Field('key', 'K:Cm'))[0]
        <music21.key.Key of c minor>

        By specifying an empty K: field, or K:none you will get a
        key signature with no tonic, mode or sharps and flats

        >>> th.abc_key(Field('key', 'K:'))[0]
        <music21.key.KeySignature of pitches: []>

        >>> th.abc_key(Field('key', 'K:none'))[0]
        <music21.key.KeySignature of pitches: []>

        The key signatures may be modified by adding accidentals, according to
        the format K:<tonic> <mode> <accidentals>

        "K:D Phr ^f" would give a key signature with two flats and one sharp.

        >>> ks = th.abc_key(Field('key', 'K:D Phr ^f'))[0]
        >>> ks.alteredPitches
        [<music21.pitch.Pitch B->, <music21.pitch.Pitch E->, <music21.pitch.Pitch F#>]

        Previous key signature could also be notated as K:D exp _b _e ^f, where
        'exp' is an abbreviation of 'explicit'.

        >>> ks = th.abc_key(Field('key', 'K:D exp _b _e ^f'))[0]
        >>> ks.alteredPitches
        [<music21.pitch.Pitch B->, <music21.pitch.Pitch E->, <music21.pitch.Pitch F#>]

        The two following keys are specifically for notating highland bagpipe tunes.

        >>> th.abc_key(Field('key', 'K:HP'))[0]
        <music21.key.KeySignature of pitches: [F#, C#]>
        >>> th.abc_key(Field('key', 'K:Hp'))[0]
        <music21.key.KeySignature of pitches: []>

        You can add clef specifiers to the K: field, with or without a key
        signature, to change the clef and various other staff properties, such
        as octave transposition.

        >>> th.abc_key(Field('key', 'K: C clef=bass'))
        (<music21.key.Key of C major>, <music21.clef.BassClef>, None)
        >>> th.abc_key(Field('key', 'K: clef=treble octave=-1'))
        (None, <music21.clef.TrebleClef>, -1)
        """
        key_field_str = token.data

        def abc2m21_note(abc) -> str:
            accidental = NoteMixin.abc_accidental(abc[:-1])
            return f"{abc[-1].upper()}{accidental}"

        if match := ABC_KEY_EXP_RE.match(key_field_str):
            # <tonic> exp <accidentals>
            match = match.groupdict()
            ks = key.KeySignature(sharps=None)
            ap = [abc2m21_note(n) for n in match['accidentals'].strip().split()]
            ks.alteredPitches = ap
        elif match := ABC_KEY_MODE_RE.match(key_field_str):
            match = match.groupdict()
            _mode = match['mode'].lower()[:3]
            if _mode == 'm':
                _mode = 'minor'
            elif not _mode:
                _mode = 'major'

            # in abc only the first 3 letters of a mode are relevant
            mode = ABC_MODES.get(_mode[:3], None)
            if mode:
                tonic = key.convertKeyStringToMusic21KeyString(match['tonic'])
                ks = key.Key(tonic, mode)
                if match['accidentals']:
                    # create a mapping between pitch class name (step) and accidental
                    altered_pitches = {p.step: p.accidental.modifier for p in ks.alteredPitches}
                    # override key signature accidentals with explicit accidentals
                    # from the abc key field
                    for n in match['accidentals'].strip().split():
                        pitch_str = abc2m21_note(n)
                        altered_pitches[pitch_str[0]] = pitch_str[1:]

                    # Set alteredPitches of the KeySignature
                    ks.alteredPitches = [f"{p}{a}" for p, a in altered_pitches.items()]
            else:
                self.abc_error(f"Unknown mode '{mode}' in ABC Key field.", token)
                ks = None

        elif key_field_str == "HP":
            ks = key.KeySignature(sharps=None)
            ks.alteredPitches = ["F#", 'C#']
        elif key_field_str == "Hp":
            ks = key.KeySignature(sharps=None)
        elif not key_field_str or key_field_str == 'none':
            # an empty key field or 'none'
            ks = key.KeySignature(sharps=None)
        else:
            ks = None

        if ks:
            self.key_signature = ks

        # the abc key filed may define a clef and an octave transposition
        m21_clef, octave = self.abc_clef(token)

        if octave is not None:
            self.octave = octave
        if m21_clef is not None:
            self.clef = m21_clef

        return ks, m21_clef, octave

    def abc_part(self, token: Field):
        """
        voices in the header represent the arrangement of sections in the tune.
        In this context part refers to a section of the tune, rather than a voice
        in multi-voice music.

        The tune voices are played, i.e. P:ABABCDCD, and then inside the tune body
        to mark each part, i.e. P:A or P:B.

        Args:
            token (Field): The part token to be processed.

        The part sequence will be stored in self.section_sequence

        Examples:

        >>> from ABC2M21 import Field
        >>> processor = TuneHeader()
        >>> processor.abc_part(Field('Section', 'P: A2BC'))
        >>> processor.section_sequence
        'AABC'
        """

        result = []
        data = token.data
        for char in ABC_RE_voices.findall(data.replace('.', ' ')):
            if char.isdigit():
                result.append("*")
            elif char != ')' and result and result[-1] != '(':
                result.append("+")
            if char.isalpha():
                char = f"'{char}'"

            result.append(char)

        # The use of eval is safe here.
        # It only performs addition and multiplication operations between strings and integers.
        self.section_sequence = eval("".join(result))

    def abc_voice(self, token: Field) -> \
            (str, clef.Clef | None, int | None):
        """
        Process the ABC voice field token and return relevant information
        for a Music21 Part.
        The V: field allows the writing of multi-voice music. In multi-voice
        abc tunes, the tune body is divided into several voices, each beginning
        with a V: field. All the notes following such a V: field, up to the next
        V: field or the end of the tune body, belong to the voice.

        V: can appear both in the body and the tune header. In the latter case, V:
        is used exclusively to set voice properties.

        Args:
         token (Field): The token representing an ABC Voice field.

        Returns:
         Tuple[str, Optional[clef.Clef], Optional[int]]: A tuple containing the part ID,
         clef information, and octave information.
        """
        data = token.data
        splitter = data.split(maxsplit=1)

        if not splitter:
            self.abc_error('Ignore abc voice field without voice id.', token)
            return None, None, None

        voice_id = splitter[0][:20]

        name, subname, stem, m21_clef, octave = None, None, None, None, None

        if len(splitter) > 1:
            m21_clef, octave = self.abc_clef(token)

            for m in ABC_VOICE_RE.finditer(splitter[1]):
                k = m.lastgroup.lower()
                if not (v := m.group().split('=')[1].strip().strip('"')):
                    continue
                match k:
                    case 'name':
                        name = v
                    case 'subname':
                        subname = v
                    case 'stem':
                        v = v.lower()
                        if v not in ['up', 'down']:
                            self.abc_error(f'Illegal value "{stem}" for the voice'
                                           'property stem (up/down)', token)
                        else:
                            stem = v

        if voice_id not in self.voice_info:
            # If the part is not yet known
            # Create a PartInfo for the part
            self.voice_info[voice_id] = VoiceInfo(
                voice_id=voice_id,
                stem=stem,
                m21_clef=m21_clef,
                octave=octave,
                name=name,
                sub_name=subname
            )
        else:
            # Otherwise, update the VoiceInfo of the voice with the
            # information found in the token
            info: VoiceInfo = self.voice_info[voice_id]
            if name is not None:
                info.name = name
            if subname is not None:
                info.sub_name = subname
            if stem is not None:
                info.stem = stem
            if m21_clef is not None:
                info.m21_clef = m21_clef
            if octave is not None:
                info.octave = octave

        return voice_id, m21_clef, octave


class ABCOverlay(ABCObject):
    def __init__(self):

        self.stream: None = None

        self.courtesy: bool = False

        # We remember the grace note until we find a target note.
        # We want to slur the first grace note to the target note,
        # and we need the target note to calculate the grace duration.
        self.grace_notes: list[note.GeneralNote] = []

        self.auto_trill_spanner: expressions.TrillExtension | note.GeneralNote | None = None
        self.is_trill = False

        # remember the last inserted note token in this voice
        self.last_note: note.GeneralNote | None = None

        # remember the duration modifier of the last broken rhythm
        self.broken_rhythm: tuple[float, float] | None = None

        # store for an open tuplet in this voice
        self.tuplet: list[duration.Tuplet] = []

        # store articulation Tokens for the next Note  in this voice
        self.articulations: list[articulations] = []

        # store expression Tokens for the next Note in this voice
        self.expressions: list[expressions.Expression] = []

        # Stack for open spanners in this voice
        self.open_spanner: list[spanner.Spanner] = []

        # accidental of the next note is a ficta accidental
        self.ficta: bool = False

        self.decorations: list[music21.Music21Object] = []

    def get_last_tied_note(self, m21_note: note.Note) -> note.Note | None:
        if self.last_note:
            if isinstance(self.last_note, note.Note):
                if self.last_note.tie and self.last_note.nameWithOctave == m21_note.nameWithOctave:
                    if self.last_note.tie.type != 'stop':
                        return self.last_note
            elif isinstance(self.last_note, chord.Chord):
                for chord_note in self.last_note.notes:
                    if chord_note.tie and chord_note.nameWithOctave == m21_note.nameWithOctave:
                        if self.last_note.tie.type != 'stop':
                            return chord_note

    def cleanup_ties(self, notes: list[note.Note]):
        if self.last_note:
            if isinstance(self.last_note, note.Note):
                last_notes = [self.last_note]
            elif isinstance(self.last_note, chord.Chord):
                last_notes = self.last_note.notes
            else:
                return

            for last_note in last_notes:
                if last_note.tie is None or last_note.tie.type == 'stop':
                    continue
                if any(last_note.nameWithOctave == _note.nameWithOctave for _note in notes):
                    continue

                if last_note.tie.type == 'continue':
                    last_note.tie.type = 'stop'
                else:
                    self.abc_error("The previous note cannot be tied to a subsequent note.")
                    last_note.tie = None

    def append(self, m21_object: music21.Music21Object):
        self.stream.append(m21_object)

    def apply_tuplet(self, general_note: note.GeneralNote):
        if self.tuplet:
            m21_tuplet = deepcopy(self.tuplet[-1])
            self.tuplet.pop()

            if m21_tuplet.durationNormal is None:
                m21_tuplet.setDurationType(general_note.duration.type,
                                           general_note.duration.dots)

            general_note.duration.appendTuplet(m21_tuplet)

    def close_auto_trill_spanner(self):
        if len(self.auto_trill_spanner.spannerStorage) == 1:
            general_note = self.auto_trill_spanner.spannerStorage.first()
            general_note.expressions.append(expressions.Trill())

        elif isinstance(self.auto_trill_spanner, expressions.TrillExtension):
            self.auto_trill_spanner.completeStatus = True

        self.is_trill = False
        self.auto_trill_spanner = None

    def apply_auto_trill_spanner(self, general_note: note.GeneralNote) -> expressions.TrillExtension | None:
        if self.is_trill:
            # Create a trill extension spanner for continues trill notes
            if self.auto_trill_spanner is None:
                self.auto_trill_spanner = expressions.TrillExtension()

            # Add recent note to the spanner
            self.auto_trill_spanner.addSpannedElements(general_note)
            self.is_trill = False

            # Once the trill spanner has two notes, it is permanent
            # return the spanner to get inserted into the part stream
            if len(self.auto_trill_spanner.spannerStorage) == 2:
                return self.auto_trill_spanner

        elif self.auto_trill_spanner:
            self.close_auto_trill_spanner()
            return

    def apply_decorations(self, general_note: note.GeneralNote):
        # add note/chord/rest to the open spanner of this context
        for m21_spanner in self.open_spanner:
            m21_spanner.addSpannedElements(general_note)

        # Transfer the previously collected expressions from the context to the
        # note/chord.
        general_note.expressions = self.expressions
        self.expressions = []

        # Transfer the previously collected articulations to the note/chord.
        general_note.articulations = self.articulations
        self.articulations = []

        for element in self.decorations:
            self.stream.append(element)

        self.decorations = []

        #  Fict accidental
        if self.ficta:
            general_note.editorial.ficta = pitch.Accidental(self.ficta)
            self.ficta = None

    def apply_broken_rhythm(self, general_note: note.GeneralNote):
        # Apply duration modifications of a broken rhythm
        if self.broken_rhythm:
            left_mod, right_mod = self.broken_rhythm
            self.broken_rhythm = None
            self.last_note.quarterLength *= left_mod
            self.stream.coreElementsChanged()
            general_note.quarterLength *= right_mod

    def close_spanner(self):
        if self.open_spanner:
            self.open_spanner[-1].completeStatus = True
            self.open_spanner.pop()

    def close(self):

        self.cleanup_ties([])

        while self.open_spanner:
            self.abc_error(f"Close {len(self.open_spanner)} unclosed spanner.")
            self.close_spanner()

        if self.auto_trill_spanner:
            self.close_auto_trill_spanner()

        if self.articulations:
            self.abc_error(f"Remove {len(self.articulations)} unassigned articulations")
            self.articulations = []

        if self.expressions:
            self.abc_error(f"Remove {len(self.expressions)} unassigned expressions")
            self.articulations = []

        if self.ficta:
            self.abc_error("Remove unassigned editorial/dicta")
            self.ficta = False

        if self.tuplet:
            self.abc_error(f"Remove incomplete {len(self.tuplet)} tuplet(s)")
            self.tuplet = []

        if self.broken_rhythm:
            self.abc_error("Remove unfinished broken rhythm")
            self.broken_rhythm = None

        if self.grace_notes:
            # grace notes without target note are legal?!
            self.grace_notes = []

        self.decorations: list[music21.Music21Object] = []
        self.last_note = None

        if self.auto_trill_spanner:
            self.auto_trill_spanner = None


class ABCVoice(ABCObject):

    def __init__(self, voice_id: str | None,
                 m21_clef: clef.Clef | None = None,
                 octave: int = 0):

        self.voice_id: str | None = voice_id
        self.part: stream.Part = stream.Part(id=voice_id)

        # Part stream objekt of this context
        # carried accidentals in this voice
        self.carried_accidentals: dict = {}

        # Remember a clef token to insert in the next measure
        self.clef: clef.Clef | None = m21_clef
        self.octave: int = octave

        self.lyrics: list = []
        self.lyric_bar_count: int = 0

        # last measure of the part in this context
        self.stream: stream.Measure | None = None
        self.repeat_bracket: spanner.RepeatBracket | None = None
        self.overlay: ABCOverlay = ABCOverlay()
        self._overlays: list[ABCOverlay] = [self.overlay]

    def apply_grace_notes(self, general_note: note.GeneralNote):

        if self.overlay.grace_notes:
            # Add the grace notes and this note to a Slur Spanner
            slur = spanner.Slur(self.overlay.grace_notes)
            slur.addSpannedElements(general_note)
            self.part.insert(0, slur)
            # Insert the grace notes to the overlay
            if self.overlay.grace_notes:
                for gn in self.overlay.grace_notes:
                    self.overlay.append(gn)

            # reset the grace notes in the context
            self.overlay.grace_notes = []

    def add_spanner(self, m21_spanner: spanner.Spanner):
        self.overlay.open_spanner.append(m21_spanner)
        self.part.insert(0, m21_spanner)

    # def append(self, m21_object: music21.Music21Object):
    #    self.stream.append(m21_object)

    def split_measure(self, quarterLength: float):
        splits = self.stream.splitAtQuarterLength(quarterLength)
        self.part.remove(self.stream)
        for measure in splits:
            self.stream = measure
            self.part.append(measure)

    def next_overlay(self) -> ABCOverlay:
        n = len(self.stream.getElementsByClass(stream.Voice))
        if len(self._overlays) <= n:
            self.abc_error(f'Create Overlay #{n} context in voice: {self.voice_id}')
            self._overlays.append(ABCOverlay())

        self.overlay = self._overlays[n]
        self.overlay.stream = stream.Voice()
        self.stream.insert(0, self.overlay.stream)
        self.carried_accidentals = {}
        return self.overlay

    def open_repeat_bracket(self, number: int):
        if self.repeat_bracket:
            self.abc_error('Close still open repeat braket.')
            self.close_repeat_bracket()

        self.repeat_bracket = spanner.RepeatBracket(self.stream)
        self.repeat_bracket.number = number
        self.repeat_bracket.completeStatus = False
        self.part.insert(0, self.repeat_bracket)

    def close_repeat_bracket(self):
        assert (self.repeat_bracket is not None)
        self.repeat_bracket.completeStatus = True
        self.repeat_bracket = None

    def close_measure(self, time_signature: meter.TimeSignature, bar_line: bar.Barline | None = None):

        assert self.stream is not None, "No open measure in the active context to close found"
        assert self.stream.quarterLength > 0, 'Closing an empty measure!'
        # Split a measure if the measure length is greater than the measure
        # length of the given time signature
        if time_signature is not None:
            measures = self.part.getElementsByClass(stream.Measure)
            if len(measures) == 1:
                measures[0].timeSignature = time_signature

            time_sig_length = time_signature.barDuration.quarterLength
            if self.stream.quarterLength > time_sig_length:
                self.split_measure(time_sig_length)

        # set the closing barline i the measure
        self.stream.rightBarline = bar_line if bar_line else bar.Barline()

        self.carried_accidentals = {}

        # Remove the measure reference from the context
        self.stream = None
        self.overlay.stream = None

        # Set the overlay context to the first overlay
        self.overlay = self._overlays[0]

    def open_measure(self,
                     bar_line: bar.Barline | None = None,
                     key_signature: key.KeySignature | None = None
                     ):

        # Assign collected lyric lines to the last measures
        if self.lyrics:
            self.align_lyrics()

        assert self.stream is None, \
            f"Last measure of active part '{self.voice_id}' is still open!"

        # Create a new measure with one Voices (ABC Overlay)
        measure = stream.Measure()

        # For the first measure in this context, add recent clef,
        # key signature and meter
        if not self.part.getElementsByClass(stream.Measure):
            if self.clef:
                measure.clef = self.clef
            if key_signature:
                measure.keySignature = key_signature

        # Add the left bar line for the open measure
        if bar_line:
            assert not (isinstance(bar_line, bar.Repeat) and bar_line.direction == 'end'), \
                f"Cannot open a measure with a closing repeat bar line"
            measure.leftBarline = bar_line

        # add the measure to an open repeat bracket spanner
        if self.repeat_bracket:
            self.repeat_bracket.addSpannedElements(measure)

        # set active measure in the context
        self.stream = measure
        self.overlay = self._overlays[0]
        self.overlay.stream = stream.Voice()
        self.stream.insert(0, self.overlay.stream)
        self.part.append(measure)

    def close(self):

        if self.lyrics:
            self.align_lyrics()

        for context in self._overlays:
            context.close()

        if self.repeat_bracket:
            self.abc_error("Close unclosed repeat bracket.")
            self.close_repeat_bracket()

    def align_lyrics(self):
        # start aligning syllable to notes of the first Overlay/Voice
        measures = list(self.part.getElementsByClass(stream.Measure))
        is_in_word: bool = False
        for syllables in self.lyrics:
            for measure in measures[self.lyric_bar_count:]:
                overlay_notes = iter(measure.getElementsByClass(stream.Voice).first().notes)
                for _note in overlay_notes:
                    if syllables and syllables[0] == '|':
                        syllables.pop(0)
                        for no_lyric_note in overlay_notes:
                            _note.lyrics.append(
                                note.Lyric(number=len(no_lyric_note.lyrics), text='')
                            )
                        break

                    if syllables:
                        syllable = syllables[0]
                        syllables.pop(0)
                    else:
                        _note.lyrics.append(
                            note.Lyric(number=len(_note.lyrics), text='')
                        )
                        continue

                    match syllable:
                        case '_' | '-' | '*':
                            # previous syllable is to be held for an extra note
                            _note.lyrics.append(
                                note.Lyric(number=len(_note.lyrics), text='')
                            )
                        case '\\-':
                            # @TODO: appears as hyphen; aligns multiple syllables under one note
                            continue
                        case _:
                            if syllable.endswith('-'):
                                if is_in_word:
                                    syllabic: note.SyllabicChoices = "middle"
                                else:
                                    syllabic: note.SyllabicChoices = "begin"
                                    is_in_word = True
                            else:
                                if is_in_word:
                                    syllabic: note.SyllabicChoices = "end"
                                    is_in_word = False
                                else:
                                    syllabic: note.SyllabicChoices = "single"

                            _note.lyrics.append(
                                note.Lyric(number=len(_note.lyrics), text=syllable, syllabic=syllabic)
                            )
                else:
                    if syllables and syllables[0] == '|':
                        syllables.pop(0)

        self.lyric_bar_count = len(measures)
        self.lyrics = []


class NoteMixin:

    def __init__(self):
        self.voice: ABCVoice | None = None
        self.key_signature: key.KeySignature | None = None
        self.accidental_mode: str = 'not'
        self.time_signature: meter.TimeSignature | None = None

    @abstractmethod
    def abc_error(self, message: str, token: Token = None, exception=None):
        pass

    def abc_note(self, token: Token) -> note.Note:
        """
         Parses an ABC notation note string and returns a music21 Note object.

         Returns:
             note.Note: A music21 Note object representing the parsed note.
         """
        if not (match := ABC_RE_ABC_NOTE.match(token.src)):
            # Check the regular expression; this shouldn't happen.
            raise ABCException(f"String '{token.src}' is not an ABC note.")

        # ABC pitches are case-sensitive, indicating an octave.
        pitch_name = match.group(2)
        octave: int = self.voice.octave + (5 if pitch_name.islower() else 4)
        pitch_name: common.types.StepName = pitch_name.upper()

        if m := match.group(3):
            octave = octave - m.count(',') + m.count("'")

        # the abc accidental of the note
        accidental = self.abc_accidental(match.group(1))
        implicit_accidental = None

        # Handle carried accidentals
        if (carried_accidentals := self.voice.carried_accidentals) is not None:
            if accidental:
                # Remember the active accidentals in the measure
                if self.accidental_mode == 'pitch':
                    carried_accidentals[pitch_name] = accidental
                elif self.accidental_mode == 'octave':
                    carried_accidentals[(pitch_name, octave)] = accidental
            else:
                if self.accidental_mode == 'pitch' and pitch_name in carried_accidentals:
                    implicit_accidental = carried_accidentals[pitch_name]
                elif self.accidental_mode == 'octave' and (pitch_name, octave) in carried_accidentals:
                    implicit_accidental = carried_accidentals[(pitch_name, octave)]

        if implicit_accidental is None and (acc := self.key_signature.accidentalByStep(pitch_name)):
            # Determine the implicit accidental based on the key signature
            implicit_accidental = acc.modifier

        if implicit_accidental:
            if not accidental or accidental == implicit_accidental:
                # If note has no explicit accidental or both explicit and implicit
                # accidentals are equal the use the implicit accidental but don't
                # display them in the score.
                accidental, display = implicit_accidental, False
            else:
                # Display the explicit accidental in the score and ignore the implicit one.
                accidental, display = accidental, True
        else:
            if accidental:
                # We have an explicit accidental but no implicit accidental,
                # display the explicit accidental in the score.
                accidental, display = accidental, True
            else:
                # No accidentals at all.
                accidental, display = '', None

        m21_note = note.Note(f"{pitch_name}{accidental}{octave}")

        if m := match.group(4):
            try:
                length_modifier = self.abc_length(m)
            except ABCException as e:
                self.abc_error("Fallback to note length modifier '1.0'.", token, e)
                length_modifier = 1.0
        else:
            length_modifier = 1.0

        m21_note.quarterLength = length_modifier

        if accidental:
            m21_note.pitch.accidental.displayStatus = display
            if self.voice.overlay.courtesy:
                m21_note.pitch.accidental.displayStyle = 'parentheses'

        if match.group(5):
            m21_note.tie = tie.Tie('start')

        return m21_note

    def abc_tuplet(self, token: Token) -> list[duration.Tuplet]:
        """
        Parses an ABC tuplet token and returns a list with multiples references
        to music21 duration. Tuplet objects, one for each note of the tuplet.

        Args:
          token: The token representing an ABC tuplet.

        Returns:
          List[duration.Tuplet]: A list of references to the music21 duration.Tuplet objects.

        """
        parts = token.src.strip().split(':')
        p = int(parts[0][1:])
        r = int(parts[2]) if len(parts) >= 3 and parts[2] else p

        if len(parts) >= 2 and parts[1]:
            q = int(parts[1])
        else:
            # it is automatically determined based on the meter.  If the meter
            # is compound, q is set to 3; otherwise, it is set to 2.
            s = 3 if self.time_signature and self.time_signature.beatDivisionCount == 3 else 2
            q = (1, 3, 2, 3, s, 2, s, 3, s)[p - 1]

        m21_tuplet = duration.Tuplet(p, q)
        return [m21_tuplet] * r

    def abc_length(self, src: str) -> float:
        """
        Parses an ABC notation note/rest/chord length string and returns the
        length modifier as a float.

        https://abcnotation.com/wiki/abc:standard:v2.1#lunit_note_length

        Args:
            src (str): The ABC notation length string.

        Returns:
            float: The length modifier as a float.
        """


        denominator: int = 1
        while src.endswith('/'):
            denominator *= 2
            src = src[:-1]

        if not src:
            return 1.0 / denominator

        try:
            numerator = 1.0
            if src.startswith('/'):
                # common usage: /4 short for 1/4
                denominator = int(src.lstrip('/'))
            elif '/' in src:
                # common usage: 3/4
                n, d = src.split('/')
                numerator, denominator = int(n), int(d)
            elif src.isdigit():
                numerator = int(src)

            return numerator / denominator

        except ValueError:
            raise ABCException(f'Incorrectly encoded or unparsable duration.')


    @staticmethod
    def abc_accidental(src: str) -> str:
        """
        Parses an ABC notation accidental string and returns the corresponding
        music21 accidental symbol.

        Args:
           src (str): The ABC notation accidental string.

        Returns:
           str: The corresponding accidental symbol.

        Example:
        >>> np = NoteMixin
        >>> np.abc_accidental('^')
        '#'

        >>> np.abc_accidental('_')
        '-'

        >>> np.abc_accidental('=')
        'n'

        >>> np.abc_accidental('^=')
        'n'

        >>> np.abc_accidental('^^_')
        '#'
        """
        if src:
            voices = src.split('=')
            if len(voices) > 1 and not voices[-1]:
                return 'n'
            elif accidental := voices[-1]:
                sharps = accidental.count('^') - accidental.count('_')
                return '#' * sharps if sharps > 0 else '-' * (-sharps)
        else:
            return ''

    def abc_broken_rhythm(self, token: Token):
        """
        Process a BrokenRhythm token according to the `abc:standard:v2.1:broken_rhythm
        <https://abcnotation.com/wiki/abc:standard:v2.1#broken_rhythm>`_

        Broken rhythm indications are used to modify the timing of notes or groups of notes.
        """
        left_mod, right_mod = {'>': (1.5, 0.5),
                               '>>': (1.75, 0.25),
                               '>>>': (1.875, 0.125),
                               '<': (0.5, 1.5),
                               '<<': (0.25, 1.75),
                               '<<<': (0.125, 1.875)
                               }.get(token.src, (1, 1))

        return (left_mod, right_mod)


class TuneBody(TuneHeader, NoteMixin):
    def __init__(self, tune_header: TuneHeader):
        super().__init__(abc_version=tune_header.abc_version)

        # Create a music21 Score for the Tune
        self.score: stream.Score = stream.Score()

        self.metadata = tune_header.metadata
        self.score.append(self.metadata)

        self.clef = tune_header.clef or clef.TrebleClef()
        self.octave = tune_header.octave
        self.token_generator = tune_header.token_generator

        if tune_header.key_signature:
            self.key_signature = tune_header.key_signature
        else:
            self.abc_error(f"No valid key signature, default to 'C major'")
            self.key_signature = key.Key('C')

        self.time_signature = tune_header.time_signature
        self.user_defined = tune_header.user_defined
        self.tempo = tune_header.tempo
        self.accidental_mode = tune_header.accidental_mode
        self.section_sequence = [c for c in tune_header.section_sequence]
        self.voice_info = tune_header.voice_info

        self.linebreak = tune_header.linebreak
        self.is_legacy_abc_decoration = tune_header.is_legacy_abc_decoration
        self.is_legacy_abc_chord = tune_header.is_legacy_abc_chord
        self.midi = tune_header.midi
        self.staves = tune_header.staves

        # if the unit note length is not set then initialize it
        # based on the meter.
        if tune_header.quarter_length:
            self.quarter_length: float = tune_header.quarter_length
        else:
            self.quarter_length: float = self.default_unit_note_length()

        # Store ABCVoiceContext in a dictionary by section id and voice id.
        self.sections: dict[str | None, dict[str | None, ABCVoice]] = {
            None: {None: ABCVoice(m21_clef=self.clef, octave=self.octave, voice_id=None)}
        }

        # Because sections may be played in any order, we need to remember the
        # tempo of each section.
        self.section_tempo: dict[str | None, tempo.MetronomeMark] = {None: self.tempo}
        self.part: dict[str | None, ABCVoice] = self.sections[None]
        self.voice: ABCVoice = self.part[None]

    def close_part(self):
        for context in self.part.values():
            context.close()

    def voice_grouping(self):
        score_instruction: ScoreInstruction
        if not self.staves:
            return

        # Insert voices in a bracketed staff group.
        for group in self.staves.bracket:
            if len(group) < 2:
                continue
            self.score.insert(0, layout.StaffGroup(
                [part for part in self.score.getElementsByClass(stream.Part) if part.id in group],
                symbol='bracket'))

        for group in self.staves.brace:
            if len(group) < 2:
                continue
            self.score.insert(0, layout.StaffGroup(
                [part for part in self.score.getElementsByClass(stream.Part) if part.id in group],
                symbol='brace'))

        for group in self.staves.square:
            if len(group) < 2:
                continue
            self.score.insert(0, layout.StaffGroup(
                [part for part in self.score.getElementsByClass(stream.Part) if part.id in group],
                symbol='square'))

        for group in self.staves.continued_bar_lines:
            self.score.insert(0, layout.StaffGroup(
                [part for part in self.score.getElementsByClass(stream.Part) if part.id in group],
                barTogether=True))

    def apply_midi(self, m21_part: stream.Part, index: int = 0):
        if midi := self.midi:
            if program := midi.get(m21_part.id, midi.get(index, None)):
                m21_part.insert(
                    0,
                    instrument.instrumentFromMidiProgram(program)
                )

    def combine_abc_parts(self) -> Iterator[stream.Part]:

        # Initially, we'll ensure all voices in this abc part are the same
        # length by adding empty measures if necessary.
        self.fix_part_lengths()

        section_sequence: str | list = self.section_sequence or list(self.sections.keys())

        # keep track of used parts objekts
        multiple_parts = set()

        # The id of the first part (top on the score)
        first_part = None

        voice_order = self.voice_order()
        for voice_id in voice_order:
            if voice_info := self.voice_info.get(voice_id, None):
                combined_part = stream.Part(id=voice_id)
                combined_part.partName = voice_info.name
                combined_part.partAbbreviation = voice_info.sub_name
            else:
                combined_part = stream.Part()

            for part_id in section_sequence[:]:
                section = self.sections[part_id]
                if ctx := section.get(voice_id, None):
                    # We need to create a deepcopy when a part object is used
                    # multiple times. To avoid creating a deepcopy each time,
                    # we keep track of the parts that have already been used.
                    # We only create a deepcopy when the part is actually needed again.
                    if ctx.part.id in multiple_parts:
                        m21_part = deepcopy(ctx.part)
                    else:
                        m21_part = ctx.part
                        multiple_parts.add(ctx.part.id)

                    if (first_measure := m21_part.getElementsByClass(stream.Measure).first()) is None:
                        self.abc_error(f"Skip empty voice: {voice_id}")
                        continue

                    if first_part is None:
                        first_part = m21_part

                    if m21_part.id == first_part.id:
                        if _tempo := self.section_tempo[part_id]:
                            first_measure.insert(0, _tempo)

                        # Insert a TextMark for the Part ID (except the anonymous Part (id=None))
                        if part_id:
                            label = expressions.TextExpression(content=part_id)
                            label.placement = 'above'
                            label.enclosure = style.Enclosure.SQUARE
                            first_measure.insert(0, label)

                    # Kopieren Sie die Elemente aus part2 in part1
                    for element in m21_part.elements:
                        combined_part.append(element)

            if combined_part.quarterLength > 0:
                try:
                    first_measure: stream.Measure = combined_part.getElementsByClass(stream.Measure).first()
                    if first_measure.timeSignature and first_measure.barDurationProportion() < 1.0:
                        first_measure.padAsAnacrusis()
                except Exception as e:
                    self.abc_error(
                        f"Error while analyzing an anacrusis in the part: {combined_part.id}",
                        exception=e)

                yield combined_part

    def set_context(self, voice_id: str | None):
        """
        Change the active abc voice in the processor.
        From now on, all Music21 objects, such as notes and measures,
        will be inserted into the active part.
        """
        m21_clef, octave = None, None

        if voice_id not in self.part:
            # This voice is not yet known in the active section.
            if voice_info := self.voice_info.get(voice_id, None):
                # However, there is already information about this voice
                # from the tune header or previously notated abc voice fields.
                m21_clef = voice_info.m21_clef
                octave = voice_info.octave

            # Create an ABCVoiceContext in the active section for this voice.
            self.part.update({
                voice_id: ABCVoice(voice_id=voice_id,
                                   m21_clef=m21_clef or self.clef,
                                   octave=octave or self.octave)
            })

        self.voice = self.part[voice_id]

    def abc_overlay(self, token: Token):
        """
        Process an abc voice overlay token according to the
        `abc:standard:v2.1:voice_overlay
        <https://abcnotation.com/wiki/abc:standard:v2.1#voice_overlay>`_.

        The & operator may be used to temporarily overlay several voices within
        one measure.

        Args:
            token (Token): The token representing an ABC voice overlay.
        """

        assert self.voice.stream is not None, "Cannot append overlay, the measure is already closed"
        self.voice.next_overlay()

    def abc_lyrics(self, token: Field):
        """
        Parse a lyrics field token according `abc:standard:lyrics
        <https://abcnotation.com/wiki/abc:standard:v2.1#lyrics>`_

        Lyrics fields provide text annotations that correspond to specific
        notes in the music.

        The lyrics field can contain various special characters such as '*',
        '-',  and '|', which are used for rhythmic alignment.

        If '-' is preceded by a space or another hyphen, the '-' is regarded as
        a separate syllable.

        The processed lyrics are stored in the active context until the next
        measure is closed.
        """

        # Append a new lyric line to the active voice
        _RE_ABC_LYRICS = re.compile(r'[*\-_|]|[^*\-|_ ]+[\-]?')
        syllables = [s.replace('~', ' ') for s in _RE_ABC_LYRICS.findall(token.data)]
        self.voice.lyrics.append(syllables)

    def abc_chord_symbol(self, token: Token):
        """
        Process a chord symbol token in ABC notation.

        Chord symbols provide harmonic annotations to the melody.
        """
        name = re.sub(r'[\[\]]', '', token.src.strip('"'))
        name = common.cleanedFlatNotation(name)
        try:
            if token.src.upper() in ('NC', 'N.C.', 'NO CORD', 'NONE'):
                cs = harmony.NoChord(name)
            else:
                cs = harmony.ChordSymbol(name)
            self.voice.overlay.decorations.append(cs)
        except Exception as e:
            self.abc_error(f'Chord symbol is malformed.', token, e)

    def abc_grace_notes(self, token: Token):
        """
        This method processes the internal structure of the GraceNotes token
        and stores the resulting grace notes in the active context to be
        associated with the main note.

        Args:
            token: The token representing ABC GraceNotes.
        """
        if self.voice.stream is None:
            self.voice.open_measure(key_signature=self.key_signature)

        intern = token.src[1:-1]
        slash = intern.startswith('/')
        if slash:
            intern = intern[1:]

        tokens = list(tokenize(intern, abc_version=self.abc_version))

        # remember the grace notes to slur to a main note
        self.voice.overlay.grace_notes = GraceNoteParser(self).process(tokens, slash)

    def abc_key(self, token: Field):
        ks, _, _ = super().abc_key(token)

        if ks:
            if self.voice.stream is None:
                self.voice.open_measure(key_signature=self.key_signature)

            self.voice.overlay.append(self.key_signature)



    def abc_bidirectonal_barline(self, token: Token):
        """
        Process a bidirectional bar line token and split it into its
        constituent parts.

        The token is split into its constituent voices, and further processing
        is done based on the specific pattern
        """
        if token.src[-1].isdigit():

            self.abc_end_repeat_barline(
                Token('EndRepeatBarline', f'{token.src[:-2]}|',
                      pos=token.pos)
            )
            self.abc_start_repeat_barline(
                Token('StartRepeatBarline', token.src[-2:],
                      pos=token.pos + len(token.src) - 2
                      )
            )
        elif token.src.endswith('|]'):
            self.abc_end_repeat_barline(
                Token('EndRepeatBarline', token.src[:-1],
                      pos=token.pos)
            )
            self.abc_barline(
                Token('Barline', '|]',
                      pos=token.pos + len(token.src) - 2)
            )
        elif token.src.startswith('[|'):
            self.abc_barline(
                Token('Barline', '[|', pos=token.pos)
            )
            self.abc_start_repeat_barline(
                Token('Barline', '|:',
                      pos=token.pos + 2)
            )
        elif '|' in token.src:

            left, right = token.src.split('|', maxsplit=1)
            self.abc_end_repeat_barline(
                Token('EndRepeatBarline', f'{left}|',
                      pos=token.pos)
            )
            self.abc_start_repeat_barline(
                Token('Barline', '|:',
                      pos=token.pos + len(token.src) - 2)
            )
        else:
            self.abc_end_repeat_barline(
                Token('EndRepeatBarline', f'{token.src[:-1]}|',
                      pos=token.pos)
            )
            self.abc_start_repeat_barline(
                Token('StartRepeatBarline', f'|:',
                      pos=token.pos + len(token.src) - 2
                      )
            )

    def abc_start_repeat_barline(self, token: Token):
        """
        Process the StartRepeatBarline token.

        If the last measure is still open, it needs to be closed first.
        Then, create a new measure with this bar line token.

        Parameters:
            token (Token): The StartRepeatBarline token to process.
        """

        if self.voice.stream:
            # If the last measure is still open, close it
            self.voice.close_measure(self.time_signature)

        # When starting a new repeat section, we will close all open repeat
        # Brackets.
        if self.voice.repeat_bracket:
            self.voice.close_repeat_bracket()

        if token.src[-1].isdigit():  # [n, |n
            # Open a new measure without a bar line
            self.voice.open_measure(key_signature=self.key_signature)
            # And open a repeat bracket
            self.voice.open_repeat_bracket(int(token.src[-1]))
        else:  # |:
            # Create a new measure with this bar line token
            self.voice.open_measure(
                key_signature=self.key_signature,
                bar_line=bar.Repeat(direction='start')
            )

    def abc_end_repeat_barline(self, token: Token):
        """
        Process the EndRepeatBarline token.

        If a measure is open, close it with this EndRepeatBarline token.

        Parameters:
            token (Token): The EndRepeatBarline token to process.
        """

        if self.voice.repeat_bracket:
            self.voice.close_repeat_bracket()

        #  Count the number of colons to determine the times
        if self.voice.stream:
            #  Close the current measure with this EndRepeatBarline Token
            self.voice.close_measure(
                time_signature=self.time_signature,
                bar_line=bar.Repeat(direction='end', times=token.src.count(':') + 1)
            )
        else:
            # There is no open measure in the context that can be closed
            # with this token
            print(f"Ignore end repeat bar line there is no open measure in this part.")

    def abc_barline(self, token: Token):
        """
        Process a Barline token.

         - '|' : This bar line only separates two measures.
         - '|] : This bar line has a light-heavy style
         - '[| : This bar line has a heavy-light style
         - '|| : This bar line has a light-light stylet

        - If a measure is open, close it with this bar line.
        - If there is no open measure, create a new measure with this bar line.

        Parameters:
          token (Token): The Barline token to process.
        """

        match token.src:
            case '|]':
                bar_line = bar.Barline('light-heavy')
            case '||':
                bar_line = bar.Barline('light-light')
            case '[|':
                bar_line = bar.Barline('heavy-light')
            case _:
                bar_line = bar.Barline()

        if bar_line.type != 'regular' and self.voice.repeat_bracket:
            self.voice.close_repeat_bracket()

        if self.voice.stream:
            # Close the current measure with this bar line
            self.voice.close_measure(self.time_signature, bar_line)
        else:
            # Create a new measure with this bar line
            self.voice.open_measure(bar_line,
                                    key_signature=self.key_signature
                                    )

    def abc_part(self, token: Field):
        """
        Processes an ABC Section token and manages section-related actions.

        This method extracts the section ID from the token and performs the
        following tasks:

        - Assigns leftover lyrics in the recent context.
        - Adds a new section if it doesn't already exist.
        - Sets the new active section and its active part.

        Args:
            token (Field): Token representing an abc part field (P:).
        """

        # Close old abc part
        self.close_part()
        part_id = token.data[0]

        # Add the section if it doesn't exist yet.
        if part_id not in self.part:
            self.section_tempo[part_id] = self.tempo
            self.sections[part_id] = {
                None: ABCVoice(
                    voice_id=None,
                    m21_clef=self.clef,
                    octave=self.octave)
            }

        # Set the new active section.
        self.part = self.sections[part_id]

        # Also set the active part of the new section.
        self.set_context(voice_id=None)


    def abc_broken_rhythm(self, token: Token):
        """
        Process a BrokenRhythm token according to the `abc:standard:v2.1:broken_rhythm
        <https://abcnotation.com/wiki/abc:standard:v2.1#broken_rhythm>`_

        Broken rhythm indications are used to modify the timing of notes or groups of notes.
        """
        if self.voice.overlay.last_note:
            self.voice.overlay.broken_rhythm = super().abc_broken_rhythm(token)
        else:
            self.abc_error('Ignore broken rhythm. No left side note.', token)

    def abc_unknown_token(self, token: Token):
        """
        Process an unknown ABC token. If the token represents a line break,
        it is processed accordingly. Otherwise, an error is generated for
        unknown tokens.

        Args:
         token (Token): The token representing an unknown ABC token.

        """
        self.abc_error(f"Unknown token.", token)

    def abc_annotation(self, token: Token):
        """
        Process a text annotation token in ABC notation.

        Text annotations are placed in quotation marks and provide additional
        textual information related to the melody.

        The first character of the annotation source string indicates the
        placement of the annotation relative to the next note:

        ====== ====================================
        Symbol Placement
        ====== ====================================
         `^`    above the note
         `_`    below the note
         `<`    left of the note (not supported by music21)
         `>`    right of the note (not supported by music21)
         `@`    indicate a free placement position (not supported by music21)
        ====== ====================================
        """

        content = token.src.strip('"')
        if text := content[1:]:
            text_expr = expressions.TextExpression(content=text)
        else:
            self.abc_error("Empty annotation.", token)
            return

        match content[0]:
            case '^':
                text_expr.placement = 'above'
            case '_':
                text_expr.placement = 'below'
            case _:
                self.abc_error(f"Text placement '{content[0]}' is not supported by music21.", token)

        self.voice.overlay.decorations.append(text_expr)

    def abc_ficta(self, token: Token):
        """
        Process an ABC ficta token.

        This method sets the ficta flag in the voice context, indicating that
        the next Note accidental represents an editorial accidental.

        Args:
            token (Token): The token representing an ABC ficta decoration.
        """
        self.voice.overlay.ficta = True

    def abc_close_spanner(self, token: Token):
        """
        Process a closing decoration spanner token in ABC notation.

        Closing spanners mark the end of the last opened spanner, such as
        a crescendo or diminuendo, and are used to indicate the scope of
        the spanner.

        Args:
            token (Token): The closing spanner token to process.

        """

        if self.voice.overlay.open_spanner:
            # Pop the spanner token on the open_spanner stack
            self.voice.overlay.close_spanner()
        else:
            self.abc_error(f"No open spanner to close.", token)

    def abc_open_slur(self, token: Token):
        """
        Process an ABC Open Slur token and add a Slur spanner to the active
        part.

        Args:
            token (Token): The token representing an ABC Open Slur.

        This method processes an ABC Open Slur token by adding a Slur spanner
        to the active context and part.

        """
        slur = spanner.Slur()
        if token.src.startswith('.'):
            slur.lineType = 'dashed'
        self.voice.add_spanner(slur)

    def abc_close_slur(self, token: Token):
        """
        Process a closing slur spanner token in ABC notation.

        Redirects this token to :class:`~BodyProcessor.abc_CloseSpanner`

        Args:
            token (Token): The closing slur spanner token to process.
        """
        self.abc_close_spanner(token)

    def abc_newline(self, token: Token):
        """
        Process a Newline token as a score linebreak if <EOL> is set in the
        linebreak symbols.
        """
        if not self.voice.part:
            return

        # Set a line break if <EOL> is a line break symbol and no backslash is
        # suppressing the newline
        if '<EOL>' in self.linebreak and not token.src.endswith('\\'):
            self.abc_score_linebreak(token)

    def abc_voice(self, token: Field):
        """
        Process abc voice field token in the tune body.
        """

        voice_id, m21_clef, octave = super().abc_voice(token)

        # change active voice context
        self.set_context(voice_id)

        if m21_clef is not None:
            self.voice.clef = m21_clef

        if octave is not None:
            self.voice.octave = octave

    def abc_tempo(self, token: Field):
        """
        Process a tempo token.

        Insert a music21 tempoMark Object into the recent measure
        """
        if tempoMark := super().abc_tempo(token):
            if self.voice.stream is None:
                self.voice.open_measure(key_signature=self.key_signature)

            self.voice.overlay.append(tempoMark)

    def abc_tuplet(self, token: Token):
        """
        Parses an ABC tuplet token and returns a list with multiples references
        to music21 duration. Tuplet objects, one for each note of the tuplet.

        Args:
          token: The token representing an ABC tuplet.

        Returns:
          List[duration.Tuplet]: A list of references to the music21 duration.Tuplet objects.

        """
        self.voice.overlay.tuplet = super().abc_tuplet(token)

    def abc_decoration_or_chord(self, token: Token):
        """
        Process a token that can represent either a decoration or a chord based on
        the ABC version or the 'I:decoration' instruction.

        - In ABC version 2.0, the '+' symbol is used instead of '!' to denote
          decorations.
        - In early versions of the ABC standard (1.2 to 1.5), chords were
          delimited with '+' symbols.
        - Using the 'I:decoration +' directive will enable the '+' symbol to
          denote decorations (while '!' is still valid for decorations) but
          will disable the legacy ABC chord symbol '+'.

        Args:
            token (Token): The token to process.
        """
        if self.is_legacy_abc_chord:
            try:
                self.abc_chord(token)
            except ABCException as e:
                self.abc_error("Cannot parse this chord (+ dialect). Perhaps it is in the + decoration dialect?", token)

        elif self.is_legacy_abc_decoration:
            self.abc_decoration(token)
        else:
            self.abc_error("The legacy use of '+' for chords or decorations is not allowed", token)

    def abc_decoration(self, token: Token):
        """
        Process a decoration token from ABC notation. This method determines
        the type of decoration (Dynamic, Repeat, Expression, Articulation,
        Spanner) and calls the appropriate processing method based on the
        decoration type.

        If the decoration is not recognized, an ABC error is printed.

        Args:
            token (Token): The decoration token to process.
        """

        # remove the decoration symbol '!' or '+'
        decoration = token.src[1:-1]

        if decoration == 'courtesy':
            self.voice.overlay.courtesy = True
        if decoration == 'trill':
            # Trill is a special case for detecting
            self.voice.overlay.is_trill = True
        elif decoration in M21_DYNAMICS:
            self.voice.overlay.decorations.append(
                dynamics.Dynamic(decoration)
            )
        elif decoration in M21_REPEATS:
            self.abc_repeat(token)
        elif decoration in M21_EXPRESSIONS:
            self.voice.overlay.expressions.append(
                M21_EXPRESSIONS[decoration]()
            )
        elif decoration in M21_ARTICULATIONS:
            self.voice.overlay.articulations.append(
                M21_ARTICULATIONS[decoration]()
            )
        elif decoration in M21_CLOSE_SPANNER:
            self.abc_close_spanner(token)
        elif decoration in M21_OPEN_SPANNER:
            self.voice.add_spanner(M21_OPEN_SPANNER[decoration]())
        elif decoration in ('1', '2', '3', '4', '5'):
            finger = articulations.Fingering(fingerNumber=int(decoration))
            finger.placement = 'below'
            self.voice.overlay.articulations.append(finger)
        else:
            self.abc_error('Unknown abc decoration', token)

    def abc_repeat(self, token: Token):
        """
        Process a repeat marking token in ABC notation.

        Repeat markers in ABC notation are special annotations used to indicate
        specific points in a musical score where the playback or notation
        should repeat or jump to another part of the score. These markers provide
        instructions for navigating the musical piece during performance or
        rendering.

        Insert the music21 repeat marker object into the decorations buffer of
        the active context. The objects in decorations will be inserted with
        the next note in this context.
        """
        self.voice.overlay.decorations.append(
            M21_REPEATS[token.src[1:-1]]()
        )

    def abc_GeneralNote(self, ncr: note.GeneralNote):
        """
        Apply various modifications to all music21 GeneralNote objects and add
        the note to the measure.

        - Apply duration modifications for a BrokenRhythm.
        - Handle the GeneralNote as part of a tuplet.
        - Apply slurs as the main note of grace notes.
        - Apply this note to open spanner.
        - Add collected expressions and articulations to the note.
        - Mark the accidental of the GeneralNote as a ficta/editorial
          accidental.

        Args:
            ncr (note.GeneralNote): The GeneralNote object to be processed.
        """
        if self.voice.stream is None:
            self.voice.open_measure(key_signature=self.key_signature)

        self.voice.overlay.apply_broken_rhythm(ncr)
        self.voice.overlay.apply_tuplet(ncr)
        self.voice.apply_grace_notes(ncr)
        self.voice.overlay.apply_decorations(ncr)

        # Autotrill spanner detection
        if trill_spanner := self.voice.overlay.apply_auto_trill_spanner(ncr):
            self.voice.part.insert(0, trill_spanner)

        self.voice.overlay.last_note = ncr

        # Append note/chord/rest to active overlay
        self.voice.overlay.append(ncr)

    def abc_note(self, token: Token):
        """
        Process an ABC note token and convert it to a music21 Note object.

        This method processes an ABC note token, converting it to a music21
        Note and applying necessary modifications such as adjusting the note's
        duration based on the quarter length.

        - Parses the ABC note and converts it to a music21 Note.
        - Adjusts the note's duration based on the current quarter length.
        - Applies modifications for GeneralNote objects

        Args:
            token (Token): The token representing an ABC note.
        """

        m21_note = super().abc_note(token)
        m21_note.quarterLength *= self.quarter_length
        # Existiert eine Bindung von einer vorherigen note zu dieser Note?

        if prev := self.voice.overlay.get_last_tied_note(m21_note):
            if m21_note.tie:
                m21_note.tie.type = 'continue'
            elif prev.tie.type in ('start', 'continue'):
                m21_note.tie = tie.Tie('stop')

        # End unconnected ties in the previous note/chord.
        self.voice.overlay.cleanup_ties([m21_note])

        self.abc_GeneralNote(m21_note)

    def abc_meter(self, token: Field):
        _meter = super().abc_meter(token)
        if _meter:
            if self.voice.stream is None:
                self.voice.open_measure(
                    key_signature=self.key_signature
                )
            self.voice.time_signature = _meter
            self.voice.stream.timeSignature = _meter

    def abc_chord(self, token: Token):
        """
        Process an ABC chord token and convert it to a music21 Chord object.

        This method processes an ABC chord token, converting it to a Music21
        Chord and applying necessary modifications, such as adjusting the
        chord's duration based on the quarter length.

        - Parses the internals of the ABC chord and converts it to a music21 Chord.
        - Adjusts the chord's duration based on the current quarter length.

        Args:
            token (Token): The token representing an ABC chord.

        """
        if (m21_chord := ChordParser(self).process(token)) is None:
            return
        m21_chord.quarterLength *= self.quarter_length
        self.abc_GeneralNote(m21_chord)

    def abc_rest(self, token: Token):
        """
        Process an ABC rest token and convert it to a music21 Rest object.
        This method processes an ABC rest token, converting it to a music21
        Rest object and adjusting its duration based on the specified length
        modifier and rest symbol. Additionally, it handles hiding the rest
        symbol if 'x' or 'X' is specified in the ABC.

        - Parses the length modifier and rest symbol from the ABC rest token.
        - Converts the ABC rest to a music21 Rest object, adjusting its
        duration based on the modifiers.
        - Handles hiding the rest symbol if specified in the ABC.

        Args:
            token (Token): The token representing an ABC rest.
        """

        rest_symbol = token.src[0]
        try:
            length_modifier = self.abc_length(token.src[1:])
        except ABCException as e:
            length_modifier = 1.0
            self.abc_error("Fallback to rest length modifier '1.0'.", token, e)

        rest: note.Rest = note.Rest()

        if rest_symbol in 'ZX':
            rest.quarterLength = length_modifier * self.time_signature.barDuration.quarterLength
        else:
            rest.quarterLength = length_modifier * self.quarter_length

        if rest_symbol in 'xX':
            rest.style.hideObjectOnPrint = True

        self.voice.overlay.cleanup_ties([])
        self.abc_GeneralNote(rest)

    def abc_user_symbol(self, token: Token):
        """
        Represents a user-defined symbol token in `abc:standard:v2.1:redefinable_symbols
        <https://abcnotation.com/wiki/abc:standard:v2.1#redefinable_symbols>`_

        This class is a subclass of Token and is used to represent a user-defined
        symbol (h-w, H-W and ~) in ABC notation. User-defined symbols are custom
        symbols that can be used in the body of an ABC tune.

        This Token will be replaced in the parser by tokens defined in an abc
        'U:user defined'.
        """
        if tokens := self.user_defined.get(token.src, None):
            for t in tokens:
                self.abc_token(t)

    def abc_score_linebreak(self, token: Token):
        """
        Process this token as a score linebreak and insert a music21 system
        layout object in an open measure or the music21 part.

        Args:
          token (Token): The token representing an ABC linebreak.

        """
        if token.src.strip() in self.linebreak or token.type == "newline":
            linebreak = layout.SystemLayout(isNew=True)
            if self.voice.stream:
                self.voice.stream.append(linebreak)
            else:
                self.voice.overlay.decorations.append(linebreak)
        else:
            self.abc_error(f"Symbol '{token.src}' is not a supported score linebreak")


    def fix_part_lengths(self):
        """
        Append additional empty measures to voices of a section to ensure equal
        lengths across all voices. It checks the length of each part within a
        section and extends them to match the length of the longest part. Empty
        voices or those not shown in the score are skipped.

        - Extends the length of voices to match the maximum part length within a section.
        - Do not extend voices that are empty in all sections.
        - voices or those not shown in the score are not extended.
        """
        section_sequence: str | list = self.section_sequence or list(self.sections.keys())
        part_order = self.voice_order()

        # Create a list of IDs for voices that are not empty.
        non_empty_voices = set()
        for part_id, section in self.sections.items():
            for voice_id, ctx in section.items():
                # Only include voices that are being played and are not empty
                if voice_id in part_order and len(ctx.part.getElementsByClass(stream.Measure)):
                    non_empty_voices.add(voice_id)

        for part_id, section in self.sections.items():
            # This section is not played
            if part_id not in section_sequence:
                continue

            section_part_lengths = [len(ctx.part.getElementsByClass(stream.Measure))
                                    for ctx in section.values()]

            if not section_part_lengths:
                continue

            max_part_len = max(section_part_lengths)

            for voice_id in non_empty_voices:
                if voice_id not in section:
                    section[voice_id] = ABCVoice(voice_id=None)

                ctx = section[voice_id]
                part_len = len(ctx.part.getElementsByClass(stream.Measure))
                if part_len < max_part_len:
                    for i in range(max_part_len - part_len):
                        fill_measure = stream.Measure()
                        ctx.part.append(fill_measure)

    def voice_order(self) -> list[str | None]:
        """
        Yield the order in which music21 voices should be shown in the score
        based on SCORE instruction or ABC tune.

        - If a SCORE instruction is present, yield the voice ID in the order
          specified by the SCORE instruction.

        - If no SCORE instruction is found, yield the voice ids in the order of
          the voices as defined in the ABC tune.

        Returns:
           List[str]: A list of voice identifiers in the appropriate order.
        """
        if self.staves:
            # yield voice ids in the order specified by the SCORE instruction
            return self.staves.order
        else:
            # yield voice ids in the order of the voices as defined in the ABC
            # tune
            return [None] + list(k for k in self.voice_info.keys())

    def process(self, token_generator: Iterator[Token]) -> stream.Score:
        for token in token_generator:
            if token.type == 'Emptyline':
                break

            self.abc_token(token)

        self.close_part()

        parts = list(self.combine_abc_parts())
        for midi_channel, part in enumerate(parts, start=1):
            self.apply_midi(part, midi_channel)
            self.score.append(part)

        try:
            fix_measures(self.score)
        except ABCException as e:
            self.abc_error('Fixing bar line failed', exception=e)

        self.voice_grouping()
        return self.score


class ChordParser(ABCParser, NoteMixin):
    def __init__(self, body_processor: TuneBody):
        super().__init__(body_processor.abc_version)
        self.key_signature = body_processor.key_signature
        self.accidental_mode = body_processor.accidental_mode
        self.voice = body_processor.voice
        self.is_legacy_abc_chord = body_processor.is_legacy_abc_chord

    def process(self, token: Token):

        if token.src.startswith('+'):
            # legacy chord style: +CEG+/2
            intern_str, length_str = token.src[1:].split('+', 1)
        else:
            # recent chord style [CEG]/2
            intern_str, length_str = token.src[1:].split(']', 1)

        if chord_is_tied := length_str.endswith('-'):
            length_str = length_str.rstrip('-')

        m21_notes: list[note.Note] = []

        for token in tokenize(intern_str):
            m21_note: note.Note = self.abc_note(token)
            m21_notes.append(m21_note)

            if chord_is_tied:
                m21_note.tie = tie.Tie('start')

            if prev := self.voice.overlay.get_last_tied_note(m21_note):
                if m21_note.tie:
                    m21_note.tie.type = 'continue'
                elif prev.tie.type in ('start', 'continue'):
                    m21_note.tie = tie.Tie('stop')

        self.voice.overlay.cleanup_ties(m21_notes)

        if not m21_notes:
            self.abc_error("Empty Chord.", token)
            return None

        # The internal length of the chord is equal the first chord note
        # Set the internal length to all chord notes
        for t in m21_notes:
            t.quarterLength = m21_notes[0].quarterLength

        m21_chord = chord.Chord(m21_notes)
        try:
            chord_length_modifier = self.abc_length(length_str)
        except ABCException as e:
            chord_length_modifier= 1.0
            self.abc_error("Fallback to chord length modifier '1.0'.", token, e)

        m21_chord.quarterLength = m21_notes[0].quarterLength * chord_length_modifier


        return m21_chord


class GraceNoteParser(ABCParser, NoteMixin):
    def __init__(self, body_processor: TuneBody):
        super().__init__(body_processor.abc_version)

        self.voice: ABCVoice = copy.copy(body_processor.voice)

        self.key_signature = body_processor.key_signature
        self.accidental_mode = body_processor.accidental_mode
        self.time_signature = body_processor.time_signature
        self.quarterLength = 0.25

    def process(self, intern: list[Token], slash:bool = False) -> list[music21.Music21Object]:
        grace_notes: list[note.Note] = []
        for token in intern:
            if grace_note := self.abc_token(token):
                grace_note.duration.slash = slash
                grace_notes.append(grace_note)
        return grace_notes

    def abc_broken_rhythm(self, token: Token):
        """
        Während grace notes broken rhythm enthalten können, dürfen sie nicht mir
        einen broken rhythm ausserhalb ihres kontext kommunizieren.
        """
        self.abc_error('Broken rhythm for grace notes not supported. (yet)', token)

    def abc_tuplet(self, token: Token):
        """
        Während grace notes broken rhythm enthalten können, dürfen sie nicht mir
        einen broken rhythm ausserhalb ihres kontext kommunizieren.
        """
        self.abc_error('Tuplets for grace notes not supported. (yet)', token)

    def abc_note(self, token: Token):
        m21_note= super().abc_note(token)
        m21_note.quarterLength *= self.quarterLength
        return m21_note.getGrace()


def ABCTranslator(abc: str | pathlib.Path) -> stream.Stream:
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
    >>> tune_path = Path('abc/avemaria.abc')
    >>> score = ABCTranslator(tune_path)
    >>> score
    <music21.stream.Score X:1 (file='abc/avemaria.abc')>
    >>> score.metadata.title
    "Ave Maria (Ellen's Gesang III) - Page 1"

    However, music21 spanners are set in the Part object, so the following
    example, even if it consists of only a few notes, will return a Part object.

    >>> abc_fragment = '''
    ... !>(!ABCD!>)!'''
    >>> isinstance(ABCTranslator(abc_fragment), stream.Part)
    True

    """
    if isinstance(abc, str):
        source_type = "string"
        src = abc
    elif isinstance(abc, pathlib.Path):
        source_type = str(abc)
        with abc.open() as f:
            src = f.read()
    else:
        raise ABCException("Illegal abc input, chose a pathlib.Path or str")

    abc_tune_book, *abc_tunes = ABC_TUNE_BOOK_SPLIT(src)
    # The ABC version strin if set is the first line of an ABC file.
    try:
        _, _version, abc_tune_book = ABC_VERSION_SPLIT(abc_tune_book, maxsplit=1)
        _version = [int(d) for d in _version.split('-', maxsplit=1)[1].split('.', maxsplit=2)]
        version = ABCVersion(_version + (3 - len(_version)) * [0])
    except ValueError:
        # no %%abc-.. Version found, use a default version ?
        version: ABCVersion = DEFAULT_VERSION

    if abc_tunes:
        # Evaluate and apply macros on the file header
        file_header_src, file_header_macros = apply_macros(abc_tune_book)
        file_header = FileHeader(version)
        t = tokenize(file_header_src, version)
        file_header.process(t)
        scores = []
        abc_tunes = iter(abc_tunes)
        while True:
            try:
                abc_refnum = next(abc_tunes).split('%', maxsplit=1)[0].strip()
                abc_tune_src = next(abc_tunes, "")
            except StopIteration:
                break

            # Evaluate and apply macros on the tunes
            tune_src = apply_macros(abc_tune_src, file_header_macros)[0].lstrip('\n')
            tokens = tokenize(tune_src)
            # tokens = list(tokens)
            # HeaderParser will process tokens until the header ends with Field 'K:'
            tune_header = TuneHeader(file_header=file_header, abc_version=version)
            tune_header.process(tokens)
            tokens = list(tokens)
            # BodyParser will process all remaining tokens
            score = TuneBody(tune_header=tune_header).process(tokens)
            if score.metadata:
                score.metadata.number = abc_refnum
            if source_type == "string":
                score.id = abc_refnum
            else:
                score.id = f"{abc_refnum} (file='{source_type}')"

            scores.append(score)

        if len(scores) > 1:
            opus = stream.Opus(id=source_type)
            for score in scores:
                opus.append(score)
            return opus
        else:
            return scores[0]
    else:
        tune_header = TuneHeader(abc_version=version)
        # no, its not a tune book just an abc fragment
        src = abc_tune_book.strip('\n')
        tokens = tokenize(src, abc_version=version)
        score = TuneBody(tune_header=tune_header).process(tokens)
        if len(score.parts) == 1:
            part = score.parts[0]
            if len(part.elements) == 1:
                measures = list(score.recurse().getElementsByClass(stream.Measure))
                if len(measures) == 1:
                    return measures[0]

            return part
        else:
            return score


if __name__ == '__main__':
    import doctest

    ABC2M21_ENVIRONMENT['debug'] = False
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
