# Importing the module
import os
from pathlib import Path
from ABC2M21 import ABCTranslator
from ABC2M21 import testtunes
from music21 import environment, converter
a = environment.Environment()

abc_tunes = ['abc_propagate_accidentals', 'abc_twinkle', 'abc_pitch_octaves',
             'abc_accidentals', 'abc_decoration_spanner', 'abc_note_duration',
             'abc_user_defined_symbols', 'abc_broken_rhythm', 'abc_dynamics',
             'abc_expressions', 'abc_articulations', 'abc_repeat_marker', 'abc_rests',
             'abc_legacy_chord_and_decoration', 'abc_ave_maria']

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

#s = ABCTranslator(abc_propagate_accidentals)
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


# delete all except png and py files
for filename in os.listdir():
    if filename.endswith(".py"):
        continue
    if filename.endswith(".png"):
        if filename.endswith("-1.png"):
            os.rename(filename, f"{filename[:-6]}.png")
        continue

    os.remove(filename)
