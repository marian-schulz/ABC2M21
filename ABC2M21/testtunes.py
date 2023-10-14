abc_tune_header_and_file_structure = """
A:Area             % depricated (mapped to Origin)
B:Book
C:Composer
D:Discography
F:File URI
G:Groups
H:History
I:linebreak $      % An instruction
%%linebreak $      % Directive (same as I:linebreak) 
K:Cm               % Key is not a file header field
L:1/4              % Unit note length
M:C                % Meter
m:$Bach = _BAcB    % Macro
N:Notes
O:Origin
P:X                % Part Field is not not a file header field
Q:1/4=120          % Tempo is not not a file header field
R:Rhythm
r:remark           % Skipped by the tokenizer
S:Source
s:!trill! - - -    % Symbol line is not a file header field
T:Tuneheader       % Titel is not not a file header field
U:m=!mordent!      % User defined
V:Viola            % Voice is not not a file header field
W:Words            % Words is not not a file header field
w:lyrics           % lyrics is not not a file header field
Z:Transcription

After an empty line you may write as many 'Free Text' you want
until a Tune starts with the X: Field. The abc parser ignores freetext.

X:1                % Tuneheader starts
T:Example 1        % ABC Standart says the Titel must follow immediately after the X: (soft requirement)
K:                 % Tune header stops with the K: field
$Bach              % Bach motive defined by macro
w:B- A- c- H       % Lyric line
%A tune ends after an empty line (A comment line is not an empty line)

This is free text again until the next Tune starts with the X: Field

X:2
T:Example 2
K:
% Having an empty abc tune is legal but removed from the abc parser               
"""

abc_note_duration = """
[L:1/4] C4   C3   C2   C3/2  C    C/2  C//   C///  C////
"""

abc_decoration_spanner = """
L:1/4
K:C
!<(!ABCD!<)! !>(!ABCD!>)! !trill(!ABCD!trill)!|
"""

abc_user_defined_symbols = """
L: 1/4
T: User defined symbols
U: W = !trill!
U: U = !staccato!
U: V = !fermata!
K:C
WC UD VE .F
"""

abc_chord_symbols = """
"A"A2 "Am"A2 "A7"A2 "Amaj7"A2 "A+"A2
"""

abc_legacy_chord_and_decoration = """
K:C
+CEG+
I:decoration +  % Set '+' als decoration denotation symbol
+CEG+           % But now, the legacy chord symbol '+' is disabled
+trill+C        % this is now a legal trill decoration
"""

abc_chord_dialect = """
+CEG+           
"""

abc_legacy_decoration_2_0 = """
%abc-2.0 
X:1
K:
+trill+C        % This is the way to write decorations in abc 2.0 
+++D            % this is illegal,
+plus+F         % but this will work
!+!G            % using ! should still work in 2.0
I:decoration +
!plus!A         % even after set the decoration symbol explicit to +
"""

abc_decoration_instruction = """
%abc-2.1
X:1
K:
+trill+C        % This is not 2.1 syntax
I:decoration +  % After setting the decoration symbol +
+plus+E         % This will work now
!trill!G        % And using ! for decorations will still work too
"""

line_continue_2_0 = """% In abc 2.0 there was a universal continuation character
X:1
T:Line\\
Continue        % continues field lines
%%linebreak\\
 $              % continue directives
K:
c               % this will create a score line break (newline)
C\              % Continue music code without a score line break
B               % this will create a score line break (newline)
"""

line_continue = """%abc-2.1
X:1
T:Line
+:Continue      % continues field lines, add a white Space between the parts
K:
E               % this will create a score line break
C               % Continue music code without a score line \\
B               % this will create a score line break
%this instruction allows a Scoreline break with $ and !
I:linebreak $
+:!             % to continue a directive use the 'I:' instruction field and use +:
AG$F!D
"""

abc_rests = """
L:1/4
M:C
z z2 z/2 z/4 z/4 | x x2 x/2 x/4 x/4 | Z | X | Z2 | X2 |
"""

tunebook_with_macros = """T: titel_file
m: ~C={g}C
U: W = !trill!
X: bla
T: Macro tune 1
U: W = !fermata!
K:
WC~C
X: 2
T: Macro tune 2
m:~C={g}c
K:
!>!C~C
X: 2
m:~C="C"~C
K:
WC~C
"""

abc_auto_trill_spanner = """
X: 
L: 1/4
M:C
K:C
C TE T[CEG] TF | TE CEG |
"""

abc_trills = """%abc-1.9
X: 
T: Tune with trills
L: 1/4
C: Marian Schulz
M:C
K:C
%% Measure with 2 trills using the !trill! decoration
!trill![CEG] E !trill!C F |
%% Measure with 2 trills using user defined Symbol 'T'
T[CEG] E TC F |
%% A trill spanner
EC !trill(! E F !trill)! |
%% The parser recognizes neighboring notes with
%% trills and converts them into trill spanners.
C TE T[CEG] TF | TE CEG |
"""

abc_overlays_and_voices = """
X:0
T:Voices and voice overlays
C:Marian Schulz
M:C
L:1/4
K:D
V:1
C/2C/2E2E & FFAA | [CEG]GGG
V:2
DDDD | AAAA & CC'CC'
"""

abc_spanner = """
X:1
U:t = !trill!
L:1/4
M:4/4
K:E
!<(!ABCD!<)! | !>(!ABCD!>)! | !trill(! ABCD | A!trill)!BCAB |
"""

abc_tempo = """
L:1/1
[Q:1/2=120]E | [Q:"Allegro" 1/4=120]F | [Q: 3/8=50 "Slowly"]G | [Q:"Andante"]A | [Q:120]B | 
"""

abc_unit_note_length = """
[L:1/1] C [L:1/2] C [L:1/4] C [L:1/8] C [L:1/16] C [L:1/32] C 
"""

abc_broken_rhythm = """
L:1/4
>F>FA<A | G<<GB>>B | C>>>C D<<<D | [CEG]>E E<[EGB] |
[BDF]>[DFA] [BDF]<[DFA] | E>D [BDF]<D | E>{CEG2}D [BDF]<{CE>G}D | D> |
"""

abc_fingerings = """
!1!E !2!G !3!E !4!F !5!G 
"""

abc_decorations = """
X: 0
L: 1/4
C: Marian
T: Tune with decoratiońs
M: C
K:
!arpeggio![CEG]!pralltriller!C !lowermordent!C !uppermordent!C | 
!mordent!C !fermata!C !invertedfermata!C !tenuto!C |
!straccent!C !emphasis!C !upbow!C !downbow!C |
!staccato!!trill![CEG] !open!C !turn!E !slide!F |
 !+!C !snap!D !nail!F !marcato!C |  !>!D !^!e !unknown!F !invertedmordent!C | 
!segno!C !coda!D !D.S.alcoda!d !D.C.alcoda!d !fine!f !D.S.alfine!e
!D.C.alfine!e !dacapo!g !D.S.!e  
!p!e !pp!e !ppp!e !pppp!e !f!e, !ff!e !fff!e !ffff!e !mp!e !mf!e !sfz!e
"""

abc_dynamics = """
[L:1/4]
!p!C !pp!C !ppp!C !pppp!C !f!C !ff!C !fff!C !ffff!C !mp!C !mf!C !sfz!C
"""

abc_expressions = """
L:1/4
K:C
  !invertedfermata!C !trill!C !mordent!C !fermata!C !turn!C !invertedturn!C !arpeggio!'[CEG] !slide!C !uppermordent!C | !tremolo!C
w:!invertedfermata!  !trill!  !mordent!  !fermata!  !turn!  !invertedturn!  !arpeggio!       !slide!  !uppermordent!  | !tremolo!  
"""

abc_articulations = """
L:1/4
K:C
!staccato!C  !>!C !downbow!C !^!C !breath!C !tenuto!C !upbow!C !open!C !+!C !snap!C !nail!C !doit! C !thumb!C| !cesura!C| 
w:!staccato! !>!  !downbow!  !^!  !breath!  !tenuto!  !upbow!  !open!  !+!  !snap!  !nail!  !doit!   !thumb!   !cesura!
"""

abc_repeat_marker = """
L:1/4
K:C
  !segno!C  | !coda!C | !fine!C | !D.S.!C | !D.S.alcoda!C | !D.S.alfine!C | !dacapo!C | !D.C.alcoda!C |
w:!segno!     !coda!    !fine!    !D.S.!    !D.S.alcoda!    !D.S.alfine!    !dacapo!    !D.C.alcoda!
"""

abc_bar_lines = """
X:1
M:4/4
L:1/4
K:C
|: EGBc [| cega :: CEGA ::|[1 de BA | defg :|[2 de dB || abcd |]
"""

abc_grace= """
X:2
L:1/4
K:D
{g2c}C {/hc}D 
"""

abc_chords = """
X:2
T: Chords
L: 1/4
K:D
[C/2EG]8 | [CEG]4 | [C/4EG]4 [C/2EG]2 [CEG]2
"""

abc_unison = """
[DD]
"""
abc_extended_tuplet = """
K:C
(3:2:4 G2A2Bc
"""

abc_chord_example = """
( "^I" !f! [CEG]- > [CEG] "^IV" [F=AC]3/2"^V"[GBD]/  H[CEG]2 )
"""

abc_tuplets = """
(3.c=c^c (5ccc=cc (6ccccc=f (7Bcc^^c=cc^f
(3.c2=c2^c2 (3.c2=c2^c2
(6c/c/c/c/c/=f/ (6B/c/c/^^c/c/^f/ z4
"""

abc_shorthand_decorations = """
[L:1/4]
(3.a.b.c vAuBvA T[DFA]
"""

abc_primitive_polyphonic = '''M:6/8
L:1/8
K:G
V:1 name="Whistle" snm="wh"
B3 A3 | G6 | B3 A3 | G6 ||
V:2 name="violin" snm="v"
BdB AcA | GAG D3 | BdB AcA | D6 ||
V:3 name="Bass" snm="b" clef=bass
D3 D3 | D6 | D3 D3 | D6 ||
'''

abc_the_begger_boy = '''
X:5
T:The Begger Boy
R:Jig
H:The tune name may derive from the song "The Begger Boy of the North"
H:(c. 1630)
N:This tune is in the rare Phrygian mode--suggested chords are given
M:6/8
L:1/8
Q:90
K:APhry
AAAf2f|ec2d2c|AF2G2G|A2B cA2||
AAAf2f|ec2d2c|Ac2ede|fA2G3|
Acc e>dc|dfg/2f/2 efd|cAF G2G|A2B cA2||
W:From ancient pedigree, by due descent
W:I well can derive my generation
W:Throughout all Christendome, and also Kent
W:My calling is known both in terme and vacation
W:My parents old taught me to be bold
W:Ile never be daunted, whatever is spoken
W:Where e're I come, my custome I hold
W:And cry, Good your worship, bestow one token!
W:--Roxburghe Ballads
'''

abc_ale_is_dear = '''%  <A name="D1X180"></A>
X: 180
T:Ale is Dear, The
M: 4/4
L: 1/8
R:Reel
Q:1/4=211
% Last note suggests Locrian mode tune
K:D % 2 sharps
% (c) SSF January 2006
V:1
f2 ef B2 fe| \
fa ef cA ec| \
f2 ef B2 fe| \
fa ec B2 Bc|
f2 ef B2 fe| \
fa ef cA ec| \
f2 ef B2 fe| \
fa ec B2 Bc|
B3/2B<Bc/2 d2 cB| \
A3/2A<AB<AB/2 c<A| \
B3/2B<Bc/2 d2 cB| \
f<a e3/2c/2 B2 B2|
B3/2B<Bc/2 d2 cB| \
A3/2A<AB<AB/2 c<A| \
d2 f3/2d/2 c2 e3/2c/2| \
d<f e3/2c<BB<Bc/2|
V:2
% Chords
B,,z [FDB,]z B,,z [FDB,]z| \
B,,z [FDB,]z A,,z [ECA,]z| \
B,,z [FDB,]z B,,z [FDB,]z| \
B,,z [ECA,]z B,,z [FDB,]z|
B,,z [FDB,]z B,,z [FDB,]z| \
B,,z [FDB,]z A,,z [ECA,]z| \
B,,z [FDB,]z B,,z [FDB,]z| \
B,,z [ECA,]z B,,z [FDB,]z|
B,,z [FDB,]z B,,z [FDB,]z| \
A,,z [ECA,]z A,,z [ECA,]z| \
B,,z [FDB,]z B,,z [FDB,]z| \
B,,z [ECA,]z B,,z [FDB,]z|
B,,z [FDB,]z B,,z [FDB,]z| \
A,,z [ECA,]z A,,z [ECA,]z| \
B,,z [FDB,]z A,,z [ECA,]z| \
B,,z [ECA,]z B,,z [FDB,]
'''

abc_fyrareprisarn = '''
%%abc-charset utf-8
X: 1
T: Fyrareprisarn
O: Jät, Småland
S: efter August Strömberg
D: Svensson, Gustafsson mfl - Bålgetingen
Z: Till abc av Jon Magnusson 100517
R: Hambo
M: 3/4
L: 1/8
K: F
c2 a>g f>e|d>c BA G>F|E>F GA B>c|d>c AB c>c|
c>a a>g f>e|d>c BA G>F|E>F Gd c>E|F2 f4::
{A}d>^c de f>g|e>f de =c>A|A>B AG FE|DE FG A>A|
d>^c de fg|e>f de =c>A|A>B AG FE|D2 d4::
c2 f2 c>c|B>d B4|G>c e2 c>e|f>>g a>f c2|
c2 f2 c>c|B>d g4|G2 e>g c>>>e|f2 f4::
f>f f4|e>e e3A|A>B AG FE|D>E FD E2|
f>f f4|e>e e3A|A>B AG FE|D2 d4:|
'''

abc_kitchen_girl = '''X: 57
T:Kitchen Girl
% Nottingham Music Database
S:via PR
M:4/4
L:1/4
K:D
"A"[c2 a2 ]"G"[B2g2]|"A"e/2f/2e/2d/2 cc/2d/2|"A"e/2c/2e/2f/2 "G"g/2a/2b/2a/2|\
"E"^ge ee/2=g/2|
"A"a/2b/2a/2f/2 "G"g/2a/2g/2f/2|"A"e/2f/2e/2d/2 c/2d/2e/2f/2|\
"G"gd "E"e/2f/2e/2d/2|"A"cA A2::
"Am"=cc/2A/2 "G"B/2A/2G/2B/2|"Am"A/2B/2A/2G/2 E/2D/2E/2G/2|\
"Am"A/2G/2A/2B/2 "C"=c/2B/2c/2d/2|"Em"ee/2g/2 e/2d/2B/2A/2|
"Am"=cc/2A/2 "G"B/2A/2G/2B/2|"Am"A/2B/2A/2G/2 E/2D/2E/2G/2|\
"Am"=c/2B/2A/2c/2 "G"B/2A/2G/2B/2|"Am"A3/2B/2 A2:|
'''


# http://abcnotation.com/tunePage?a=abc.sourceforge.net/NMD/nmd/morris.txt/0030
# noinspection SpellCheckingInspection
abc_william_and_nancy = '''X: 31
T:William and Nancy
% Nottingham Music Database
P:A(AABBB)2(AACCC)2
S:Bledington
M:6/8
K:G
P:A
D|"G"G2G GBd|"C"e2e "G"dBG|"D7"A2d "G"BAG|"C"E2F "G"G2:|
P:B
d|"G"e2d B2d|"C"gfe "D7"d2d|"G"e2d B2d|"A7""C"gfe "D7""D"d2c|
"G""Em"B2B Bcd|"C"e2e "G"dBG|"D7"A2d "G"BAG|"C"E2F "G"G2:|
P:C
"G"d3 "C"e3|"G"d3 "Em"B3|"G"d3 "C"g3/2f3/2|"C"e3 "G"d3|"D7"d3 "G"e3|"G"d3 B2d|\
"A7""C"gfe "D7""D"d2c|
"G""Em"B2B Bcd|"C"e2e "G"dBG|"D7"A2d "G"BAG|"C"E2F "G"G2:|
'''

# http://abcnotation.com/tunePage?a=www.fiddletech.com/music/abcproj/0253
# noinspection SpellCheckingInspection
abc_mystery_reel = '''
X:254
T:Mystery Reel
R:reel
Z:transcribed by Dave Marshall
M:C|
K:G
|: egdB A3B | ~G3B A2Bd | e2dB A2BA |1 GEDE GABd :|2 GEDE GBdc |
|: B~G3 GEDG | BGAB GEDG | A2GB A2GA |1 Bdef gedc :|2 Bdef gedB |
|: ~G3E DEGB | dBGB A~E3 | GAGE DEGF | GBdB A2G2 :|
| gede g2ag | egde ge (3eee | gede g2ag | egde ~g3a |
gede g2ag | egde ge (3eee | ~g3e a2ba | ge (3eee b2ag |
'''

abc_hector_the_hero = '''X: 48
T:Hector the Hero
M:3/4
L:1/8
C:Scott Skinner
K:A
A2B2|:"A"c3 BA2|"D"f4ec|"A"e4-ef|e4AB|\
"F#m"c4BA|"D"f4ec|"Bm"B4-Bc|"E"B4ce|
"F#m"c3 BA2|"D"f4ec|"A"e4A2|"D"a4f2|\
"A"e4Ac|"E"B4A2|"A"A6 -|[1 A2A2B2:|[2 A2c2e2
||:"D"f4df|a4gf|"A"e4-ef|e4ce|\
"F#m"f4ec|e4Ac|"Bm"B4-Bc|"E"B4ce|
"D"f4df|a4gf|"A"e4dc|"D"a4d2|\
"A"c4Ac|"E"B4A2|"A"A6 -|[1 A2c2e2:|[2 A2 z2||
'''


abc_full_rigged_ship = '''X: 1
T:Full Rigged Ship
M:6/8
L:1/8
Q:100
C:Traditional
S:From The Boys of the Lough
R:Jig
O:Boys Of The Lough
A:Shetland
D:Boys of the Lough "Wish You Were Here"
K:G
|:e2a aea|aea b2a|e2f~g3|eag fed|
e2a aea|aea b2a|~g3 edB|A3A3:|!
|:efe edB|A2Bc3|BAG BAG|BcdE3|
efe edB|A2Bc2d|efe dBG|A3A3:|!
|:EFE EFE|EFE c3|EFE E2D|E2=F GEC|
EFE EFE|EFE c2d|efe dBG|A3A3:|
'''

abc_the_ale_wifes_daughter = '''X:1
T:The Ale Wife's Daughter
Z:Jack Campin: "Embro, Embro", transcription (c) 2001
F:17riot/abc/AleWife.abc
S:John Hamilton: A Collection of Twenty-Four Scots Songs (Chiefly Pastoral.), 1796
B:NLS Glen.311
M:C
L:1/8
Q:1/4=80
N:Slow and Supplicative
K:G Mixolydian
(E/F/)|G<G GE  GA  c>B|A>A A>G Ac d3/ (c//d//)| e>g          d>e c>d e>d|cA A>G G3||
(c/d/)|e<e e>c e>f g>e|d>d d>c de f3/ (e//f//)|(g/f/) (e/f/) ed  c>d e>d|cA A>G G3|]
'''

abc_key_signature = """
X: 2
T: Key signatures
M: 4/4
L: 1/8
K:
[K:C#]"^C# major"CDEFGABc | [K:D]"^D major"CDEFGABc | [K:Eb]"^E- major"CDEFGABc | 
[K:F#]"^F# major"CDEFGABc | [K:G]"^G major"CDEFGABc | [K:Ab]"^A- major"CDEFGABc |
[K:B]"^B major"CDEFGABc | [K:C]"^C major"CDEFGABc | [K:Db]"^D- major"CDEFGABc |
[K:E]"^E major"CDEFGABc | [K:F]"^F major"CDEFGABc | [K:Gb]"^G- major"CDEFGABc | 
[K:A]"^A major"CDEFGABc | [K:Bb]"^B- major"CDEFGABc | [K:Cb]"^C- major"CDEFGABc |
[K:C#Ion]"^C# ionian"CDEFGABc | [K:DIon]"^D ionian"CDEFGABc | [K:EbIon]"^E- ionian"CDEFGABc | 
[K:F#Ion]"^F# ionian"CDEFGABc | [K:GIon]"^G ionian"CDEFGABc | [K:AbIon]"^A- ionian"CDEFGABc |
[K:BIon]"^B ionian"CDEFGABc | [K:CIon]"^C ionian"CDEFGABc | [K:DbIon]"^D- ionian"CDEFGABc |
[K:EIon]"^E ionian"CDEFGABc | [K:FIon]"^F ionian"CDEFGABc | [K:GbIon]"^G- ionian"CDEFGABc | 
[K:AIon]"^A ionian"CDEFGABc | [K:BbIon]"^B- ionian"CDEFGABc | [K:CbIon]"^C- ionian"CDEFGABc |
[K:A#Aeo]"^A# aeolian"CDEFGABc | [K:C#Aeo]"^C# aeolian"CDEFGABc | [K:EAeo]"^E aeolian"CDEFGABc | 
[K:GAeo]"^G aeolian"CDEFGABc | [K:BbAeo]"^B- aeolian"CDEFGABc | [K:D#Aeo]"^D# aeolian"CDEFGABc | 
[K:F#Aeo]"^F# aeolian"CDEFGABc | [K:AAeo]"^A aeolian"CDEFGABc | [K:CAeo]"^C aeolian"CDEFGABc | 
[K:EbAeo]"^E- aeolian"CDEFGABc | [K:G#Aeo]"^G# aeolian"CDEFGABc | [K:BAeo]"^B aeolian"CDEFGABc | 
[K:DAeo]"^D aeolian"CDEFGABc | [K:FAeo]"^F aeolian"CDEFGABc | [K:AbAeo]"^A- aeolian"CDEFGABc |
[K:A#m]"^A# minor"CDEFGABc | [K:C#m]"^C# minor"CDEFGABc | [K:Em]"^E minor"CDEFGABc | 
[K:Gm]"^G minor"CDEFGABc | [K:Bbm]"^B- minor"CDEFGABc | [K:D#m]"^D# minor"CDEFGABc | 
[K:F#m]"^F# minor"CDEFGABc | [K:Am]"^A minor"CDEFGABc | [K:Cm]"^C minor"CDEFGABc | 
[K:Ebm]"^E- minor"CDEFGABc | [K:G#m]"^G# minor"CDEFGABc | [K:Bm]"^B minor"CDEFGABc | 
[K:Dm]"^D minor"CDEFGABc | [K:Fm]"^F minor"CDEFGABc | [K:Abm]"^A- minor"CDEFGABc |
[K:G#Mix]"^G# mixolydian"CDEFGABc | [K:BMix]"^B mixolydian"CDEFGABc | [K:DMix]"^D mixolydian"CDEFGABc  |
[K:FMix]"^F mixolydian"CDEFGABc | [K:AbMix]"^A- mixolydian"CDEFGABc | [K:C#Mix]"^C# mixolydian"CDEFGABc |
[K:EMix]"^E mixolydian"CDEFGABc | [K:GMix]"^G mixolydian"CDEFGABc | [K:BbMix]"^B- mixolydian"CDEFGABc |
[K:DbMix]"^D- mixolydian"CDEFGABc | [K:F#Mix]"^F# mixolydian"CDEFGABc | [K:AMix]"^A mixolydian"CDEFGABc | 
[K:CMix]"^C mixolydian"CDEFGABc | [K:EbMix]"^E- mixolydian"CDEFGABc | [K:GbMix]"^G- mixolydian"CDEFGABc |
[K:D#Dor]"^D# dorian"CDEFGABc | [K:F#Dor]"^F# dorian"CDEFGABc | [K:ADor]"^A dorian"CDEFGABc |
[K:CDor]"^C dorian"CDEFGABc | [K:EbDor]"^E- dorian"CDEFGABc | [K:G#Dor]"^G# dorian"CDEFGABc | 
[K:BDor]"^B dorian"CDEFGABc | [K:DDor]"^D dorian"CDEFGABc | [K:FDor]"^F dorian"CDEFGABc | 
[K:AbDor]"^A- dorian"CDEFGABc | [K:C#Dor]"^C# dorian"CDEFGABc | [K:EDor]"^E dorian"CDEFGABc | 
[K:GDor]"^G dorian"CDEFGABc | [K:BbDor]"^B- dorian"CDEFGABc | [K:DbDor]"^D- dorian"CDEFGABc |
[K:E#Phr]"^E# phrygian"CDEFGABc | [K:G#Phr]"^G# phrygian"CDEFGABc | [K:BPhr]"^B phrygian"CDEFGABc |
[K:DPhr]"^D phrygian"CDEFGABc | [K:FPhr]"^F phrygian"CDEFGABc |  [K:A#Phr]"^A# phrygian"CDEFGABc |
[K:C#Phr]"^C# phrygian"CDEFGABc | [K:EPhr]"^E phrygian"CDEFGABc | [K:GPhr]"^G phrygian"CDEFGABc |
[K:BbPhr]"^B- phrygian"CDEFGABc | [K:D#Phr]"^D# phrygian"CDEFGABc | [K:F#Phr]"^F# phrygian"CDEFGABc |
[K:APhr]"^A phrygian"CDEFGABc | [K:CPhr]"^C phrygian"CDEFGABc | [K:EbPhr]"^E- phrygian"CDEFGABc |
[K:F#Lyd]"^F# lydian"CDEFGABc | [K:GLyd]"^G lydian"CDEFGABc | [K:AbLyd]"^A- lydian"CDEFGABc |
[K:BLyd]"^B lydian"CDEFGABc | [K:CLyd]"^C lydian"CDEFGABc | [K:DbLyd]"^D- lydian"CDEFGABc |
[K:ELyd]"^E lydian"CDEFGABc | [K:FLyd]"^F lydian"CDEFGABc | [K:GbLyd]"^G- lydian"CDEFGABc |
[K:ALyd]"^A lydian"CDEFGABc | [K:BbLyd]"^B- lydian"CDEFGABc | [K:CbLyd]"^C- lydian"CDEFGABc |
[K:DLyd]"^D lydian"CDEFGABc | [K:EbLyd]"^E- lydian"CDEFGABc | [K:FbLyd]"^F- lydian"CDEFGABc |
[K:B#Loc]"^B# locrian"CDEFGABc | [K:C#Loc]"^C# locrian"CDEFGABc | [K:DLoc]"^D locrian"CDEFGABc |
[K:E#Loc]"^E# locrian"CDEFGABc | [K:F#Loc]"^F# locrian"CDEFGABc | [K:GLoc]"^G locrian"CDEFGABc |
[K:A#Loc]"^A# locrian"CDEFGABc | [K:BLoc]"^B locrian"CDEFGABc | [K:CLoc]"^C locrian"CDEFGABc |
[K:D#Loc]"^D# locrian"CDEFGABc | [K:ELoc]"^E locrian"CDEFGABc | [K:FLoc]"^F locrian"CDEFGABc |
[K:G#Loc]"^G# locrian"CDEFGABc | [K:ALoc]"^A locrian"CDEFGABc | [K:BbLoc]"^B- locrian"CDEFGABc |
"""

abc_meter = """
X:0
L:1/8
M:6/8
K:C
CDEFGA|[M:4/4]CDEFGABc|[M:C]CDEFGABc|[M:C|]CDEFGABc|[M:(2+3+2)/8]CDEFGAB
"""

abc_accidentals = """
L:1/1
   "_sharp"^C "_flat"_D  "_natural"=E  "_double sharp"^^F  "_double flat"__G "_!courtesy!"!courtesy!^C
"""

abc_overlays_and_lyric = """
X: 2
T: Lyrics with overlays
M: 4/4
L: 1/4
K: C
   C D E/2 E/2 F & g/2 g/2 b2 b|
w: C D E-  -   F |
"""

abc_annotations = """
"^Above"C "_Below"D "<Left"E ">Right"F "@Free placement"G
"""

abc_lyrics_1 = """
I:linebreak $
C D E F|
w: doh re mi fa
G A B c|
w: sol la ti doh
"""

abc_lyrics_2 = """
I:linebreak $
C D E F|
G A B c|
w: doh re mi fa sol la ti doh
"""

abc_lyrics_3 = """
I:linebreak $
C D E F|
w: doh re mi fa
G G G G|
w:
F E F C|
w: fa mi re doh
"""

abc_lyrics_4 = """
gf|e2dc B2A2|B2G2 E2D2|
.G2.G2 GABc|d4 B2 |
w: Sa-ys my au-l' wan to your aul' wan,
+: Will~ye come to the Wa-x-ies dar-gle?
"""

abc_verses_1 = """
CDEF FEDC|
w: these are the lyr-ics for verse one
w: these are the lyr-ics for verse two
"""

abc_verses_2 = """
CDEF FEDC|
w: these are the lyr-ics
+:  for verse one
w: these are the lyr-ics
+:  for verse two 
"""

abc_suppress_score_linebreak = """
abc cba|\ % Backslash before the comment
abc cba| % Backslash at the end of the line \\
abc cba| 
"""

abc_score_line_break_symbols = """
abc cba|$abc cba|!abc cba|
"""

abc_line_continue_over_comments = """
abc cab|\\
%%setbarnb 10
M:9/8
%comment
abc cba abc|
"""

spanner = """
X: 1
T:Test spanner
U:t = !trill!
L:1/4
M:4/4
M:4/4
K:E
!<(!ABCD!<)! | !>(!ABCD!>)! | !trill(! ABCD | A!trill)!tBCtAtB |
"""

keysigs = """
X: 1
T:Test keysigs
L:1/8
M:4/4
P:ABAC
K:D
P:A
ABCDEFGA|[K: F]BCDE"C"FGAB|
P:B
CDEFGAAB|[K: C#]DEFGAABC|
P:C
CDEFGAAB|[K: F]DEFG[K: E]AABC|
"""

abc_pitch_octaves = """X:1
L:1/1
K:C
   C, D, E, F, G, A, B, C D E F G A B c d e f g a b c' d' e' f' g' a' b' |
w: C, D, E, F, G, A, B, C D E F G A B c d e f g a b c' d' e' f' g' a' b'
"""

abc_twinkle = """
X:1
T:Twinkle, Twinkle Little Star in C
M:C
K:C
L:1/4
vC C G G|A A G2|F F E E|D D C2|vG G F F|E E D2|
uG G F F|E E D2|vC C G G|A A G2|uF F E E|D D C2|]
"""

abc_propagate_accidentals = """
X:1
T:Propagate-accidentals
M:4/4
L:1/4
K:C
[V:1 name="octave"]
[I:propagate-accidentals octave]
   ^C C  D c | C ^C C  c |
w: C# C# D C | C C# C# C |
[V:2 name="pitch"]
[I:propagate-accidentals pitch]
   ^C C  D c   | C ^C C  c  |
w: C# C# D C#  | C C# C# C# |
[V:3 name="not"]
[I:propagate-accidentals not]
   ^C C  D c | C ^C C c |
w: C# C  D C | C C# C C |
"""

abc_simple_ties = """
X: 1
M: 4/4
L: 1/4
K: C
C-C-[CEG-]G-|[CEG]-[EGB]-B z |
"""

abc_ties = """
X: 1
M: 4/4
L: 1/4
K: C
CC-C-C-|CCz2|
C-[CEG]-Gz| 
[CE-G-]GEz|  
[E-G-B-][CEG]-[GBD]z |
C4- & G4- | C4 & G4 |
[CEG-]4- & [g-bd]4- | [GBD]4 & g4 |
C-z[CE-G]2-    
"""

abc_slur = """
X: 1
M: 4/4
L: 1/4
K: C
C(DE)F|ABC(D|AB).([CEG]C.)|
"""

abc_carry_accidentals = """
X: 1
M: 4/4
L: 1/4
K: G
CF^CD
%|C^C[CEG]F
"""

tempo_in_parts_and_voices = """
X: 1
M: 4/4
L: 1/2
Q: 1/4 = 100
P: AB
K: C
P: A
V:1
AB | [Q: 1/4 = 80]CD
V:2
AB | CD
P: B
V:1
AB | CD
V:2
Q: 1/2 = 200
AB | CD
"""

segno_and_fine = """
X: 1
M: 2/4
L: 1/4
Q: 1/4 = 100
K:
!segno! CE | !fine! DF
"""
ficta = """
X: 1
M: 2/4
L: 1/4
Q: 1/4 = 100
K:
!editorial! ^F^EGA
"""

abc_ave_maria = """%abc-2.1
X:1
T:Ave Maria (Ellen's Gesang III) - Page 1
C:Franz Schubert
%%score 1 (2 | 3)
L:1/8
Q:1/4=26
M:4/4
I:linebreak $
%%MIDI program 1  54
K:Bb
V:1 treble nm="Voice" clef= treble
 z8 | z8 [|: B3 A/B/ (d7/2 c/) | B2 z2 (c2 {dc} B/A/)(G/A/) | B2 z d d3/2(c/4B/4) A/G/ d/=e/ | %5
w: ||A- ve Ma- ri- -|a! Jung- - - frau *|mild! Er- hö- re * ei- ner Jung- frau|
w: ||A- ve Ma- ri- -|a! Un- - - be- -|fleckt! Wenn wir auf * die- sen Fels hin-|
w: ||A- ve Ma- ri- -|a! Rei- - - ne *|Magd! Der Er- de * und der Luft Dä-|
d2 ^c3/2A/ =c3/2B/(3:2:3 (A/c/)d/(3:2:3(e/c/)A/ |$ %6
w: Fle- hen! Aus die- sem Fel- - sen, starr * und|
w: sin- ken zum Schlaf, und uns * dein Schutz * be-|
w: mo- nen, von dei- nes Au- - ges Huld * ver-|
 B3 (d/c/) c3/2A/(3:2:3 (G/=B/)d/(3:2:3 (f/d/)B/ | (c2-(6:4:6 c/G/A/_B/ {cB}A/G/) F2 z F ::| %8
w: wild, soll * mein Ge- bet * zu dir * hin|we- - - - - - - hen. Wir|
w: deckt, wird * weich der har- - te Fels * uns|dün- - - - - - - ken. Du|
w: jagt, sie * kön- nen hier * nicht bei * uns|woh- - - - - - - nen! Wir|
V:2 treble nm="RH"
"^Sehr langsam"!pp!(6:4:6 z/ (.[D/F/].[F/B/]!>!.[B/d/].[F/B/].[D/F/])(6:4:6 z/ (.[D/F/].[F/B/]!>!.[B/d/].[F/B/].[D/F/])!<(!(6:4:6 z/ (.[F/B/].[B/d/]!>!.[d/f/].[B/d/].[F/B/])(6:4:6 z/ (.[_A/d/].[d/f/]!>!.[f/_a/].[d/f/]!<)!.[A/d/]) | %1
!>(!(6:4:6 z/ (.[G/B/].[B/e/]!>!.[e/g/].[B/e/].[G/B/])(6:4:6 z/ (.[_G/=A/].[A/e/]!>!.[e/_g/].[A/e/]!>)!.[G/A/])(6:4:6 z/ (.[F/B/].[B/d/]!>!.[d/f/].[B/d/].[F/B/])(6:4:6 z/ (.[D/F/].[F/B/]!>!.[B/d/].[F/B/].[D/F/]) [|:$ %2
(6:4:6 z/ [D/F/][F/B/][B/d/][F/B/][D/F/](6:4:6 z/ [D/=E/][E/B/][B/d/][E/B/][D/E/](6:4:6 z/ [D/F/][F/B/][B/d/][F/B/][D/F/](6:4:6 z/ [_E/A/][A/c/][c/e/][A/c/][E/A/] | %3
(6:4:6 z/ [D/G/][G/B/][B/d/][G/B/][D/G/](6:4:6 z/ [D/G/][G/B/][B/d/][G/B/][D/G/](6:4:6 z/ [E/G/][G/c/][c/e/][G/c/][E/G/](6:4:6 z/ [E/F/][F/A/][A/c/][F/A/][E/F/] |$ %4
(6:4:6 z/ [D/F/][F/B/][B/d/][F/B/][D/F/](6:4:6 z/ [D/F/][F/B/][B/d/][F/B/][D/F/]!<(!(6:4:6 z/ [D/^F/][F/B/][B/d/][F/B/][D/F/](6:4:6 z/ [D/G/][G/B/][B/d/][G/B/]!<)![D/G/] | %5
!>(!(6:4:6 z/ [=E/G/][G/B/][B/d/][G/B/][E/G/](6:4:6 z/ [E/G/][G/A/][A/^c/][G/A/][E/G/]!>)!(6:4:6 z/ [_E/A/][A/=c/][c/e/][A/c/][E/A/](6:4:6 z/ [E/A/][A/c/][c/e/][A/c/][E/A/] |$ %6
(6:4:6 z/ [D/G/][G/B/][B/d/][G/B/][D/G/](6:4:6 z/ [D/=E/][E/B/][B/d/][E/B/][D/E/](6:4:6 z/ [C/F/][F/A/][A/c/][F/A/][C/F/](6:4:6 z/ [F/G/][G/=B/][B/f/][G/B/][F/G/] | %7
(6:4:6 z/ [F/A/][A/c/][c/f/][A/c/][F/A/](6:4:6 z/ [=E/B/][B/c/][c/=e/][B/c/][E/B/](6:4:6 z/ [F/A/][A/c/][c/f/][A/c/][F/A/](6:4:6 z/ [F/A/][A/c/][c/f/][A/c/][F/A/] | %8
V:3 bass nm="LH"
"_col Pedale" [B,,,B,,] z [B,,,B,,] z [B,,,B,,] z [B,,,B,,] z | %1
 [B,,,B,,] z [B,,,B,,] z [B,,,B,,] z [B,,,B,,] z [|:$ %2
 [B,,,B,,] z [G,,,G,,] z [F,,,F,,] z [F,,,F,,] z | %3
 [G,,,G,,] z [G,,,G,,] z [E,,,E,,] z [F,,,F,,] z |$ %4
 [B,,,B,,] z [B,,,B,,] z [B,,,B,,] z [B,,,B,,] z | %5
 [A,,,A,,] z [A,,,A,,] z [^F,,,^F,,] z [F,,,F,,] z |$ %6
 [G,,,G,,] z [G,,,G,,] z [A,,,A,,] z [D,,D,] z | [C,,C,] z [C,,C,] z [F,,F,] z [F,,F,] z | %8
"""


Magnificat = """%abc-2.1
X: 1
T: Magnificat
T: RV. 610 in Re minore
C: Antonio Vivaldi (1678-1741)
M: 4/4
L: 1/4
Q: "Adagio" 1/4 = 66
V: S clef=treble   name="Soprano"   sname="S"
K: Dm
[V: S] B2 B>B    |HB2=B B/ B/    |=BBA2-  |AAHA2|
"""

lyrics = """
X: 1
T: Lyrics
M: 4/4
L: 1/4
K: C
C D E F|
w: doh re mi fa
G G G G|
w:
F E F C|
w: fa mi re doh
"""

with_lyrics_parts_and_voices = """
X: 1
T: lyrics with multible parts and voices
M: 4/4
L: 1/4
K: C
P:AB
V:1
C D E F|
w: DO RE MI FA
G G G G|
w:
G A B C|
w: SO LA TI DO
w: ohm ohm ohm ohm
V:2
G G G G|
w:  
w: ohm ohm ohm ohm
c d e f|
w: do re mi fa
w: ohm ohm ohm ohm
g a b c|
w: so la ti do
P:B
V:1
C D E F|
w: ha ha ha -
G G G G|
w: - - - -
G A B C|
w: ho ho ho -
V:2
F F F F|
w: - - - -  
c c e e |
w: da da - da
w: di - di di
a a a a|
w: so la la -
"""

lyrics_parts_and_voices = """
X: 1
T: lyrics with multible parts and voices
M: 4/4
L: 1/4
K: C
P:AB
V:1
C D E F|
w: DO RE MI FA
w: ohm ohm ohm ohm
V:2
c d e f|
w: do re mi fa
w: ohm ohm ohm ohm
P:B
V:1
C D E F|
w: ha ha ha -
w: ho ho ho -
V:2
c c e e |
w: da da - da
w: di - di di
"""

clef = """

"""

abc_simple_grace = """
X: 1
L: 1/2
K: C
"^Appoggiatura"{g}E {GdGe}F | "^Acciaccatura"{/g}E {/GdGe}F |
"""

abc_atholl_brose ="""X:2
T:Atholl Brose
%%MIDI program 1  110
Q:1/4=80
% in this example, which reproduces Highland Bagpipe gracing,
%  the large number of grace notes mean that it is more convenient to be specific about
%  score line-breaks (using the $ symbol), rather than using code line breaks to indicate them
I:linebreak $
K:D
{gcd}c<{e}A {gAGAG}A2 {gef}e>A {gAGAG}Ad|
{gcd}c<{e}A {gAGAG}A>e {ag}a>f {gef}e>d|
{gcd}c<{e}A {gAGAG}A2 {gef}e>A {gAGAG}Ad|
{g}c/d/e {g}G>{d}B {gf}gG {dc}d>B:|$
{g}c<e {gf}g>e {ag}a>e {gf}g>e|
{g}c<e {gf}g>e {ag}a2 {GdG}a>d|
{g}c<e {gf}g>e {ag}a>e {gf}g>f|
{gef}e>d {gf}g>d {gBd}B<{e}G {dc}d>B|
{g}c<e {gf}g>e {ag}a>e {gf}g>e|
{g}c<e {gf}g>e {ag}a2 {GdG}ad|
{g}c<{GdG}e {gf}ga {f}g>e {g}f>d|
{g}e/f/g {Gdc}d>c {gBd}B<{e}G {dc}d2|]
"""

field_continue = """
X: 
L:1/4
T:Field \\
T:continue
C:Marian
+:Schulz
K:
C
"""

abc_part = """
X:1
L:1
I:linebreak $
P:((AB)2.C2D)2
M:C
K:C
[P:A]A |
[P:B]B |
[P:C]C |
[P:D]D |$
"""

voices_and_parts = """
X: 0
L: 1/4
T: Voices And Parts
C: Marian Schulz
P: A2BC
M: C
M: C
K: C treble
P: A
V: V1
| aaaa | [M: 3/4]aaa |[M: 4/4] cccc
V: V2 bass
| [M: 4/4] AAAA AAA | [M: 4/4] cccc
P: B
V: V1
| bbbb | [bdg]bbb |
%% This voice has less measures than the other voices
V: V2 name="V2"
| CCCC | CCCC |
P: C
V: V1 name="V1"
| cccc | [M: 3/4] ccc |
%% In Part C there is no voice 2 but voice 22
V: V22 treble name="V22"
| [M: 4/4] CCCC | [M: 3/4] CCC |
"""

#print(list(k for k in locals().keys() if not k.startswith('_')))