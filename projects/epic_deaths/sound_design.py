"""Sound design for "Most Epic Deaths": score cue sheet, stingers, music FX, story SFX, automatic SFX from the
timeline, ambiences. `python3 sound_design.py` renders the score stems and the final mix (mix.wav).

Trigger syntax: 'phrase' = onset of its first word; 'phrase>' = end of its last word; '+0.3' style offsets via opts.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))

import numpy as np  # noqa: E402

import build as B  # noqa: E402
from engine.core import FPS, W  # noqa: E402
from engine.sound import music as MU  # noqa: E402
from engine.sound import mixer  # noqa: E402

# ============================================================ score cue sheet
# (trigger, style, mood, intensity, opts)  -- a cue runs until the next cue (or opts['end'])
MUSIC = [
    ('These are the most epic', 'modern', 'cold', 1, {}),
    ("Now, if you've spent", 'modern', 'groove', 1, {}),
    ("This isn't one of those lists", 'modern', 'build', 2, dict(ramp=(1, 3), end="Let's get into it>")),
    # ---- Harald
    ('Harald Hardrada.', 'viking', 'mystery', 1, {}),
    ('If the Viking Age had a final boss', 'viking', 'heroic', 2, dict(end='So, in case this name')),
    ('So, in case this name is new', 'viking', 'intrigue', 1, {}),
    ('At about fifteen', 'viking', 'speedrun', 2, dict(ending='button', end="And that's just the warm-up>")),
    ('Because in 1066', 'viking', 'intrigue', 1, {}),
    ('So Harald sails for England', 'viking', 'march', 2, dict(end="pretty much thinks he's won>")),
    ("Now, here's the problem with this story", 'viking', 'scholar', 0, {}),
    ('On September 25th', 'viking', 'pastoral', 1, {}),
    ('Meanwhile, the English king has been racing', 'viking', 'tension', 2, dict(ramp=(1, 3), end='So what does the scariest')),
    ('So what does the scariest', 'viking', 'mystery', 1, {}),
    ('First, Harald rides out', 'viking', 'saga', 1, {}),
    ('Then twenty English riders', 'viking', 'tension', 1, dict(ramp=(1, 2), end='Translation')),
    ('Oh, and that rider', 'viking', 'intrigue', 1, dict(end='Harald chooses violence')),
    ('Harald chooses violence', 'viking', 'battle', 3, dict(end='And then an arrow hits him')),
    ("That's it. The last great Viking king", 'viking', 'tragic', 1, {}),
    ('And the English have their own version', 'viking', 'saga_heroic', 2, {}),
    ('It gets worse for Norway', 'viking', 'tension', 1, {}),
    ("But here's the craziest part", 'viking', 'epic', 2, dict(ending='button', end='Not bad for a guy')),
    # ---- Attila
    ('Attila the Hun.', 'hun', 'mystery', 1, {}),
    ("If you're fuzzy on the Huns", 'hun', 'gallop', 2, {}),
    ('He started out sharing the throne', 'hun', 'war', 2, dict(ramp=(2, 3))),
    ('He even had a legendary weapon', 'hun', 'mystic', 1, {}),
    ('And yet, according to Priscus', 'hun', 'feast_light', 1, dict(end='So why is a list')),
    ('In 453', 'hun', 'feast', 2, dict(end='went to bed drunk>')),
    ('During the night', 'hun', 'dread', 1, dict(end='and he choked on it')),
    ('The next morning', 'hun', 'tension', 1, dict(end="So that's the death")),
    ('But the funeral', 'hun', 'funeral_epic', 3, dict(ramp=(2, 3), end='And it worked')),
    ('And it worked', 'hun', 'mystery', 1, dict(end='He walked so every heavy metal')),
    # ---- Crassus
    ('Marcus Licinius Crassus.', 'roman', 'comedic', 1, {}),
    ('How rich?', 'roman', 'heist', 2, {}),
    ("If you've heard of Spartacus", 'roman', 'dark', 2, {}),
    ('But Crassus had a problem', 'roman', 'pomp', 1, dict(end='It did not go well>')),
    ('In 53 BC', 'roman', 'battle_tense', 2, {}),
    ("Crassus's son led a charge", 'roman', 'battle', 3, dict(end='and he was killed')),
    ('Plutarch says about twenty thousand', 'roman', 'tragic', 1, dict(end="And that's not even the wild part")),
    ('The Parthians cut off his head', 'roman', 'theater', 1, dict(end='The richest man in Rome ended up')),
    ('Meanwhile, the Parthian general', 'roman', 'parade', 2, {}),
    ('Oh, and another historian', 'roman', 'mystery', 1, dict(ending='button', end='more than he could swallow>')),
    # ---- Arrichion
    ('Arrichion of Phigalia.', 'greek', 'lyre', 1, {}),
    ('He competed in pankration', 'greek', 'anthem', 2, {}),
    ('If pankration is new to you', 'greek', 'comedic_fight', 1, {}),
    ('No weight classes', 'greek', 'build', 2, dict(end='And the prize')),
    ("And Arrichion wasn't just good at it", 'greek', 'anthem', 2, dict(ramp=(2, 3))),
    ('And in the final, it all goes wrong', 'greek', 'struggle', 2, dict(end='So his coach')),
    ('So his coach is basically yelling', 'greek', 'comedic', 1, dict(end='Respectfully')),
    ('But it worked', 'greek', 'climax', 3, dict(end='Arrichion died from the chokehold')),
    ('So the judges did the only fair thing', 'greek', 'triumph', 2, {}),
    ('About seven hundred years', 'greek', 'lyre', 1, dict(end='But our last guy')),
    # ---- mid-roll
    ('Okay, quick pause', 'lofi', 'lofi', 1, dict(end='Alright. Final entry')),
    # ---- Yi Sun-sin
    ('Yi Sun-sin.', 'korean', 'mystery', 1, dict(end='If you said Horatio Nelson')),
    ("But there's a name", 'korean', 'reveal', 1, {}),
    ('In 1592', 'korean', 'war', 2, {}),
    ('But at sea', 'korean', 'heroic', 2, {}),
    ('At Hansan Island', 'korean', 'battle', 3, dict(end='And as a reward')),
    ('his own government arrested him', 'korean', 'injustice', 1, {}),
    ('Meanwhile, his replacement', 'korean', 'disaster', 2, {}),
    ('So the king, out of options', 'korean', 'resolve', 1, dict(ramp=(1, 2))),
    ('Twelve. Plus one more', 'korean', 'heroic', 2, {}),
    ('At the Battle of Myeongnyang', 'korean', 'epic_build', 2, dict(ramp=(2, 3))),
    ('When the fighting started', 'korean', 'battle', 3, dict(ending='button', end="Yi didn't lose a single ship>")),
    ('Weeks later', 'korean', 'grief', 0, {}),
    ('Which brings us to 1598', 'korean', 'night_battle', 2, dict(ramp=(2, 3), end='a bullet struck Yi')),
    ('He knew right away', 'korean', 'tragic', 1, {}),
    ('His son and his nephew', 'korean', 'drum_rise', 2, dict(ramp=(1, 3))),
    ('The fleet fought on and won', 'korean', 'battle', 3, {}),
    ('Afterward, the Chinese admiral', 'korean', 'tragic', 1, {}),
    ('Think about that', 'korean', 'legacy', 2, dict(ramp=(2, 3), ending='button', end='He earned all of it>')),
    # ---- outro
    ("So, that's part one", 'modern', 'recap', 1, {}),
    ('Now, a quick recap', 'modern', 'groove', 2, dict(end='Sources:')),
    ("And if it's two in the morning", 'modern', 'outro', 1, dict(end='@last')),
]

# (trigger, stinger kind, style, opts)
STINGS = [
    ('final boss', 'boss', 'viking', {}),
    ('becomes King of Norway', 'fanfare', 'viking', dict(at='King of Norway>')),
    ('shine of a whole lot of armor', 'braam', 'viking', {}),
    ('the English king himself', 'dun3', 'viking', {}),
    ("That's it. The last great Viking king", 'death', 'viking', {}),
    ('Not bad for a guy', 'button', 'viking', dict(at='lost to the weather>')),
    ('most feared man in Europe', 'braam', 'hun', {}),
    ('sword of the war god', 'harp_gliss', 'hun', {}),
    ('and he choked on it', 'death', 'hun', dict(at='choked on it')),
    ('Embarrassing', 'sad_trombone', 'hun', dict(at='Embarrassing>')),
    ('the blood of men', 'braam', 'hun', {}),
    ('killed the men who dug', 'dun3', 'hun', dict(at='dug the grave>')),
    ('heavy metal album cover', 'metal', 'hun', dict(at='heavy metal')),
    ('superpower', 'braam', 'roman', {}),
    ('never going to run out', 'dun3', 'roman', dict(at='run out>')),
    ('parting shot', 'rimshot', 'roman', dict(at='parting shot>')),
    ('and he was killed', 'death', 'roman', dict(at='was killed')),
    ('more than he could swallow', 'button', 'roman', dict(at='swallow>')),
    ('in Sparta', 'braam', 'greek', dict(at='Sparta')),
    ("That's a threat", 'button', 'greek', dict(at='threat>')),
    ('Arrichion died from the chokehold', 'death', 'greek', dict(at='died from the chokehold')),
    ('They crowned the corpse', 'fanfare', 'greek', {}),
    ('with an entire fleet', 'braam', 'korean', dict(at='entire fleet')),
    ('If you said Horatio Nelson', 'pomp_fanfare', 'roman', dict(at='Horatio Nelson')),
    ('If you said Captain Hook', 'jig', 'roman', dict(at='Captain Hook')),
    ('most epic death in recorded history', 'braam', 'korean', dict(at='recorded history')),
    ('Your servant still has twelve ships', 'swell', 'korean', dict(at='still has twelve', degree=5, dur=3.4)),
    ('Those who seek death shall live', 'braam', 'korean', {}),
    ('Then the tide turned', 'fanfare', 'korean', {}),
    ('a bullet struck Yi', 'death', 'korean', dict(at='struck Yi')),
    ('Ever.', 'rimshot', 'modern', dict(at='Ever>')),
]

# music FX: tape stops, scratches, drops (silence), muffles (blackout)
MFX = [
    ("Let's get into it>", 'drop', dict(dur=0.6)),
    ("pretty much thinks he's won>", 'tapestop', dict(dur=0.75)),
    ('Translation', 'scratch', {}),
    ('So why is a list', 'scratch', {}),
    ('went to bed drunk>', 'tapestop', dict(dur=1.0)),
    ('It did not go well>', 'tapestop', dict(dur=0.8)),
    ('Arrichion is fading', 'muffle', dict(until='So his coach', f=380.0)),
    ('Respectfully', 'scratch', {}),
    ('please leave', 'scratch', {}),
    ('And as a reward', 'scratch', {}),
]

# Story SFX (trigger, name, gain dB vs voice, opts)
SFX = [
    # intro
    ("he's already dead", 'sub_drop', -12, {}),
    ("Let's get into it>", 'riser', -10, dict(lead=1.4, at_end=True)),
    # Harald
    ('hard ruler', 'sword_shing', -16, {}),
    ('They lose. Olaf dies', 'sub_drop', -14, dict(at='Olaf dies')),
    ('Harald is badly wounded', 'thud', -12, dict(at='badly wounded')),
    ('flees all the way', 'whoosh', -14, {}),
    ('breaks out', 'metal_clang', -9, dict(kw=dict(f0=310.0))),
    ('giant iron chain', 'chain_rattle', -12, {}),
    ('One ship snaps in half', 'wood_crack', -8, dict(at='snaps in half')),
    ('His makes it', 'splash', -14, {}),
    ('marries a princess', 'sparkle', -17, {}),
    ('King of England dies', 'bell', -14, dict(kw=dict(f=392.0, dur=3.0))),
    ('smashes the first English army', 'impact', -10, dict(at='smashes')),
    ('leave their armor back at the ships', 'metal_clang', -16, dict(kw=dict(f0=520.0, dur=1.0), at='armor back')),
    ('40 miles a day', 'gallop', -15, {}),
    ('a cloud of dust rises', 'whoosh', -12, dict(kw=dict(dur=1.2, lo=150, hi=1800))),
    ('his horse stumbles', 'thud', -7, dict(at='throws him to the ground')),
    ('in front of everybody', 'crowd_gasp', -16, {}),
    ('twenty English riders', 'gallop', -14, {}),
    ('swinging with both hands', 'sword_clash', -10, {}),
    ('both hands>', 'sword_clash', -12, dict(seed=3)),
    ('an arrow hits him', 'arrow_hit', -5, dict(at='arrow hits', lead=0.34)),
    ('killed about forty men', 'sword_clash', -12, dict(seed=5)),
    ('stabbed up through the gap', 'thunk', -9, dict(at='stabbed')),
    ('floating barrel', 'splash', -12, {}),
    ('Three days later, William', 'thud', -14, dict(at='lands in the south')),
    ('he dies at the Battle of Hastings', 'arrow_hit', -12, dict(at='Battle of Hastings', lead=0.34)),
    # Attila
    ('horse archers from the steppe', 'gallop', -11, {}),
    ('paying them to go away', 'coins', -13, {}),
    ('2,100 pounds of gold', 'cha_ching', -9, {}),
    ('charging it a subscription', 'notify', -10, dict(at='subscription')),
    ('Bleda died', 'sub_drop', -15, {}),
    ('invaded Italy', 'impact', -13, {}),
    ('found a sword buried', 'sword_shing', -11, {}),
    ('wooden plate', 'coffin_thud', -16, {}),
    ('went to bed drunk>', 'snore', -13, dict(offset=0.9)),
    ('his nose started bleeding', 'heartbeat', -9, dict(kw=dict(n_beats=5, bpm=58, slow=0.6))),
    ('choked on it', 'sub_drop', -9, {}),
    ('cut off their hair', 'sword_shing', -16, dict(at='slashed')),
    ('one of gold', 'metal_clang', -8, dict(kw=dict(f0=440.0))),
    ('one of silver', 'metal_clang', -8, dict(kw=dict(f0=330.0))),
    ('one of iron', 'metal_clang', -7, dict(kw=dict(f0=165.0, dur=3.0))),
    ('buried him at night', 'shovel', -12, {}),
    ('weapons and treasure', 'shovel', -13, dict(seed=4)),
    ('his empire fell apart', 'wood_crack', -14, dict(at='fell apart')),
    # Crassus
    ('crassus means', 'boing', -17, dict(at='"fat"')),
    ('a wild last name', 'cha_ching', -10, dict(at='richest man in Rome')),
    ('catching fire or collapsing', 'fire_whoosh', -12, {}),
    ('for almost nothing', 'coins', -14, {}),
    ('while it was on fire', 'cha_ching', -10, dict(at='on fire>')),
    ('the gladiator who led', 'sword_clash', -14, {}),
    ('crucified along the road', 'sub_drop', -13, {}),
    ('his bank account', 'coins', -14, {}),
    ('sports chariot', 'gallop', -15, {}),
    ('behind your shield', 'thud', -14, {}),
    ('run out of arrows', 'arrow', -13, {}),
    ('camels loaded with fresh arrows', 'click', -10, dict(at='fresh arrows')),
    ('fire backward', 'arrow', -10, dict(kw=dict(direction=1))),
    ("his son's head on a spear", 'crowd_gasp', -14, dict(at='on a spear')),
    ('a scuffle broke out', 'sword_clash', -12, {}),
    ('uses it as the prop', 'crowd_gasp', -13, {}),
    ('snatches the head', 'swish', -12, {}),
    ('gave the actor a fortune', 'applause', -10, dict(kw=dict(dur=2.6))),
    ('fake Roman victory parade', 'crowd_cheer', -19, {}),
    ('poured molten gold', 'sizzle', -10, {}),
    ('more than he could swallow', 'gulp', -10, dict(at='swallow')),
    # Arrichion
    ('at the ancient Olympics', 'crowd_cheer', -18, {}),
    ('superstars of their day', 'crowd_cheer', -15, {}),
    ('think MMA', 'boxing_bell', -14, {}),
    ('punching, kicking', 'punch', -10, dict(at='punching')),
    ('kicking, choking', 'punch', -11, dict(at='kicking', seed=2)),
    ('joint locks', 'bone_crack', -9, {}),
    ('kicking a guy in the stomach', 'punch', -9, dict(at='stomach', seed=4)),
    ('until they snapped', 'bone_crack', -6, dict(at='snapped')),
    ('No weight classes', 'text_hit', -11, {}),
    ('No rounds', 'text_hit', -11, dict(seed=2)),
    ('No time limit', 'text_hit', -10, dict(seed=3)),
    ('A wreath of olive leaves', 'sparkle', -14, {}),
    ('He won the Olympic pankration', 'crowd_cheer', -14, dict(at='572 BC')),
    ('Then again in 568', 'crowd_cheer', -14, dict(seed=2, at='568')),
    ('third straight title', 'crowd_cheer', -12, dict(seed=3)),
    ('makes it to the final', 'boxing_bell', -11, {}),
    ('wraps his legs around', 'thud', -12, {}),
    ('squeezes his neck', 'heartbeat', -8, dict(kw=dict(n_beats=8, bpm=70, slow=0.9))),
    ("wrenched his opponent's", 'bone_crack', -5, dict(at='out of joint')),
    ('out of joint>', 'crowd_gasp', -12, {}),
    ('the opponent gave up', 'boxing_bell', -10, dict(at='gave up')),
    ('died from the chokehold', 'sub_drop', -9, {}),
    ('The winner was dead', 'crickets', -13, dict(kw=dict(dur=4.0))),
    ('They crowned the corpse', 'crowd_cheer', -13, {}),
    ('for the third time', 'crowd_cheer', -15, dict(seed=5)),
    ('his statue still standing', 'sparkle', -16, {}),
    ('Which sounds impossible to top', 'riser', -12, dict(at='impossible to top>', lead=1.3)),
    ('with an entire fleet', 'cannon', -12, dict(at='fleet>', offset=0.25)),
    # mid-roll
    ("killed by a man he'd already beheaded", 'sword_shing', -16, dict(at='beheaded')),
    ('with a roof tile', 'bonk', -9, dict(at='roof tile')),
    ('drop a comment', 'notify', -11, {}),
    ('25,000 likes', 'click', -9, {}),
    ('25,000 likes>', 'pop', -12, {}),
    ('Final entry. Well, the final entry', 'riser', -11, dict(at='part one>', lead=1.2)),
    # Yi
    ('In 1592, Japan invades Korea', 'impact', -11, dict(at='invades Korea')),
    ('falls in about three weeks', 'thud', -13, {}),
    ('iron spikes', 'metal_clang', -15, dict(kw=dict(f0=600.0, dur=1.0))),
    ('cannons on every side', 'cannon', -9, {}),
    ("a dragon's head", 'fire_whoosh', -13, {}),
    ('wrapped his ships around it', 'whoosh', -13, {}),
    ('wiped most of it out', 'ship_crash', -9, {}),
    ('arrested him', 'chain_rattle', -12, {}),
    ('tortured, nearly executed', 'sub_drop', -14, {}),
    ('his mother died', 'bell', -15, dict(kw=dict(f=294.0, dur=3.0))),
    ('straight into a Japanese ambush', 'cannon', -10, dict(at='ambush')),
    ('ambush>', 'ship_crash', -11, dict(offset=0.3)),
    ('pretty much alone', 'cannon', -10, {}),
    ('found the nerve to join in', 'cannon', -11, dict(seed=3)),
    ('crashing into each other', 'ship_crash', -9, {}),
    ('tore into them', 'cannon', -10, dict(seed=4)),
    ('31 Japanese ships had been wrecked', 'ship_crash', -12, dict(seed=2)),
    ('killed his youngest son', 'sub_drop', -14, {}),
    ('hit the Japanese fleet in the Noryang', 'cannon', -11, {}),
    ('a bullet struck Yi', 'gunshot', -4, dict(at='bullet struck')),
    ('The fleet fought on and won', 'crowd_cheer', -15, dict(at='and won')),
    ('hundreds of Japanese ships were destroyed', 'cannon', -11, dict(seed=7)),
    ('fell to the deck three times', 'thud', -14, {}),
    ('100-won coin', 'coins', -12, {}),
    # outro
    ('A Viking king who skipped armor day', 'sword_shing', -18, {}),
    ('A warlord beaten by a nosebleed', 'boing', -17, {}),
    ("Rome's richest man, turned into", 'cha_ching', -16, {}),
    ('An Olympic champion crowned', 'crowd_cheer', -20, {}),
    ('Sources: a pile', 'page_flip', -13, {}),
]

# deaths: the recurring death motif (stinger + visual stamp) — shared with the video layer
DEATHS = [('Harald', "That's it. The last great Viking king"), ('Attila', 'choked on it'), ('Crassus', 'was killed'),
          ('Arrichion', 'died from the chokehold'), ('Yi Sun-sin', 'struck Yi')]

# ambience per backdrop / photo
BG_BED = {'field': 'birds', 'sea': 'sea', 'night': 'night', 'arena': 'stadium', 'hall': 'hall', 'forest': 'birds',
          'stamford_river': 'river', 'hagia_sophia': 'hall', 'puszta': 'wind', 'carrhae': 'desert', 'olympia_stadium': 'stadium',
          'gyeongbokgung': 'birds'}
PHOTO_BED = {'stamford_arbo': 'battle', 'feast_attila': 'feast', 'fire_rome': 'fire', 'hun_archer': 'wind', 'olympia_stadium': 'stadium',
             'turtle_ship': 'sea', 'myeongnyang': 'river', 'greek_theater': 'stadium', 'parthian_archer': 'desert'}
BATTLE_SCENES = {'Harald chooses violence', 'charged out ahead', 'an arrow hits him', 'held the bridge', 'underneath the bridge',
                 "Crassus's son led", 'lured into peace talks', 'Roman legionary', 'fire backward', 'pretty much alone',
                 "Yi's flagship held off", 'crashing into each other', 'raged until daylight', 'picked up the war drum',
                 'captains hung back', 'straight into a Japanese ambush'}
BED_GAIN = {'battle': 3.0, 'stadium': 2.0, 'sea': 1.0, 'feast': 1.0, 'fire': 2.0}


# ============================================================ timing helpers
def word_end(i):
    return B.WORDS[i]['e']


def resolve(spec, cursor=0):
    """Return (time_s, word_index) for a trigger spec."""
    if spec == '@last':
        return B.LAST_WORD_END + 7.0, len(B.WORDS) - 1
    end = spec.endswith('>')
    ph = spec[:-1] if end else spec
    i = B.find(ph, cursor)
    if end:
        j = i + len([w for w in ph.split() if B.norm(w)]) - 1
        return word_end(j), i
    return B.WORDS[i]['s'] - 0.02, i


# ============================================================ build event lists
def score(timeline):
    A = MU.Arranger()
    cues = []
    cur = 0
    starts = []
    for k, (trig, style, mood, I, o) in enumerate(MUSIC):
        t0, i = resolve(trig, cur)
        cur = i
        starts.append((t0, i))
    for k, (trig, style, mood, I, o) in enumerate(MUSIC):
        t0, i = starts[k]
        if o.get('end'):
            t1, _ = resolve(o['end'], i)
        else:
            t1 = starts[k + 1][0] if k + 1 < len(MUSIC) else B.LAST_WORD_END
        if t1 - t0 < 0.8:
            continue
        cues.append(MU.Cue(t0, t1, style, mood, I, ending=o.get('ending', 'cut'), ramp=o.get('ramp'), seed=k))
    for c in cues:
        MU.arrange(A, c)
    # title-card hits from the timeline (exact cut frames)
    sect_style = {'Harald Hardrada.': 'viking', 'Attila the Hun.': 'hun', 'Marcus Licinius Crassus.': 'roman',
                  'Arrichion of Phigalia.': 'greek', 'Yi Sun-sin.': 'korean'}
    for b in timeline:
        if b['kind'] == 'title':
            MU.stinger(A, 'title_hit', b['f0'] / FPS, sect_style.get(b['trigger'], 'viking'))
    cur = 0
    for trig, kind, style, o in STINGS:
        try:
            t, i = resolve(o.get('at', trig), cur)
        except KeyError:
            t, i = resolve(o.get('at', trig), 0)
        cur = max(0, i - 40)
        MU.stinger(A, kind, t, style, **{k: v for k, v in o.items() if k not in ('at',)})
    # the nephew's war drum (diegetic) - taiko on the scene's drum beats
    for b in timeline:
        if b.get('drum'):
            for f in range(b['f0'], b['f1'], 12):
                A.note('perc', (0, 116), f / FPS, 0.6, 38, 112)
                A.drum('perc', 48, f / FPS, 35, 100)
    MU.stinger(A, 'outro_sting', B.LAST_WORD_END + 0.2, 'modern')
    return A, cues


def music_fx(timeline=None):
    out = []
    cur = 0
    cuts = sorted(b['f0'] / FPS for b in (timeline or []) if b['kind'] == 'title')
    for trig, kind, o in MFX:
        try:
            t, i = resolve(trig, cur)
        except KeyError:
            t, i = resolve(trig, 0)
        cur = max(0, i - 40)
        if kind == 'muffle':
            t1, _ = resolve(o['until'], i)
            out.append(dict(t=t, kind='muffle', dur=t1 - t, f=o.get('f', 420.0)))
        elif kind == 'drop':
            dur = o['dur']
            nxt = [c for c in cuts if c > t]
            if nxt:                                   # a dramatic silence must never eat into a title hit
                dur = min(dur, nxt[0] - t - 0.035)
            out.append(dict(t=t, kind='drop', dur=dur, gain=0.0))
        else:
            out.append(dict(t=t, kind=kind, dur=o.get('dur', 0.8)))
    return out


def xpan(x):
    return float(np.clip((x - W / 2) / (W / 2) * 0.7, -0.8, 0.8))


PROP_SFX = {'gold_pile': ('coins', -13), 'coin': ('coins', -15), 'crown': ('sparkle', -17), 'sword': ('sword_shing', -13),
            'shield': ('thud', -15), 'book': ('page_flip', -15), 'tombstone': ('stone_slam', -8), 'coffin': ('coffin_thud', -14),
            'wreath': ('sparkle', -15), 'house': ('fire_whoosh', -12), 'flames': ('fire_whoosh', -12), 'jail': ('metal_clang', -12),
            'chain': ('chain_rattle', -14), 'barrel': ('splash', -15), 'salt': ('pop', -12), 'plate': ('coins', -18),
            'cup': ('coins', -18), 'tv': ('click', -12), 'chariot': ('gallop', -15), 'eagle': ('sparkle', -16),
            'door': ('door_crash', -7), 'shovel': ('shovel', -13), 'tile': ('bonk', -12), 'pedestal': ('stone_slam', -14),
            'longship': ('splash', -16), 'turtle_ship': ('splash', -15), 'jp_ship': ('splash', -16), 'dust': ('whoosh', -16),
            'arrow': ('arrow', -12), 'drum': (None, 0), 'sun': (None, 0), 'bed': (None, 0), 'stage': (None, 0), 'car': (None, 0)}
ICON_SFX = {'x': ('buzzer', -15), 'check': ('ding', -18), 'heart': ('sparkle', -17), 'skull': ('impact', -14),
            'question': ('boing', -15), 'recycle': ('whoosh', -14), 'bang': ('punch', -11)}


def auto_sfx(timeline, calls, overlays):
    ev = []
    seed = [0]

    def add(t, name, gain, **kw):
        seed[0] += 1
        ev.append(dict(t=t, name=name, gain=gain, seed=kw.pop('seed', seed[0] % 7), **kw))
    prev = None
    for b in timeline:
        t0 = b['f0'] / FPS
        e = b.get('ev', {})
        k = b['kind']
        if k == 'title':
            add(t0, 'impact', -1, seed=1, verb='hall', send=0.3)
        elif k == 'kinetic':
            for li, (base, words, width) in enumerate(b['lines']):
                for wi, w in enumerate(words):
                    pass
            for i, (_, _, wds) in enumerate([(0, 0, x) for x in b['kin'].layout]) if hasattr(b['kin'], 'layout') else []:
                pass
            for f in sorted({lf for line in b['kin'].lines for (_, _, _, lf) in line[1]}):
                add(f / FPS, 'text_hit', -9, seed=int(f) % 5, kw=dict(weight=1.2))
        elif k == 'photo':
            add(t0, 'swish', -19)
            if b.get('bodycam'):
                add(t0, 'radio_static', -18)
                add(t0 + 0.1, 'rec_beep', -22)
            if 'circle' in e or b.get('circle'):
                add(e.get('circle', b['f0'] + 9) / FPS, 'marker', -16)
        elif k == 'collage':
            for i, _ in enumerate(b.get('imgs', [])):
                add(t0 + 0.12 * i, 'swish', -18, seed=i)
        elif k == 'map':
            add(t0, 'whoosh', -15, kw=dict(dur=0.45, lo=300, hi=2500))
            for key, f in e.items():
                if key.startswith('stop'):
                    add(f / FPS, 'whoosh', -17, kw=dict(dur=0.6, lo=500, hi=3000))
                    add(f / FPS + 0.55, 'pop', -14, kw=dict(f0=600.0))
                elif key.startswith('pin_'):
                    add(f / FPS, 'pop', -13, kw=dict(f0=750.0))
            for n_, label, trig in b.get('pins', []):
                if not trig:
                    add(t0 + 0.3, 'pop', -14, kw=dict(f0=800.0))
        elif k == 'card':
            ty = b.get('type')
            add(t0, 'page_flip' if ty in ('quote', 'calendar', 'list', 'playlist', 'dict') else 'swish', -17)
            items = b.get('items', [])
            for i, it in enumerate(items):
                f = e.get(f'item{i}')
                if f is not None:
                    if ty == 'inventory':
                        add(f / FPS, 'sparkle' if isinstance(it, dict) and it.get('rarity', '').startswith('LEG') else 'pop', -15,
                            kw={} if isinstance(it, dict) and it.get('rarity', '').startswith('LEG') else dict(f0=520.0 + 60 * i))
                    elif ty == 'versus':
                        add(f / FPS, 'impact', -11, seed=i)
                    else:
                        add(f / FPS, 'pop', -14, kw=dict(f0=560.0 + 70 * i))
                    if b.get('mark') == 'check':
                        add(f / FPS + 0.08, 'ding', -21)
            for key, f in e.items():
                if key.startswith('strike'):
                    add(f / FPS, 'marker', -12)
                    add(f / FPS + 0.3, 'buzzer', -17)
            if 'overlay' in e:
                kind = b.get('overlay_icon')
                nm, g = ICON_SFX.get(kind, ('pop', -14))
                add(e['overlay'] / FPS, nm, g)
            if ty == 'quote' and b.get('word_frames'):
                for wf in b['word_frames']:
                    add(wf / FPS, 'click', -24, kw=dict(f=2600.0))
            if ty == 'comment':
                add(t0, 'notify', -13)
            if ty in ('text',):
                add(t0, 'impact', -7, verb='hall')
            if ty == 'ammo':
                add(t0 + 0.2, 'click', -12)
                add(t0 + 0.35, 'thunk', -14)
            if ty == 'bio':
                for i, ln in enumerate(b.get('lines', [])):
                    f = e.get(f'item{i}')
                    if f is not None:
                        add(f / FPS, 'pop', -16, kw=dict(f0=600.0 + 50 * i))
        elif k == 'scene':
            if b.get('teaser'):
                add(t0, 'whoosh', -9, kw=dict(dur=0.55, lo=400, hi=5000))
                add(t0 + 0.05, 'camera_shutter', -12)
            else:
                add(t0, 'swish', -21)
            for i, ch in enumerate(b.get('chars', [])):
                if f'c{i}' in e:
                    add(e[f'c{i}'] / FPS, 'swish', -15, pan=xpan(ch['x']), seed=i)
                if f'c{i}_exit' in e:
                    add(e[f'c{i}_exit'] / FPS, 'swish', -16, pan=xpan(ch['x']), seed=i + 3)
                if ch.get('say') and f'say{i}' not in e:
                    add(t0 + 0.15, 'pop', -16, pan=xpan(ch['x']), kw=dict(f0=900.0))
                elif f'say{i}' in e:
                    add(e[f'say{i}'] / FPS, 'pop', -15, pan=xpan(ch['x']), kw=dict(f0=900.0))
            for i, p in enumerate(b.get('props', [])):
                name = p['name']
                if name == 'icon':
                    nm, g = ICON_SFX.get(p.get('kw', {}).get('kind'), ('pop', -15))
                else:
                    nm, g = PROP_SFX.get(name, ('pop', -16))
                if nm is None:
                    continue
                if name == 'jail' and p.get('kw', {}).get('broken'):
                    continue                     # the break-out has its own story SFX
                if name == 'coffin' and b['trigger'] == 'three coffins':
                    continue                     # metal clangs from the story list
                if name == 'arrow' and p.get('move'):
                    continue
                f = e.get(f'p{i}', b['f0'])
                add(f / FPS + 0.03, nm, g, pan=xpan(p['x']), seed=i, verb='room' if b.get('bg') == 'hall' else None)
            for li, lab in enumerate(b.get('labels', [])):
                f = e.get(f'label{li}')
                if f is not None:
                    add(f / FPS, 'pop', -17, pan=xpan(lab[1]), kw=dict(f0=820.0))
            if b.get('censor'):
                add(t0 + 0.2, 'censor_beep', -19)
            if b.get('boss'):
                pass                             # boss stinger handles it
        elif k == 'ships':
            add(t0, 'whoosh', -14, kw=dict(dur=0.7, lo=200, hi=2200))
            add(t0 + 0.25, 'splash', -17)
            if 'change' in e:
                add(e['change'] / FPS, 'splash', -13, seed=3)
                add(e['change'] / FPS + 0.05, 'wood_crack', -17)
        elif k == 'end':
            lf = e.get('logo')
            if lf:
                add(lf / FPS + 0.3, 'click', -10)
                add(lf / FPS + 0.45, 'notify', -12)
        elif k == 'host':
            if b.get('zoom') and prev is not None and prev['kind'] == 'host' and not prev.get('zoom'):
                add(t0, 'swish', -23)
        prev = b
    for c in calls:
        add(c['f0'] / FPS, 'text_hit', -12, seed=c['f0'] % 5)
    for o in overlays:
        t0, t1 = o['f0'] / FPS, o['f1'] / FPS
        add(t0, 'rec_beep', -20)
        add(t0, 'clock_tick', -22, kw=dict(dur=round(t1 - t0, 2), period=0.5))
        add(t1, 'ding', -14)
    return ev


def story_sfx():
    ev = []
    cur = 0
    for trig, name, gain, o in SFX:
        spec = o.get('at', trig)
        try:
            t, i = resolve(spec, cur)
        except KeyError:
            t, i = resolve(spec, 0)
        cur = max(0, i - 60)
        ev.append(dict(t=t + o.get('offset', 0.0), name=name, gain=gain, seed=o.get('seed', 0), kw=o.get('kw', {}),
                       lead=o.get('lead', 0.0), pan=o.get('pan', 0.0), verb=o.get('verb')))
    return ev


def death_sfx():
    """The recurring death motif's hit, landing with the DEATH stamp slam (4 frames after the death moment)."""
    return [dict(t=t + 4 / FPS, name='impact', gain=-3, seed=9, verb='hall', send=0.4) for _, t in death_times()]


def ambience(timeline):
    segs = []
    for b in timeline:
        bed = None
        bg = str(b.get('bg', ''))
        if b['kind'] == 'scene':
            if bg.startswith('img:'):
                key, _, fb = bg[4:].partition('|')
                bed = BG_BED.get(key, BG_BED.get(fb))
            else:
                bed = BG_BED.get(bg)
            if b['trigger'] in BATTLE_SCENES:
                bed = 'battle' if bed not in ('sea',) else 'sea'
        elif b['kind'] == 'photo':
            bed = PHOTO_BED.get(b.get('img'))
        elif b['kind'] == 'ships':
            bed = 'sea'
        if bed:
            segs.append([b['f0'] / FPS, b['f1'] / FPS, bed])
    merged = []
    for s in segs:
        if merged and merged[-1][2] == s[2] and s[0] - merged[-1][1] < 2.5:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [dict(t0=a, t1=b, bed=c, gain=BED_GAIN.get(c, 0.0), seed=i) for i, (a, b, c) in enumerate(merged)]


def death_times():
    out = []
    cur = 0
    for who, trig in DEATHS:
        t, i = resolve(trig, cur)
        cur = i
        out.append((who, t))
    return out


def validate():
    bad = []
    for lst, pos in ((MUSIC, 0), (STINGS, 0), (MFX, 0), (SFX, 0)):
        for row in lst:
            specs = [row[0]]
            o = row[-1] if isinstance(row[-1], dict) else {}
            for k in ('at', 'end', 'until'):
                if o.get(k):
                    specs.append(o[k])
            for sp in specs:
                try:
                    resolve(sp, 0)
                except KeyError:
                    bad.append(sp)
    return bad


def main(write=True):
    timeline, calls, overlays = B.compile_all()
    A, cues = score(timeline)
    print('cues', len(cues), 'parts', len(A.parts))
    stems = A.render(B.TOTAL_S)
    fx = music_fx(timeline)
    ev = auto_sfx(timeline, calls, overlays) + story_sfx() + death_sfx()
    amb = ambience(timeline)
    print('sfx events', len(ev), 'ambience segments', len(amb))
    vp = os.path.join(HERE, 'voice.wav')
    vp = vp if os.path.exists(vp) else os.path.join(HERE, 'voice.flac')
    out = os.path.join(HERE, 'mix.wav')
    stats = mixer.mix(vp, B.VOICE_OFFSET, B.TOTAL_S, stems, fx, ev, amb, out, stems_dir=os.path.join(HERE, 'stems'),
                      amb_under_db=22.0)
    print('loudness', stats)
    json.dump(dict(deaths=death_times()), open(os.path.join(HERE, 'sound_events.json'), 'w'), indent=1)
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        print('missing triggers:', validate())
    else:
        main()
