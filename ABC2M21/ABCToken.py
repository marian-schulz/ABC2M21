import re
from typing import Iterator, TypeAlias

'''
# ABCToken Module Documentation

The ABCToken module is a crucial component of the ABC notation parsing process. It
defines various tokens utilized by the `~tokenize` method to generate tokens based
on regular expressions.

Token Types and Regular Expressions
------------------------------------

Each token corresponds to a specific element type in ABC notation, such as
metadata, notes, chords, and more. To allow the tokenizer to create these tokens
accurately, each token type requires a regular expression. This regular expression
defines the pattern that the tokenizer uses to identify and generate tokens of that
type.

The token types and their regular expressions are defined as tuples in the token
specification list.

TOKEN_SPEC: list[tuple[str,str]] = [ ('foobar', r'foobar') ... ]

Order of Token Specifications
-----------------------------

The order of tokens in the `TOKEN_SPEC` list is crucial, as it determines the
sequence in which the corresponding regular expressions are applied in the
`~tokenizer` method. For instance, consider the `Tuplet` and `OpenSlur` tokens. The
`Tuplet` token begins with a '(' followed by digits and sometimes ':' characters,
and it must precede the `OpenSlur` token in the list because the `OpenSlur` token
consists of a single '('. Consequently, the 'UnknownToken' is always listed last,
as it matches any character.

By maintaining the correct order of tokens, you ensure that the tokenizer can
accurately match and generate tokens from the input ABC notation.
'''

# Type aliases
ABCVersion: TypeAlias = tuple[int, int, int]

# Constants and default values
DEFAULT_VERSION: ABCVersion = (1, 6, 0)


class Token:
    """
    Represents a token in the ABC notation.
    Attributes:
        type (str): The type of the token (e.g., "MetaData", "Note", etc.).
        src (str): The text of the token as it appears in the ABC code.
        pos (int): The position within the abc source where the token begins.
    """
    __slots__ = ('type', 'src', 'pos')

    def __init__(self, type, src, pos: int = 0):
        self.type: str = type
        self.src: str = src
        self.pos: int = pos

    def __str__(self):
        return f"<{self.type}: '{self.src}' (pos={self.pos})>"

    def __repr__(self):
        return str(self)


class Field(Token):
    @property
    def tag(self):
        return self.src[1] if self.src.startswith('[') else self.src[0]

    @property
    def data(self):
        return (self.src[3:-1] if self.src.startswith('[') else self.src[2:]).strip()


def abc_field_regex(tags: str) -> str:
    r"""
    Creates a regular expression for abc fields. It will create
    an additional expression for inline field tags.
    """
    inline_tags = [t for t in tags if t in "IKLMPQRNUV"]
    regex = rf'^[{tags}]:.*(\n|$)'
    if inline_tags:
        regex += rf'|([\[]{"".join(inline_tags)}:[^\]\n%]*[\]])'
    return regex

TOKEN_SPEC: list[tuple[str, str]] = [
    ('Directive', r'^[%]{2}.*\n'),
    ('f_meta_data', abc_field_regex('ABCDFGHNORSTWZX')),
    ('f_meter', abc_field_regex('M')),
    ('f_key', abc_field_regex('K')),
    ('f_part', abc_field_regex('P')),
    ('f_user_def', abc_field_regex('U')),
    ('f_lyrics', abc_field_regex('w')),
    ('f_unit_note_length', abc_field_regex('L')),
    ('f_instruction', abc_field_regex('I')),
    ('f_tempo', abc_field_regex('Q')),
    ('f_voice', abc_field_regex('V')),
    ('f_symbol_line', abc_field_regex('s')),
    ('LineContinue', abc_field_regex('+')),
    ('tuplet', r'\([2-9]:[2-9]?:[2-9]|\([2-9]:[2-9]|\([2-9]'),
    ('grace_notes', r'\{[^\}]*\}'),
    ('bidirectonal_barline', r"|".join([':+[\|\]][12]', ':+\|:+', '\[\|:+', ':+\|\]', r'::+(?![\|\[])'])),
    ('end_repeat_barline', r"|".join([r':+[\|]', '[\|\]][1-9]'])),
    ('start_repeat_barline', r'[\|]:+|\[[1-9]'),
    ('barline', r"|".join([r'\|\]', r'\[\|', r'\|\|(?![:])', r'\|'])),
    ('decoration', r'![^!%\[\]\|:\s]+!'),     # Note that decorations may not contain any spaces, [, ], | or : signs.
    ('chord', r'[\[][^\]:]*[\]][0-9]*[/]*[0-9]*(\s*[-])?'),
    ('decoration_or_chord', r'[+][^+:\n]*[+][0-9]*[/]*[0-9]*(\s*[-])?'),  # for legacy support
    ('unknown_decoration', rf"![^!\n]!"),
    ('open_slur', r'[\.]?\('),
    ('close_slur', r'[\.]?\)'),
    ('broken_rhythm', r'[>]{1,3}|[<]{1,3}'),
    ('annotation', r'"[\^_<>@][^"]*"'),
    ('chord_symbol', r'"[^\^<>_@"][^"]*"'),
    ('overlay', r'&'),
    ('rest', r'[zZxX][0-9/]*(?!:)'),
    ('note', r'[=_\^]*[a-gA-G][\',0-9/]*(\s*[-])?'),
    ('score_linebreak', '[\$\!]'),
    ('user_symbol', r'[H-Wh-w~\.](?![:])'),
    ('EmptyLine', r'^([ \t]*[\n])+'),
    ('Skip', r'^%(?!%).*(\n|$)|%.*$'),
    ('newline', r'[\\ ]*(%[^\n\\]*)?[\\]?[ \t]*\n'),
    ('unknown_token', r'\S')
    # ('Space', r'\s+')
]

TOKEN_RE = re.compile(r"|".join(f'(?P<{name}>{regex})' for name, regex in TOKEN_SPEC),
                      flags=re.MULTILINE)


def remove_comment(text: str) -> str:
    """
    This method carefully removes comments, ensuring '%' is not enclosed
    within "".

    Examples:
        Remove '%' and all following characters.

        >>> remove_comment('K: G% a comment')
        'K: G'

        '%' enclosed by "" is not considered a comment.

        >>> remove_comment('K: G "% not a comment"% a comment')
        'K: G "% not a comment"'

        Here, '%' is not enclosed by "".

        >>> remove_comment('K: G "%a comment')
        'K: G "'

        Will work also on an empty string. (no exception)
        >>> remove_comment('')
        ''
    """
    return re.match(r'("[^"\n]*"|[^"%\n]*)*[^%]*', text).group(0).rstrip()


def tokenize(src: str, abc_version: ABCVersion | None = DEFAULT_VERSION) -> Iterator[Token]:
    """
    Tokenizes the input ABC notation source code.

    Args:
        src (str): The input ABC notation source code.
        abc_version (tuple[int, int, int], optional): The ABC notation version.
        Defaults to MIN_VERSION.

    Returns:
        List[Token]: A list of Token objects representing the parsed tokens.
    """

    if abc_version == (2, 0, 0):
        # For abc 2.0 only:
        # If the last character on a line is a backslash (\), the next line
        # should be appended to the current one, deleting the backslash and
        # the newline, to make one long logical line. There may appear spaces
        # or an end-of-line remark after the backslash: these will be deleted
        # as well.
        src = re.sub(r'[\\]((\s*\n)|(\s*%.*\n))', '', src)

    # token buffer for line continue
    token_buffer: list[Field] = []
    # line number of the token in the abc notation
    empty_line: bool = False

    for m in TOKEN_RE.finditer(src):
        token_type = m.lastgroup
        token_string = m.group()

        # Ignore anything but metadata, fields and directives
        # after an empty line appears
        if token_type.startswith('f_'):
            token_type = token_type[2:]
            # Prepare this token from an abc string type field for a line
            # continue token (+:)
            # Other fields are not of type string and can't extend by using '+:'

            # String type fields may contain accents and ligatures
            token_string = encode_accent_and_ligature(token_string.rstrip('\n').rstrip())
            field = Field(token_type, remove_comment(token_string), m.start())
            # And add this token into the buffer

            # At first yield and empty the token buffer
            if token_buffer:
                if token_buffer[0].src.endswith('\\') and token_buffer[0].tag == field.tag:
                    token_buffer[0].src = token_buffer[0].src.rstrip("\\") + field.data
                    continue

                yield from token_buffer
                token_buffer = [field]
            else:
                token_buffer.append(field)

            continue

        elif empty_line and token_type != 'Directive':
            continue

        match token_type:
            case 'EmptyLine':
                # After an emtpy line, there is often free text
                empty_line = True
                continue
            case 'Space':
                # No use of Space yet
                continue
            case 'Skip':
                continue
            case 'Directive':
                token_string = remove_comment(token_string[2:-1])
                token = Field('instruction', f'I:{token_string}', m.start())
                if token_buffer:
                    # If the token buffer is not empty, add this token
                    # in the buffer
                    token_buffer.append(token)
                else:
                    yield token
                    # For the line continue a directive is just a comment
                continue
            case 'LineContinue':
                if token_buffer:
                    # Continue Metadata and lyrics fields (string type fields) with '+:'
                    # stored in the token_buffer

                    # remove comments
                    token_string = remove_comment(token_string)
                    # String type fields may contain accents and ligatures
                    token_string = encode_accent_and_ligature(token_string[2:])
                    token_buffer[0].src = token_buffer[0].src.rstrip("\\") + " " + token_string
                else:
                    print(f"Skip '{token_type}' there was no previous abc string field to continue.")

                continue

            case _:
                # Any other token will reset the line continue feature
                # yield and empty the token buffer
                yield from token_buffer
                token_buffer = []

        # Remove newline and whitespaces
        yield Token(token_type, token_string.strip(), m.start())

    # yield the token buffer (if not empty)
    if token_buffer:
        yield from token_buffer


ACCENT_AND_LIGATURES = {'&Aacute;': 'Á', '&Abreve;': 'Ă', '&Acirc;': 'Â', '&Agrave;': 'À', '&Aring;': 'Å',
                        '&Atilde;': 'Ã', '&Auml;': 'Ä', '&Ccedil;': 'Ç', '&Eacute;': 'É', '&Ecirc;': 'Ê',
                        '&Egrave;': 'È', '&Euml;': 'Ë', '&Iacute;': 'Í', '&Icirc;': 'Î', '&Igrave;': 'Ì',
                        '&Iuml;': 'Ï', '&Ntilde;': 'Ñ', '&Oacute;': 'Ó', '&Ocirc;': 'Ô', '&Ograve;': 'Ò',
                        '&Oslash;': 'Ø', '&Otilde;': 'Õ', '&Ouml;': 'Ö', '&Scaron;': 'Š', '&Uacute;': 'Ú',
                        '&Ucirc;': 'Û', '&Ugrave;': 'Ù', '&Uuml;': 'Ü', '&Yacute;': 'Ý', '&Ycirc;': 'Ŷ',
                        '&Yuml;': 'Ÿ', '&Zcaron;': 'Ž', '&aacute;': 'á', '&abreve;': 'ă', '&acirc;': 'â',
                        '&agrave;': 'à', '&aring;': 'å', '&atilde;': 'ã', '&auml;': 'ä', '&ccedil;': 'ç',
                        '&eacute;': 'é', '&ecirc;': 'ê', '&egrave;': 'è', '&euml;': 'ë', '&iacute;': 'í',
                        '&icirc;': 'î', '&igrave;': 'ì', '&iuml;': 'ï', '&ntilde;': 'ñ', '&oacute;': 'ó',
                        '&ocirc;': 'ô', '&ograve;': 'ò', '&oslash;': 'ø', '&otilde;': 'õ', '&ouml;': 'ö',
                        '&scaron;': 'š', '&uacute;': 'ú', '&ucirc;': 'û', '&ugrave;': 'ù', '&uuml;': 'ü',
                        '&yacute;': 'ý', '&ycirc;': 'ŷ', '&yuml;': 'ÿ', '&zcaron;': 'ž', '&copy;': '©',
                        '\\"A': 'Ä', '\\"E': 'Ë',
                        '\\"I': 'Ï', '\\"O': 'Ö', '\\"U': 'Ü', '\\"Y': 'Ÿ', '\\"a': 'ä', '\\"e': 'ë', '\\"i': 'ï',
                        '\\"o': 'ö', '\\"u': 'ü', '\\"y': 'ÿ', "\\'A": 'Á', "\\'E": 'É', "\\'I": 'Í', "\\'O": 'Ó',
                        "\\'U": 'Ú', "\\'Y": 'Ý', "\\'a": 'á', "\\'e": 'é', "\\'i": 'í', "\\'o": 'ó', "\\'u": 'ú',
                        "\\'y": 'ý', '\\/O': 'Ø', '\\/o': 'ø', '\\AA': 'Å', '\\HO': 'Ő', '\\HU': 'Ű', '\\Ho': 'ő',
                        '\\Hu': 'ű', '\\^A': 'Â', '\\^E': 'Ê', '\\^I': 'Î', '\\^O': 'Ô', '\\^U': 'Û', '\\^Y': 'Ŷ',
                        '\\^a': 'â', '\\^e': 'ê', '\\^i': 'î', '\\^o': 'ô', '\\^u': 'û', '\\^y': 'ŷ', '\\`A': 'À',
                        '\\`E': 'È', '\\`I': 'Ì', '\\`O': 'Ò', '\\`U': 'Ù', '\\`a': 'à', '\\`e': 'è', '\\`i': 'ì',
                        '\\`o': 'ò', '\\`u': 'ù', '\\aa': 'å', '\\cC': 'Ç', '\\cc': 'ç', '\\uA': 'Ă', '\\uE': 'Ĕ',
                        '\\ua': 'ă', '\\ue': 'ĕ', '\\vS': 'Š', '\\vZ': 'Ž', '\\vs': 'š', '\\vz': 'ž', '\\~A': 'Ã',
                        '\\~N': 'Ñ', '\\~O': 'Õ', '\\~a': 'ã', '\\~n': 'ñ', '\\~o': 'õ', '&AElig;': 'Æ',
                        '&aelig;': 'æ', '&OElig;': 'Œ', '&oelig;': 'œ', '&szlig;': 'ß', '&ETH;': 'Ð', '&eth;': 'ð',
                        '&THORN;': 'Þ', '&thorn;': 'þ', '\\AE': 'Æ', '\\ae': 'æ', '\\OE': 'Œ', '\\oe': 'œ',
                        '\\ss': 'ß', '\\DH': 'Ð', '\\dh': 'ð', '\\TH': 'Þ', '\\th': 'þ'}

ACCENT_AND_LIGATURES_RE = re.compile('|'.join(re.escape(entity) for entity in ACCENT_AND_LIGATURES.keys()))


def encode_accent_and_ligature(text: str) -> str:
    """
    Encode accents and ligatures in a given text according `abc:standard:v2.1:accents and ligatures
    <https://abcnotation.com/wiki/abc:standard:v2.1#supported_accents_ligatures>`_

    This function takes a text input and replaces any occurrences of accents
    and ligatures found in the input with their encoded forms based on the
    ACCENT_AND_LIGATURES dictionary.

    Args:
        text (str): The input text to encode.

    Returns:
        str (str): The encoded text with accents and ligatures replaced.

    Examples:

        >>> encode_accent_and_ligature("Cafe &acirc; la carte")
        'Cafe â la carte'

        >>> encode_accent_and_ligature("Spa&szlig; ist toll")
        'Spaß ist toll'
    """
    return ACCENT_AND_LIGATURES_RE.sub(
        lambda m: ACCENT_AND_LIGATURES[m.group(0)], text)


if __name__ == '__main__':
    # Test the token regular expressions
    for name, regex in TOKEN_SPEC:
        try:
            re.compile(regex)
        except re.error as e:
            print(f"Compiling regular expressions of token '{name}' failed.", e)

    from testtunes import *

    test = """X: 1
K:G "hjh" "% foo
c %5
d
e
    """

    for token in tokenize(test):
        print(token)

    # import doctest
    # doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
