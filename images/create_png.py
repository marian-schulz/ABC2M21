# Importing the module
import os
from pathlib import Path
from abc_to_music21 import abc_translator, ABC2M21_CONFIG
from abc_to_music21 import testtunes
from music21 import environment, converter
import re
a = environment.Environment()
a['debug'] = True
ABC2M21_CONFIG['simplifiedComplexMeter'] = True

DOCUMENT_FILE = Path('../documentation.md')
MARKDOWN_ABC_RE = re.compile(r"```abc:([a-zA-Z0-9_]*)\n(.*?)```", re.DOTALL)

with DOCUMENT_FILE.open('r') as f:
    markdown_doc = f.read()

abc_fragments : dict[str, str]= {
    'twinkle': testtunes.twinkle
}

# Search in doc
for abc_match in MARKDOWN_ABC_RE.finditer(markdown_doc):
    abc_name, abc_text = abc_match.groups()
    abc_fragments[abc_name] =  abc_text


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

#s = ABCTranslator(abc_fragments['part'])
#s.show()
#exit()

# delete old pngs but bob
for filename in os.listdir():
    if filename.endswith(".png") and filename != "bob.png":
        os.remove(filename)

for abc_name, abc_text in abc_fragments.items():
    m21_stream = abc_translator(abc_text)
    xmlconv = converter.subConverters.ConverterMusicXML()
    xmlconv.write(m21_stream, fmt='musicxml', fp=f"{abc_name}.png", subformats=['png'], trimEdges=True)


# delete all except png and py files & move musicxml
for filename in os.listdir():
    if filename.endswith(".py"):
        continue

    if filename.endswith(".png"):
        if filename.endswith("-1.png"):
            os.rename(filename, f"{filename[:-6]}.png")
        continue

    os.remove(filename)
