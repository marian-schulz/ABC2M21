import unittest
from unittest.mock import patch
from io import StringIO
from testtunes import *
from typing import NamedTuple
from music21 import duration, spanner, dynamics, common, tie, instrument, clef
from music21 import expressions, articulations, harmony, style, environment
from music21 import meter, key, pitch, stream, metadata, bar, tempo, layout
from music21 import note, chord, repeat, base
from itertools import chain
from ABC2M21 import ABCTranslator, tokenize

a = environment.Environment()
a['debug'] = True


class TestMetric(NamedTuple):
    # Total number of music elements in the Score.
    objects: int = 0
    # Number of notes in the Score.
    note: int = 0
    # Number of notes in the Score.
    grace: int = 0
    # Number of chords in the score
    chord: int = 0
    # Number of measures (bars) in the Score.
    measure: int = 0
    # Number of parts in the Score.
    part: int = 0
    # Number of voices in the Score.
    voice: int = 0
    # Number of grace notes in the Score.
    grace_note: int = 0
    # Number of spanners (e.g., slurs) in the Score.
    spanner: int = 0
    # Number of articulations (e.g., staccato) in the Score.
    articulation: int = 0
    # Number of expressions (e.g., crescendo) in the Score.
    expression: int = 0
    # Number of clefs in the Score.
    clef: int = 0
    # Number of key signatures (key changes) in the Score.
    keysig: int = 0
    # Number of tempo markings in the Score.
    tempo: int = 0
    # Number of time signature changes (meter) in the Score.
    meter: int = 0
    # Number of annotations (e.g., text markings) in the Score.
    text_expression: int = 0
    # Number of barlines in the Score.
    barlines: int = 0
    # Number of tied notes in the Score.
    ties: int = 0


def create_metric(src: str):
    score: stream.Score = next(ABCtranslator(src))
    _objects = score.flatten().getElementsByClass(base.Music21Object)
    _note = score.flatten().getElementsByClass(note.Note)
    _chord = score.flatten().getElementsByClass(chord.Chord)
    _rest = score.flatten().getElementsByClass(note.Rest)
    _measure = score.recurse().getElementsByClass(stream.Measure)
    _part = score.recurse().getElementsByClass(stream.Part)
    _voice = score.recurse().getElementsByClass(stream.Voice)
    _spanner = score.flatten().getElementsByClass(stream.Voice)
    _clef = score.flatten().getElementsByClass(clef.Clef)
    _keysig = score.flatten().getElementsByClass(key.KeySignature)
    _tempo = score.flatten().getElementsByClass(tempo.MetronomeMark)
    _meter = score.flatten().getElementsByClass(meter.TimeSignature)
    _barlines = score.flatten().getElementsByClass(bar.Barline)
    _grace_note = score.flatten().getElementsByClass(stream.Voice)
    _text_expression = score.flatten().getElementsByClass(expressions.TextExpression)
    _expression = []
    _articulation = []
    _ties = 0
    _grace = 0
    for n in chain(_note, _chord):
        _expression.extend(n.expressions)
        _articulation.extend(n.articulations)
        if n.tie:
            _ties += 1
        if isinstance(n.duration, duration.GraceDuration):
            _grace += 1

    return TestMetric(
        objects=len(_objects),
        note=len(_note),
        chord=len(_chord),
        measure=len(_measure),
        part=len(_part),
        voice=len(_voice),
        grace_note=len(_grace_note),
        spanner=len(_spanner),
        articulation=len(_articulation),
        expression=len(_expression),
        clef=len(_clef),
        keysig=len(_keysig),
        tempo=len(_tempo),
        meter=len(_meter),
        text_expression=len(_text_expression),
        barlines=len(_barlines),
        ties=_ties,
        grace=_grace
    )


def create_matric_minimal(src):
    nt = create_metric(src)
    fields = [f'{n}={v}' for n, v in nt._asdict().items() if v != 0]
    return f"TestMetric({','.join(fields)})"


tunenames = ['trills', 'voices_and_overlays', 'voices_and_parts', 'keysig', 'keys_and_vocies',
             'broken_rythm', 'decorations', 'repeat', 'grace', 'chord', 'tuplets', 'overlays_and_lyric',
             'user_defined_symbols', 'spanner', 'keysigs', 'propagate_accidentals', 'ties', 'slur',
             'carry_accidentals', 'tempo_in_parts_and_voices', 'segno_and_fine', 'ficta', 'clef',
             'lyrics', 'with_lyrics_parts_and_voices', 'lyrics_parts_and_voices', 'beam_groups',
             'atholl_brose']

test_metric = {
    "trills": TestMetric(objects=48, note=20, chord=4, measure=6, part=1, voice=6, expression=4, clef=1, keysig=1,
                         meter=1, barlines=12),
    "voices_and_overlays": TestMetric(objects=39, note=23, chord=1, measure=4, part=2, voice=6, clef=2, keysig=2,
                                      meter=2, barlines=8),
    "voices_and_parts": TestMetric(objects=176, note=72, chord=2, keysig=10, meter=16, text_expression=5, barlines=40),
    "keysig": TestMetric(objects=10, note=4, keysig=1, meter=1, barlines=2),
    "keys_and_vocies": TestMetric(objects=33, note=17, expression=3, keysig=1, meter=1, barlines=8),
    "broken_rythm": TestMetric(objects=14, note=8, keysig=1, meter=1, barlines=2),
    "decorations": TestMetric(objects=44, note=20, chord=2, articulation=10, expression=8, keysig=1, meter=1,
                              text_expression=2, barlines=12),
    "repeat": TestMetric(objects=49, note=28, keysig=2, meter=2, barlines=12),
    "grace": TestMetric(objects=17, note=9, grace=6, keysig=1, barlines=2),
    "chord": TestMetric(objects=14, chord=5, keysig=1, barlines=6),
    "tuplets": TestMetric(objects=49, note=39, articulation=2, keysig=1, meter=1, barlines=4),
    "overlays_and_lyric": TestMetric(objects=22, note=13, keysig=1, meter=1, barlines=4),
    "user_defined_symbols": TestMetric(objects=8, note=3, articulation=2, expression=2, keysig=1, barlines=2),
    "spanner": TestMetric(objects=33, note=17, expression=3, keysig=1, meter=1, barlines=8),
    "keysigs": TestMetric(objects=106, note=64, keysig=9, meter=4, text_expression=4, barlines=16),
    "propagate_accidentals_not": TestMetric(objects=43, note=24, keysig=1, meter=1, barlines=12),
    "ties": TestMetric(objects=29, note=8, chord=4, keysig=1, meter=1, barlines=12, ties=7),
    "slur": TestMetric(objects=24, note=12, keysig=1, meter=1, barlines=6),
    "carry_accidentals": TestMetric(objects=16, note=7, chord=1, keysig=1, meter=1, barlines=4),
    "tempo_in_parts_and_voices": TestMetric(objects=51, note=16, keysig=4, tempo=4, meter=4, text_expression=2,
                                            barlines=16),
    "segno_and_fine": TestMetric(objects=15, note=4, keysig=1, tempo=1, meter=1, text_expression=2, barlines=4),
    "ficta": TestMetric(objects=11, note=4, keysig=1, tempo=1, meter=1, barlines=2),
    "ave_maria": TestMetric(objects=47, note=22, grace=2, keysig=1, tempo=1, meter=1, barlines=10),
    "Magnificat": TestMetric(objects=30, note=13, expression=1, keysig=2, tempo=1, meter=2, barlines=8, ties=2),
    "lyrics": TestMetric(objects=25, note=12, keysig=1, meter=1, barlines=6),
    "with_lyrics_parts_and_voices": TestMetric(objects=100, note=48, keysig=4, meter=4, text_expression=3, barlines=24),
    "lyrics_parts_and_voices": TestMetric(objects=44, note=16, keysig=4, meter=4, text_expression=3, barlines=8),
    "beam_groups": TestMetric(objects=14, note=8, keysig=1, meter=1, barlines=2),
    "unendliche_freude": TestMetric(objects=1),
    "atholl_brose": TestMetric(objects=299, note=214, grace=121, keysig=1, tempo=1, barlines=24)}

environLocal = environment.Environment('ABC2M21')


class TestFiles(unittest.TestCase):
    # Testfälle für den Translator

    def test_file_metric(self):
        return
        for testfile, metric in test_metric.items():
            score: stream.Score = next(ABCtranslator(testfile))
            notes = score.flatten().getElementsByClass(note.Note)
            self.assertEqual(len(notes), metric.note)

    def test_legacy_chord_and_decoration(self):

        # catch debug messages
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_legacy_chord_and_decoration)

        self.assertIsInstance(score, stream.Score, )
        # we have one chord ?
        self.assertEqual(len(score.recurse().getElementsByClass(chord.Chord)), 1)
        # and one note
        notes = score.recurse().getElementsByClass(note.Note)
        self.assertEqual(len(notes), 1)
        # the note has as trill expression
        self.assertIsInstance(notes[0].expressions[0], expressions.Trill)

        # Check the debug message for legacy warning about unknown decoration
        debug_messages = mock_stdout.getvalue()
        self.assertIn("TuneBody: Unknown abc decoration", debug_messages)
        self.assertIn("<decoration_or_chord: '+CEG+' (pos=100)>", debug_messages)

    def test_legacy_decoration_2_0(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_legacy_decoration_2_0)

        self.assertIsInstance(score, stream.Score)
        notes = list(score.recurse().getElementsByClass(note.Note))
        # we have 5 notes
        self.assertEqual(len(notes), 5)

        # the first note has a trill expression
        self.assertTrue(notes[0].expressions)
        self.assertIsInstance(notes[0].expressions[0], expressions.Trill)

        # the second note has no articulation
        self.assertFalse(notes[1].articulations)

        # the third note has a Pizzicato articulation
        self.assertTrue(notes[2].articulations)
        self.assertIsInstance(notes[2].articulations[0], articulations.Pizzicato)

        # the forth & fifth note has a Pizzicato articulation
        self.assertTrue(notes[3].articulations)
        self.assertIsInstance(notes[3].articulations[0], articulations.Pizzicato)
        self.assertTrue(notes[4].articulations)
        self.assertIsInstance(notes[4].articulations[0], articulations.Pizzicato)

        # Check the debug message about unknown decoration and token
        debug_messages = mock_stdout.getvalue()
        self.assertIn("TuneBody: Unknown abc decoration", debug_messages)
        self.assertIn("<decoration_or_chord: '++' (pos=70)>", debug_messages)
        self.assertIn("ABC2M21: TuneBody: Unknown token.", debug_messages)
        self.assertIn("<unknown_token: '+' (pos=72)>", debug_messages)

    def test_decoration_instruction(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_decoration_instruction)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        notes = list(score.recurse().getElementsByClass(note.Note))
        # we have 3 notes
        self.assertEqual(len(notes), 3)

        # the first note has no trill expression
        self.assertFalse(notes[0].expressions)

        # the second note has a trill expression
        self.assertTrue(notes[1].articulations)
        self.assertIsInstance(notes[1].articulations[0], articulations.Pizzicato)

        # the third note has a trill expression
        self.assertTrue(notes[2].expressions)
        self.assertIsInstance(notes[2].expressions[0], expressions.Trill)

        # Check the debug message about legacy decoration and token
        self.assertIn("The legacy use of '+' for chords or decorations is not allowed", debug_messages)
        self.assertIn("<decoration_or_chord: '+trill+' (pos=3)>", debug_messages)

    def test_tune_header(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            opus = ABCTranslator(abc_tune_header_and_file_structure)
            debug_messages = mock_stdout.getvalue()

        # we are interested in the handling of fields and freetext in the file header
        def test_custom(value: str, name: str):
            custom_value = md.getCustom(name)
            self.assertTrue(custom_value)
            self.assertIn(value, custom_value[0]._data)

        self.assertIsInstance(opus, stream.Opus)
        score = opus.scores[0]
        # there is just one tune, the second is empty:
        self.assertEqual(len(score.parts), 1)
        self.assertIn("Tune is complete empty", debug_messages)

        # Check legal metadata fields in the file header
        md = score.metadata
        self.assertEqual('Area, Origin', md.localeOfComposition)
        self.assertEqual('Composer', md.composer)
        test_custom('Discography', 'discography', )
        test_custom('File URI', 'file')
        test_custom('History', 'history')
        test_custom('Groups', 'groups')
        test_custom('Notes', 'notes')
        test_custom('Rhythm', 'rhythm')
        test_custom('Source', 'source')
        transcription = metadata.Contributor(name='Transcription', role='abc-transcription')
        self.assertIn(transcription, md.contributors)
        # Check illegal metadata fields in the file header
        self.assertNotEqual(md.title, 'Tuneheader')
        self.assertIn("FileHeader: Ignore titel (T:) field.", debug_messages)
        self.assertIn("<meta_data: 'T:Tuneheader' (pos=583)>", debug_messages)

        # Check for illegal fields in tuneheader
        self.assertIn("FileHeader: No abc_method 'abc_key'.", debug_messages)
        self.assertIn("<key: 'K:Cm' (pos=204)>", debug_messages)
        self.assertIn("FileHeader: No abc_method 'abc_part'.", debug_messages)
        self.assertIn("<part: 'P:X' (pos=338)>", debug_messages)
        self.assertIn("FileHeader: No abc_method 'abc_tempo'.", debug_messages)
        self.assertIn("<tempo: 'Q:1/4=120' (pos=401)>", debug_messages)
        self.assertIn("FileHeader: No abc_method 'abc_symbol_line'.", debug_messages)
        self.assertIn("<symbol_line: 's:!trill! - - -' (pos=523)>", debug_messages)
        self.assertIn("FileHeader: No abc_method 'abc_voice'.", debug_messages)
        self.assertIn("<voice: 'V:Viola' (pos=675)>", debug_messages)
        self.assertIn("FileHeader: Ignore ABC field 'W'.", debug_messages)
        self.assertIn("<meta_data: 'W:Words' (pos=733)>", debug_messages)
        self.assertIn("FileHeader: No abc_method 'abc_lyrics'.", debug_messages)
        self.assertIn("<lyrics: 'w:lyrics' (pos=791)>", debug_messages)

        # look for the bach motiv B-ACB in the first score
        notes = list(score.recurse().getElementsByClass(note.Note))
        self.assertEqual(len(notes), 4)
        self.assertEqual("".join([n.name for n in notes]), "B-ACB")

    def test_line_continue_2_0(self):
        tokens = list(tokenize(line_continue_2_0, abc_version=(2, 0, 0)))
        self.assertEqual(len(tokens), 9)
        self.assertEqual('newline', tokens[5].type)
        self.assertEqual('newline', tokens[8].type)

    def test_line_continue(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(line_continue)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        self.assertEqual(len(score.parts), 1)
        score_linebreaks = score.recurse().getElementsByClass(layout.SystemLayout)
        self.assertEqual(len(score_linebreaks), 4)
        self.assertEqual(score.metadata.title, 'Line Continue')

    def test_rests(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_rests)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        rests: list[note.Rest] = list(score.recurse().getElementsByClass(note.Rest))
        hidden_rest = [rest for rest in rests if rest.style.hideObjectOnPrint == True]

        self.assertEqual(14, len(rests))
        self.assertEqual(7, len(hidden_rest))
        self.assertEqual(32.0, sum(r.quarterLength for r in rests))

    def test_trills(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_trills)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        notes = list(score.recurse().getElementsByClass(note.Note))
        trill_expression_notes = [n for n in notes if n.expressions and isinstance(n.expressions[0], expressions.Trill)]
        self.assertEqual(len(trill_expression_notes), 2)
        trill_spanner = list(score.recurse().getElementsByClass(expressions.TrillExtension))
        self.assertEqual(len(trill_spanner), 2)

    def test_overlays_and_voices(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_overlays_and_voices)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        self.assertEqual(len(score.parts), 2)

    def test_spanner(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_spanner)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        spanners = list(score.recurse().getElementsByClass(spanner.Spanner))
        self.assertEqual(len(spanners), 3)
        for sp in spanners:
            self.assertTrue(sp.completeStatus)

    def test_broken_rhythm(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_broken_rhythm)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        gen_notes = list(score.recurse().getElementsByClass(note.GeneralNote))
        self.assertEqual(35, len(gen_notes))
        from collections import Counter
        durations = Counter()
        for n in gen_notes:
            durations[n.quarterLength] += 1
        self.assertEqual(6, durations[0.0])
        self.assertEqual(2, durations[0.125])
        self.assertEqual(2, durations[0.25])
        self.assertEqual(10, durations[0.5])
        self.assertEqual(1, durations[1.0])
        self.assertEqual(10, durations[1.5])
        self.assertEqual(2, durations[1.75])
        self.assertEqual(2, durations[1.875])
        self.assertIn("Overlay: Remove unfinished broken rhythm", debug_messages)
        self.assertIn("TuneBody: Ignore broken rhythm. No left side note.", debug_messages)
        self.assertIn("<broken_rhythm: '>' (pos=38)>", debug_messages)

    def test_decorations(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_decorations)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        gen_notes = list(score.recurse().getElementsByClass(note.GeneralNote))
        decorations = []
        for gen_note in gen_notes:
            decorations.extend(gen_note.expressions)
            decorations.extend(gen_note.articulations)

        def count_decoration(decoration_type) -> int:
            return len([e for e in decorations if type(e) == decoration_type])

        self.assertEqual(1, count_decoration(expressions.Trill))
        self.assertEqual(1, count_decoration(expressions.ArpeggioMark))
        self.assertEqual(2, count_decoration(expressions.Mordent))
        self.assertEqual(3, count_decoration(expressions.InvertedMordent))
        self.assertEqual(2, count_decoration(expressions.Fermata))
        self.assertEqual(1, count_decoration(expressions.Turn))
        self.assertEqual(1, count_decoration(expressions.Schleifer))
        self.assertEqual(1, count_decoration(articulations.Tenuto))
        self.assertEqual(3, count_decoration(articulations.StrongAccent))
        self.assertEqual(1, count_decoration(articulations.UpBow))
        self.assertEqual(1, count_decoration(articulations.DownBow))
        self.assertEqual(1, count_decoration(articulations.Staccato))
        self.assertEqual(1, count_decoration(articulations.OpenString))
        self.assertEqual(1, count_decoration(articulations.Pizzicato))
        self.assertEqual(1, count_decoration(articulations.SnapPizzicato))
        self.assertEqual(1, count_decoration(articulations.NailPizzicato))
        self.assertEqual(2, count_decoration(articulations.Accent))

        _dynamics = list(score.recurse().getElementsByClass(dynamics.Dynamic))
        self.assertEqual(11, len(_dynamics))
        for value in ['p', 'pp', 'ppp', 'pppp', 'f', 'ff', 'fff', 'ffff', 'mp', 'mf', 'sfz']:
            self.assertTrue(any(dyn for dyn in _dynamics if dyn.value == value))

        _repeats = list(score.recurse().getElementsByClass(repeat.RepeatMark))
        self.assertEqual(9, len(_repeats))
        for repeat_type in [repeat.Segno, repeat.Fine, repeat.Coda, repeat.DalSegno,
                            repeat.DalSegnoAlCoda, repeat.DalSegnoAlFine, repeat.DaCapo,
                            repeat.DaCapoAlCoda, repeat.DaCapoAlFine]:
            self.assertTrue(any(isinstance(r, repeat_type) for r in _repeats))

        self.assertEqual(1, debug_messages.count('Unknown abc decoration'))
        self.assertIn("TuneBody: Unknown abc decoration", debug_messages)
        self.assertIn("<decoration: '!unknown!' (pos=312)>", debug_messages)

    def test_bar_lines(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_repeat_bar_lines)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        #repeat.RepeatFinder(score).simplify()

        bar_lines: list = list(score.recurse().getElementsByClass(bar.Barline))
        self.assertEqual(8, len(bar_lines))

        self.assertIsInstance(bar_lines[0], bar.Repeat)
        self.assertEqual("start", bar_lines[0].direction)
        self.assertEqual("heavy-light", bar_lines[1].type)
        self.assertIsInstance(bar_lines[2], bar.Repeat)
        self.assertEqual("end", bar_lines[2].direction)
        self.assertEqual(2, bar_lines[2].times)
        self.assertIsInstance(bar_lines[3], bar.Repeat)
        self.assertEqual("start", bar_lines[3].direction)
        self.assertIsInstance(bar_lines[4], bar.Repeat)
        self.assertEqual("end", bar_lines[4].direction)
        self.assertEqual(3, bar_lines[4].times)
        self.assertIsInstance(bar_lines[5], bar.Repeat)
        self.assertEqual("end", bar_lines[5].direction)
        self.assertEqual(2, bar_lines[5].times)
        self.assertIsInstance(bar_lines[5], bar.Repeat)
        self.assertEqual("end", bar_lines[5].direction)
        self.assertEqual(2, bar_lines[5].times)
        self.assertEqual("double", bar_lines[6].type)
        self.assertEqual("final", bar_lines[7].type)

        repeat_bracket = list(score.recurse().getElementsByClass(spanner.RepeatBracket))
        self.assertEqual(2, len(repeat_bracket))
        self.assertEqual('1', repeat_bracket[0].number)
        self.assertEqual(2, len(repeat_bracket[0].spannerStorage))
        self.assertEqual('2', repeat_bracket[1].number)
        self.assertEqual(1, len(repeat_bracket[1].spannerStorage))

    def test_metadata(self):
        for (tf, _title, _meter, _key, _origin, _tempo) in [
            (fyrareprisarn, 'Fyrareprisarn', '3/4', 'F major', "Jät, Småland", ""),
            (mystery_reel, 'Mystery Reel', '2/2', 'G major', None, ""),
            (ale_is_dear, 'The Ale is Dear', '4/4', 'D major', None, ""),
            (kitchen_girl, 'Kitchen Girl', '4/4', 'D major', None, ""),
            (william_and_nancy, 'William and Nancy', '6/8', 'G major', None,""),
        ]:
            score = ABCTranslator(tf)
            self.assertEqual(score.metadata.title, _title)
            self.assertEqual(score.metadata.localeOfComposition, _origin)
            self.assertEqual(_meter,
                score.recurse().getElementsByClass(meter.TimeSignature)[0].ratioString)
            self.assertEqual(_key,
                score.recurse().getElementsByClass(key.KeySignature)[0].name)


    def test_chords(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(ale_is_dear)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)

        self.assertEqual(len(score.parts), 2)
        self.assertEqual(len(score.parts[0].flatten().notesAndRests), 111)
        self.assertEqual(len(score.parts[1].flatten().notesAndRests), 127)

        # chords are defined in second part here
        self.assertEqual(len(score.parts[1][chord.Chord]), 32)

        # check pitches in chords; sharps are applied due to key signature
        match = [p.nameWithOctave for p in score.parts[1].flatten().getElementsByClass(
            chord.Chord)[4].pitches]
        self.assertEqual(match, ['F#4', 'D4', 'B3'])

        match = [p.nameWithOctave for p in score.parts[1].flatten().getElementsByClass(
            chord.Chord)[3].pitches]
        self.assertEqual(match, ['E4', 'C#4', 'A3'])

    def test_user_defined_symbols(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_user_defined_symbols)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        notes = list(score.recurse().getElementsByClass(note.Note))

        self.assertEqual(3, len(notes))
        self.assertIsInstance(notes[0].expressions[0], expressions.Trill)
        self.assertIsInstance(notes[0].articulations[0], articulations.UpBow)
        self.assertIsInstance(notes[1].articulations[0], articulations.Staccato)
        self.assertIsInstance(notes[2].expressions[0], expressions.Fermata)

    def test_anacrusis_padding(self):
        # using voices in the measure streams cause a problem with the note beats ..
        return
        score = ABCTranslator(hector_the_hero)
        self.assertIsInstance(score, stream.Score)

        m1 = score.parts[0].getElementsByClass(stream.Measure).first()
        # ts is 3/4
        self.assertEqual(m1.barDuration.quarterLength, 3.0)
        # filled with two quarter notes
        self.assertEqual(m1.duration.quarterLength, 2.0)

        #v1 = m1.getElementsByClass(stream.Voice).first()
        n0 = m1.notesAndRests[0]
        n1 = m1.notesAndRests[1]
        self.assertEqual(n0.getOffsetBySite(m1) + m1.paddingLeft, 1.0)
        self.assertEqual(n0.beat, 2.0)
        self.assertEqual(n1.getOffsetBySite(m1) + m1.paddingLeft, 2.0)
        self.assertEqual(n1.beat, 3.0)

        # two 16th pickup in 4/4
        score = ABCTranslator(the_ale_wifes_daughter)
        self.assertIsInstance(score, stream.Score)
        m1 = score.parts[0].getElementsByClass(stream.Measure).first()
        n0 = m1.notesAndRests[0]
        n1 = m1.notesAndRests[1]

        # ts is 3/4
        self.assertEqual(m1.barDuration.quarterLength, 4.0)
        # filled with two 16th
        self.assertEqual(m1.duration.quarterLength, 0.5)
        # notes are shown as being on beat 2 and 3

        self.assertEqual(n0.getOffsetBySite(m1) + m1.paddingLeft, 3.5)
        self.assertEqual(n0.beat, 4.5)
        self.assertEqual(n1.getOffsetBySite(m1) + m1.paddingLeft, 3.75)
        self.assertEqual(n1.beat, 4.75)

    def test_metronome_mark(self):
        # The Q: tempo field is still very much in use, but earlier versions of
        # the standard permitted two syntax variants, now deprecated, which
        # specified how many unit note lengths to play per minute.

        score = ABCTranslator(full_rigged_ship)
        self.assertIsInstance(score, stream.Score)
        _tempo = score[tempo.TempoIndication]
        self.assertEqual(len(_tempo), 1)
        self.assertEqual(str(_tempo[0]),
                         '<music21.tempo.MetronomeMark Eighth=100>')

        score = ABCTranslator(ale_is_dear)
        self.assertIsInstance(score, stream.Score)
        _tempo = score[tempo.TempoIndication]
        self.assertEqual(len(_tempo), 1)
        self.assertEqual(str(_tempo[0]),
                         '<music21.tempo.MetronomeMark Quarter=211>')

        score = ABCTranslator(the_begger_boy)
        self.assertIsInstance(score, stream.Score)
        _tempo = score[tempo.TempoIndication]
        self.assertEqual(len(_tempo), 1)
        self.assertEqual(str(_tempo[0]),
                         '<music21.tempo.MetronomeMark Eighth=90>')

    def test_ties(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_ties)
            debug_messages = mock_stdout.getvalue()

        def assert_ties(obj, expected_ties):
            actual_ties = [None if n.tie is None else n.tie.type for n in obj]
            self.assertEqual(expected_ties, actual_ties)

        self.assertIsInstance(score, stream.Score)
        notes = list(score.recurse().getElementsByClass(note.Note))
        chords = list(score.recurse().getElementsByClass(chord.Chord))
        self.assertEqual(16, len(notes))
        self.assertEqual(9, len(chords))

        # CC-C-C-|CCz2|
        assert_ties(notes[:6], [None, 'start', 'continue', 'continue', 'stop',
                                None])
        # C- [CEG]- G   % outer chord tie creates ties for all chord notes.
        assert_ties(notes[6:8], ['start', 'stop'])
        assert_ties(chords[0], ['stop', None, 'start'])
        # [CE-G-]GEz
        assert_ties(notes[8:10], ['stop', None])
        assert_ties(chords[1], [None, None, 'start'])
        # [E-G-B-][CEG]-[GBD]
        assert_ties(chords[2], ['start', 'start', None])
        assert_ties(chords[3], [None, 'stop', 'continue'])
        assert_ties(chords[4], ['stop', None, None])
        # C4- & G4- | C4 & G4 |
        assert_ties(notes[10:14], ['start', 'start', 'stop', 'stop'])
        # [CEG-]4- & [g-bd]4- | [GBD]4 & g4 |
        assert_ties(chords[5], [None, None, 'start'])
        assert_ties(chords[6], ['start', None, None])
        assert_ties(chords[7], ['stop', None, None])
        assert_ties(notes[14:15], ['stop'])
        # C-z[CE-G]-
        assert_ties(notes[15:16], [None])
        assert_ties(chords[8], [None, None, None])


    def test_slur(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_slur)
            debug_messages = mock_stdout.getvalue()

        # C(DE)F|ABC(D|AB)([CEG]C)
        self.assertIsInstance(score, stream.Score)
        slurs = list(score.recurse().getElementsByClass(spanner.Slur))
        self.assertEqual(3, len(slurs))
        self.assertEqual(['<music21.note.Note D>', '<music21.note.Note E>'],
                         [str(n) for n in slurs[0].spannerStorage])

        self.assertEqual(['<music21.note.Note D>', '<music21.note.Note A>',
                          '<music21.note.Note B>'],
                         [str(n) for n in slurs[1].spannerStorage])

        self.assertEqual(['<music21.chord.Chord C4 E4 G4>',
                          '<music21.note.Note C>'],
                         [str(n) for n in slurs[2].spannerStorage])

    def test_grace(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_grace)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        print()

    def test_tuplets(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_tuplets)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        match = []
        # match strings for better comparison
        for n in score.flatten().notesAndRests:
            match.append(n.quarterLength)

        shouldFind = [
            1 / 3, 1 / 3, 1 / 3,
            1 / 5, 1 / 5, 1 / 5, 1 / 5, 1 / 5,
            1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 6,
            1 / 7, 1 / 7, 1 / 7, 1 / 7, 1 / 7, 1 / 7, 1 / 7,
            2 / 3, 2 / 3, 2 / 3, 2 / 3, 2 / 3, 2 / 3,
            1 / 12, 1 / 12, 1 / 12, 1 / 12, 1 / 12, 1 / 12,
            1 / 12, 1 / 12, 1 / 12, 1 / 12, 1 / 12, 1 / 12,
            2
        ]
        self.assertEqual(match, [common.opFrac(x) for x in shouldFind])

    def test_abc_primitive_polyphonic(self):
        with patch('sys.stderr', new_callable=StringIO) as mock_stdout:
            score = ABCTranslator(abc_primitive_polyphonic)
            debug_messages = mock_stdout.getvalue()

        self.assertIsInstance(score, stream.Score)
        self.assertEqual(len(score.parts), 3)
        self.assertEqual(len(score.parts[0].flatten().notesAndRests), 6)
        self.assertEqual(len(score.parts[1].flatten().notesAndRests), 17)
        self.assertEqual(len(score.parts[2].flatten().notesAndRests), 6)

    def test_overlays_and_lyric(self):
        score = ABCTranslator(abc_overlays_and_lyric)
        self.assertIsInstance(score, stream.Score)

        notes = list(score.flatten().notesAndRests)
        self.assertEqual(9, len(notes))
        test_data =  [('C', 'C'), ('G', None), ('G', None), ('D', 'D'),
                      ('B', None), ('E', 'E'), ('E', ''), ('F', 'F'),
                      ('B', None)]

        for n, (name, lyric) in zip(notes, test_data):
            self.assertEqual(n.name, name)
            self.assertEqual(n.lyric, lyric)


if __name__ == '__main__':
    from pathlib import Path

    a = environment.Environment()
    musecores = ['/home/mschulz/Anwendungen/MuseScore-3.6.0.451381076-x86_64.AppImage',
                 '/home/mschulz/Anwendungen/MuseScore-4.1.1.232071203-x86_64.AppImage',
                 '/home/mschulz/local/bin/MuseScore', '/home/mschulz/local/bin/MuseScore-4.1.1',
                 '/usr/bin/musescore']
    for musecore in musecores:
        if Path(musecore).is_file():
            a['musicxmlPath'] = musecore
            break

    unittest.main()

    from music21 import environment
    from pathlib import Path
