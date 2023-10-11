# Importing the module
import os
from pathlib import Path
from ABC2M21 import ABCTranslator, ABC2M21_CONFIG
from ABC2M21 import testtunes
from music21 import environment, converter
a = environment.Environment()

ABC2M21_CONFIG['simplifiedComplexMeter'] = True

abc_tunes = ['abc_propagate_accidentals', 'abc_twinkle', 'abc_pitch_octaves',
             'abc_accidentals', 'abc_decoration_spanner', 'abc_note_duration', 'abc_meter',
             'abc_user_defined_symbols', 'abc_broken_rhythm', 'abc_dynamics', 'abc_unit_note_length',
             'abc_expressions', 'abc_articulations', 'abc_repeat_marker', 'abc_rests',
             'abc_legacy_chord_and_decoration', 'abc_ave_maria', 'abc_fingerings',
             'abc_bar_lines', 'abc_slur', 'abc_simple_ties', 'abc_simple_grace', 'abc_tempo',
             'abc_atholl_brose', 'abc_auto_trill_spanner', 'abc_tuplets', 'abc_extended_tuplet',
             'abc_shorthand_decorations', 'abc_chord_example', 'abc_unison', 'abc_chord_symbols',
             'abc_chord_dialect', 'abc_full_rigged_ship', 'abc_hector_the_hero', 'abc_mystery_reel',
             'abc_william_and_nancy', 'abc_kitchen_girl', 'abc_fyrareprisarn', 'abc_ale_is_dear',
             'abc_the_begger_boy', 'abc_the_ale_wifes_daughter',
             ]

musecores = ['/home/mschulz/Anwendungen/MuseScore-3.6.0.451381076-x86_64.AppImage',
             '/home/mschulz/Anwendungen/MuseScore-4.1.1.232071203-x86_64.AppImage',
             '/home/mschulz/local/bin/MuseScore', '/home/mschulz/local/bin/MuseScore-4.1.1',
             '/usr/bin/musescore']

for musecore in musecores:
    if Path(musecore).is_file():
        a['musicxmlPath'] = musecore
        a['musescoreDirectPNGPath'] = musecore
        break

# Getting the current working directory
cwd = os.getcwd()

#s = ABCTranslator(testtunes.abc_accidentals)
#s.show()
#exit()

# delete old pngs
for filename in os.listdir():
    if filename.endswith(".png"):
        os.remove(filename)

for name in abc_tunes:
    if not name.startswith('abc_'):
        continue

    abc_tune = getattr(testtunes, name)
    m21_stream = ABCTranslator(abc_tune)
    xmlconv = converter.subConverters.ConverterMusicXML()
    xmlconv.write(m21_stream, fmt='musicxml', fp=f"{name[4:]}.png", subformats=['png'], trimEdges=True)


# delete all except png and py files & move musicxml
for filename in os.listdir():
    if filename.endswith(".py"):
        continue
    if filename.endswith(".musicxml"):
        os.rename(filename, f'../musicxml/{filename}')
        continue

    if filename.endswith(".png"):
        if filename.endswith("-1.png"):
            os.rename(filename, f"{filename[:-6]}.png")
        continue

    os.remove(filename)
