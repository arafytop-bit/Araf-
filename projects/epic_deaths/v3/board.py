"""v3 storyboard: every beat keyed to the narration. Characters live on REAL photos or on the black stage
(never on flat cartoon backdrops); text is big; every hold has motion; the host fills the gaps (build3.plan_hosts)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from timeline import T  # noqa: E402
from cast import *  # noqa: F401,F403,E402

BEATS, CALLS, HOSTS, STAMPS, OVERLAYS = [], [], [], [], []
SEQ = [0]
W, H = 1920, 1080


def _seq():
    SEQ[0] += 1
    return SEQ[0]
GROUND = 965          # feet line for characters on photos


def B(trigger, kind, **kw):
    BEATS.append(dict(trigger=trigger, kind=kind, seq=_seq(), **kw))


def C(trigger, text, hold=2.2, until=None, style='red', from_=None):
    CALLS.append(dict(trigger=trigger, text=text, hold=hold, until=until, style=style, seq=_seq(), **({'from': from_} if from_ else {})))


def HO(trigger, **kw):
    HOSTS.append(dict(trigger=trigger, seq=_seq(), **kw))


def STAMP(trigger, text, sub=None, x=W / 2, y=0.52 * H, off=0, hold=1.8, cap=74):
    STAMPS.append(dict(trigger=trigger, text=text, sub=sub, x=x, y=y, off=off, hold=hold, cap=cap, seq=_seq()))


def A(pal, x, y=GROUND, R=105, **kw):
    return dict(pal=pal, x=x, y=y, R=R, **kw)


def P(name, x, y, size, **kw):
    return dict(name=name, x=x, y=y, size=size, **kw)


def walk(at, frm, dur=None):
    return dict(kind='walk', at=at, frm=frm, **({'dur': dur} if dur else {}))


def run(at, frm, dur=None):
    return dict(kind='run', at=at, frm=frm, **({'dur': dur} if dur else {}))


def pop(at, dur=None):
    return dict(kind='pop', at=at, **({'dur': dur} if dur else {}))


def drop(at, height=700, dur=None):
    return dict(kind='drop', at=at, height=height, **({'dur': dur} if dur else {}))


def act(kind, at, **kw):
    return dict(kind=kind, at=at, **kw)


def exit_(kind, at, to=None, dur=None):
    d = dict(kind=kind, at=at)
    if to is not None:
        d['to'] = to
    if dur:
        d['dur'] = dur
    return d


def say(text, x, bottom, at, until):
    return (text, x, bottom, at, until)


def tagp(text, x, bottom, at, fixed=False):
    return (text, x, bottom, at, fixed)


def kline(y, cap, words):
    """Kinetic line: words = [(text, trigger T, red?)]"""
    return dict(y=y, cap=cap, words=[dict(t=t, at=a, red=r) for t, a, r in words])


# ===================================== HOOK (0:00) =====================================
# Frame 1 is mid-action: the crowned corpse. The on-screen hook lights up word by word as it is spoken.
B("One of these guys wins a fight", 'scene', bg='olympia_stadium', focus=(0.5, 0.55), until='Another wins',
  klines=[kline(0.205 * H, 0.083 * H, [('WON A FIGHT', T('wins a fight'), False), ('AFTER', T('after'), False),
                                       ('DYING', T('already dead'), True)])],
  actors=[A(ARRICHION, 860, y=GROUND - 10, R=100, lie=True, expr='ko', z=1),
          A(OPPONENT, 1450, R=100, flip=True, expr='cry', pose='cheeks', seed=3,
            acts=[act('hop', -12, dur=10, h=0.35), act('hop', 2, dur=10, h=0.35), act('hop', 16, dur=10, h=0.35),
                  act('hop', 30, dur=10, h=0.35), act('hop', 44, dur=10, h=0.35), act('hop', 58, dur=10, h=0.35)])],
  props=[P('wreath', 452, 862, 58, rot=90, enter=dict(kind='fly', at=-14, until=T('already dead'), frm=(452, 240)), z=2)],
  tags=[tagp('WINNER', 600, 640, T('already dead')), tagp('LOSER', 1450, 500, T('already dead', off=6))],
  cam=[('punch', T('already dead'), 0.03)])
B('Another wins a battle', 'scene', bg='turtle_ship', focus=(0.22, 0.48), zoom=1.15, gain=0.95, sat=0.7, night=True, blur=0.8,
  rate=0.012, until='These are the most epic',
  klines=[kline(0.205 * H, 0.083 * H, [('WON A BATTLE', T('wins a battle'), False), ('THE SAME WAY', T('the same way'), True)])],
  props=[P('drum', 1560, 820, 128, z=2, kw=dict(hit=False))],
  actors=[A(NEPHEW, 1250, R=104, pose='drum', expr='angry', z=3)],
  fx_under=[dict(kind='glow', x=1500, y=900, r=760, a=150), dict(kind='glow', x=250, y=980, r=520, a=110)],
  fx=[dict(kind='fire', x=180, y=960, size=74), dict(kind='fire', x=520, y=990, size=56), dict(kind='embers', x0=0, x1=W, n=50)],
  drum=True, cam=[('punch', T('the same way'), 0.03)])

# ===================================== TITLE (kinetic, as the reference opens) =====================================
B('These are the most epic deaths', 'kinetic', until="Now, if you've",
  lines=[kline(0.25 * H, 0.083 * H, [('THE', T('the most'), False), ('MOST', T('most epic'), False), ('EPIC', T('epic'), True)]),
         kline(0.25 * H + 0.15 * H, 0.118 * H, [('DEATHS', T('deaths'), False)]),
         kline(0.25 * H + 0.27 * H, 0.083 * H, [('IN', T('in human'), False), ('HUMAN', T('human'), False), ('HISTORY', T('history'), False)])],
  actors=[A(pal, 560 + 200 * k, y=0.93 * H, R=46, expr='grin', seed=k, enter=run(T('These', off=3 + 4 * k), 2200 + 120 * k))
          for k, pal in enumerate([HARALD, ATTILA, CRASSUS, ARRICHION, YI])])

# ===================================== INTRO =====================================
B('the greatest hits', 'band', text="HISTORY YOUTUBE'S GREATEST HITS", until="This isn't one",
  photos=[('tycho', 0.20 * W, 0.615 * H, 0.235 * W, T("Tycho Brahe's"), None, (0.5, 0.3)),
          ('chrysippus', 0.50 * W, 0.615 * H, 0.235 * W, T('The philosopher'), None, (0.5, 0.35)),
          ('rasputin', 0.80 * W, 0.615 * H, 0.235 * W, T('Rasputin refusing'), None, (0.5, 0.3))],
  label_y=0.965 * H, label_w=0.23 * W, label_cap=50,
  photo_labels=[('BLADDER', 0.20 * W, T("bladder")), ('DONKEY JOKE', 0.50 * W, T('laughed')), ("WON'T DIE", 0.80 * W, T('refusing'))])
STAMP('recycles the same', 'RECYCLED', sub='EVERY. SINGLE. LIST.', y=0.62 * H, hold=1.9, cap=96)
HO("This isn't one of those", framing='CU', pose='point', expr='smug')
B('deaths so legendary', 'scene', bg='heimskringla', blur=7.0, gain=0.40, until='And every entry',
  actors=[A(SCRIBE, 720, R=112, expr=[(None, 'talk'), (T('barely believe'), 'shock')], pose='hold',
            enter=walk(T('deaths so legendary'), -200, 26)),
          A(SNORRI, 1200, R=112, flip=True, expr=[(None, 'skeptic'), (T('barely believe'), 'shock')], pose='chin',
            enter=walk(T('legendary that', off=2), 2200, 26),
            acts=[act('hop', T('barely believe'), dur=9, h=0.3)])],
  props=[P('book', 960, 690, 64, enter=pop(T('wrote them down')), acts=[act('bob', 0, amp=0.05)])])
HO('every entry tops', pose='hips', expr='grin')
HO("Let's get into it", framing='CU', pose='wave', expr='smile')


# ===================================== #1 HARALD HARDRADA =====================================
B('Harald Hardrada.', 'title', num=1, name=['HARALD', 'HARDRADA'], img='harald_portrait', focus=(0.62, 0.42), zoom=1.25, hold=1.7)
C('hard ruler', 'HARDRADA = "HARD RULER"', until='which is the medieval')
B('no small talk', 'text', bg='harald_portrait', until="And if you're",
  lines=[("HARALD'S BIO:", 'silver', 0.06 * H), ('"NO SMALL TALK."', 'red', 0.11 * H, T('no small talk', off=2))])
HO("And if you're thinking", pose='chin', expr='skeptic')
HO("I've seen Vikings | no", framing='CU', expr='deadpan', pose='hips')
B("You've seen TV Vikings", 'scene', bg='tv_set', focus=(0.3, 0.35), zoom=1.6, blur=0.0, gain=0.95, vignette=0.35,
  until='Harald was real',
  actors=[A(VIK_TEE, 845, y=760, R=96, pose='hips', expr='grin', enter=pop(T('TV Vikings')), clip=(400, 70, 1290, 742), no_shadow=True)],
  fx=[dict(kind='crt', rect=(400, 70, 1290, 742))],
  tags=[tagp('TV VIKINGS', 845, 1010, T('TV Vikings'), fixed=True)])
B('Harald was real', 'photo', img='harald_portrait', focus=(0.6, 0.5), caption='THE REAL ONE', cap_at=T('real'),
  until='his actual life')
HO('his actual life', pose='shrug', expr='grin')
B('If the Viking Age had a final boss', 'scene', bg='fjord', focus=(0.5, 0.45), until='So, in case',
  actors=[A(HARALD, 960, R=150, pose='hips', expr=[(None, 'smug'), (T('this guy'), 'angry')], enter=drop(T('final boss'), 900))],
  fx=[dict(kind='bossbar', name='HARALD HARDRADA', sub='FINAL BOSS · VIKING AGE', at=T('final boss'))],
  cam=[('shake', T('final boss', off=8), 12)])
HO('let me speedrun his', framing='CU', pose='point', expr='grin')
OVERLAYS.append(dict(kind='timer', seq=_seq(), trigger='speedrun his', until='Because in 1066', stop=T("And that's just the warm-up", cut=True),
                     label='HARALD% SPEEDRUN'))
B('At about fifteen', 'photo', img='olav_stiklestad', mode='full', focus=(0.5, 0.5), until='They lose',
  marks=[('ring', 0.50, 0.52, 0.11, 0.16, T('half-brother Olaf')), ('label', 'OLAF', 0.50, 0.36, T('Olaf', off=2))])
C('At about fifteen', 'AGE: 15', hold=2.0)
B('They lose', 'scene', bg='olav_stiklestad', blur=6.0, gain=0.45, until='Harald is badly',
  actors=[A(HARALD_YOUNG, 700, R=108, expr=[(None, 'shock'), (T('Olaf dies'), 'sad')], pose='cheeks'),
          A(OLAF, 1220, R=108, flip=True, expr='angry', acts=[act('die', T('Olaf dies'), dur=9, back=True)])],
  tags=[tagp('HARALD (15)', 700, 455, T('They lose')), tagp('OLAF', 1220, 455, T('They lose', off=3))])
B('Harald is badly wounded', 'scene', bg='norway_forest', focus=(0.5, 0.6), until='then flees',
  actors=[A(HARALD_YOUNG, 760, R=104, expr='sad', pose='idle', enter=walk(T('badly wounded'), -250, 40))],
  props=[P('house', 1330, 830, 150, enter=pop(T('hides out')))],
  tags=[tagp('BADLY WOUNDED', 760, 470, T('wounded'))])
B('then flees all the way', 'map', region='viking_route', until='and joins the Varangian', icon='longship',
  highlight=('Norway', 'Russia', 'Ukraine', 'Turkey'),
  stops=[('Farm', 'NORWAY', T('then flees')), ('Novgorod', 'RUSSIA', T('Russia')), ('Kyiv', 'UKRAINE', T('Ukraine')),
         ('Constantinople', 'CONSTANTINOPLE', T('turns up in'))])
B('and joins the Varangian', 'photo', img='varangian', mode='frame', caption='THE VARANGIAN GUARD', cap_at=T('Varangian'),
  until="the Byzantine emperor's")
B("the Byzantine emperor's elite", 'scene', bg='hagia_sophia', focus=(0.5, 0.55), until='He fights all over',
  actors=[A(VARANGIAN, 520, R=100, expr='deadpan', enter=pop(T('elite bodyguard'))),
          A(BYZ, 960, R=112, expr='smug', pose='hips'),
          A(VARANGIAN, 1400, R=100, flip=True, expr='deadpan', enter=pop(T('bodyguard', off=4)))],
  tags=[tagp('EMPEROR', 960, 470, T("emperor's"))])
C('Scandinavian mercenaries', 'VIKINGS FOR HIRE', hold=1.8)
B('He fights all over the Mediterranean', 'map', region='viking_route', focus='Constantinople', zoom=1.25, until='and piles up',
  highlight=('Italy', 'Bulgaria', 'Israel', 'Turkey'),
  pins=[('Sicily', 'SICILY', T('all over')), ('Bulgaria', 'BULGARIA', T('the Mediterranean')), ('Jerusalem', 'JERUSALEM', T('Mediterranean and'))])
B('piles up a fortune', 'stage', until='And according to the sagas',
  actors=[A(HARALD, 760, R=118, pose='cheer', expr='grin')],
  props=[P('gold_pile', 1260, 900, 150, enter=pop(T('fortune')))],
  fx=[dict(kind='rain_gold', x=960, at=T('fortune'))])
B('he gets thrown in prison', 'scene', bg='dungeon', focus=(0.5, 0.5), until='and helps blind',
  actors=[A(HARALD, 960, R=112, expr=[(None, 'deadpan'), (T('breaks out'), 'smug')], pose=[(None, 'idle'), (T('breaks out'), 'cheer')])],
  props=[P('jail', 960, 640, 330, z=5, exit_=None, exit=dict(kind='fly', at=T('breaks out'), to=(960, -900), dur=12))],
  cam=[('shake', T('breaks out'), 16)])
B('helps blind an emperor', 'scene', bg='hagia_sophia', focus=(0.5, 0.55), until='Then he escapes',
  actors=[A(BYZ, 960, R=140, expr='shock', pose='cheeks')],
  fx=[dict(kind='censor', actor=0, at=T('blind'))])
B('Then he escapes by sailing', 'scene', bg='golden_horn', focus=(0.5, 1.0), zoom=3.4, blur=2.5, until='giant iron chain',
  props=[P('chain', 960, 900, 240, z=1), P('longship', 420, 760, 150, z=2, acts=[act('move', T('escapes'), to=(1380, 760), dur=70), act('bob', 0)])])
B('giant iron chain', 'photo', img='golden_horn_chain', caption='THE HARBOR CHAIN', cap_at=T('iron chain'), focus=(0.5, 0.62),
  until='One ship snaps', marks=[('ring', 0.52, 0.80, 0.42, 0.10, T('blocking'))])
B('One ship snaps in half', 'scene', bg='golden_horn', focus=(0.5, 1.0), zoom=3.4, blur=2.5, until='His makes it',
  props=[P('chain', 960, 900, 240, z=1)],
  fx=[dict(kind='split', x=960, y=760, size=150, at=T('snaps'))], cam=[('shake', T('snaps'), 14)])
HO('His makes it', framing='CU', pose='point', expr='grin')
B('marries a princess of Kyiv', 'scene', bg='st_sophia_kyiv', focus=(0.5, 0.5), blur=8.0, gain=0.55, until='goes home',
  actors=[A(HARALD, 720, R=106, expr='smile', enter=walk(T('marries'), -260, 26)),
          A(PRINCESS, 1200, R=104, flip=True, expr='smile')],
  props=[P('icon', 960, 430, 60, kw=dict(kind='heart'), enter=pop(T('princess')), acts=[act('bob', 0, amp=0.08, hz=1.2)])],
  tags=[tagp('PRINCESS OF KYIV', 1200, 470, T('princess of Kyiv'))])
B('goes home, and becomes King', 'scene', bg='fjord', focus=(0.5, 0.45), until="And that's just",
  actors=[A(HARALD_CROWN, 960, R=130, pose='hips', expr='smug', enter=pop(T('becomes King')))],
  tags=[tagp('KING OF NORWAY', 960, 330, T('King of Norway'))])
HO("And that's just the warm-up", framing='CU', expr='smug', pose='hips')

C('in 1066', '1066', hold=1.6)
B('the King of England dies', 'stage', until='and three different men',
  props=[P('bed', 960, 800, 190)],
  actors=[A(EDWARD, 960, y=760, R=78, lie=True, expr=[(None, 'sleep'), (T('dies'), 'ko')], no_shadow=True)],
  tags=[tagp('KING OF ENGLAND', 960, 520, T('King of England'))])
C('no son to take over', 'NO HEIR', hold=1.6)
B('three different men decide', 'trio', until='So Harald sails',
  people=[dict(img='bayeux_harold_crown', name=['HAROLD', 'GODWINSON'], at=T('three different'), lit=T('Harold Godwinson'),
               crown=T('gets crowned'), focus=(0.5, 0.4)),
          dict(img='william_statue', name=['WILLIAM OF', 'NORMANDY'], at=T('three different', off=3), lit=T('William of Normandy'),
               focus=(0.5, 0.3), sub='= THE CONQUEROR', sub_at=T('William the Conqueror')),
          dict(img='harald_portrait', name=['HARALD', 'HARDRADA'], at=T('three different', off=6), lit=T('our guy'), ring=True,
               focus=(0.62, 0.42), zoom=1.3)])
B('So Harald sails for England', 'map', region='north_sea', icon='longship', until='smashes the first', highlight=('Norway', 'United Kingdom'),
  stops=[('Norway', 'NORWAY', T('Harald sails')), ('Humber', 'ENGLAND', T('around 300'))])
C('around 300 ships', '~300 SHIPS', hold=1.6)
B('smashes the first English army', 'scene', bg='yorkshire_field', focus=(0.5, 0.55), until='and takes York',
  actors=[A(HARALD, 640, R=106, pose='point', expr='angry', enter=run(T('smashes'), -300, 14)),
          A(ENG, 1220, R=100, flip=True, expr='shock', exit=exit_('run', T('army that tries'), 2400)),
          A(ENG, 1500, R=100, flip=True, expr='nervous', exit=exit_('run', T('tries to stop'), 2500))])
B('and takes York', 'photo', img='york', mode='full', until='At this point', caption='YORK: TAKEN', cap_at=T('York'))
HO('he pretty much thinks', pose='hips', expr='smug')
HO("here's the problem with this story", framing='CU', expr='skeptic', pose='chin')
B('comes from one book', 'photo', img='heimskringla', mode='doc', caption='HEIMSKRINGLA', cap_at=T('Heimskringla'),
  until='written in Iceland')
B('written in Iceland', 'photo', img='snorri', mode='frame', focus=(0.5, 0.3), caption='SNORRI STURLUSON', cap_at=T('Snorri'),
  until='So, grain of salt')
C('160 years after', '160 YEARS LATER', hold=1.8)
B('So, grain of salt', 'photo', img='salt_shaker', mode='full', focus=(0.51, 0.55), zoom=2.8, until='But what Snorri', caption='GRAIN OF SALT', cap_at=T('grain'))
HO('But what Snorri describes', framing='CU', expr='shock', pose='cheeks')
C('September 25th', 'SEPTEMBER 25, 1066', until='a place called')
B('a place called Stamford Bridge', 'map', region='north_sea', focus='York', zoom=2.3, until='And the weather', highlight=('United Kingdom',),
  pins=[('York', 'YORK', T('a place called')), ('Stamford Bridge', 'STAMFORD BRIDGE', T('Stamford Bridge'))])
B('And the weather is gorgeous', 'scene', bg='stamford_river', focus=(0.5, 0.5), until="It's so warm",
  fx_under=[dict(kind='rays', x=300, y=120, r=900)],
  actors=[A(VIK_TEE, 960, R=112, pose='hips', expr='grin', enter=pop(T('weather')))],
  props=[P('sun', 300, 200, 110, enter=pop(T('gorgeous')), acts=[act('spin', 0, speed=0.6)])])
B("It's so warm that", 'photo', img='oseberg_ship', mode='frame', until='They walk out', caption='THE ARMOR: STILL ON THE SHIP',
  cap_at=T('armor back'))
B('They walk out with just', 'list', title='LOADOUT', mark='check', until='and the saga literally', items=[
    dict(text='SHIELD', at=T('shields')), dict(text='HELMET', at=T('helmets')), dict(text='SPEAR', at=T('spears')),
    dict(text='SWORD', at=T('swords')), dict(text='ARMOR', mark='x', style='red', at=T('and the saga'))])
B('they were all very merry', 'scene', bg='stamford_river', until='Meanwhile, the English',
  fx_under=[dict(kind='rays', x=300, y=120, r=900)],
  actors=[A(VIK_TEE, 560, R=100, pose='cheer', expr='grin', seed=1, acts=[act('hop', T('very merry', off=k * 8), dur=8) for k in range(4)]),
          A(VIK_TEE2, 960, R=100, pose='cheer', expr='grin', seed=2, acts=[act('hop', T('very merry', off=4 + k * 8), dur=8) for k in range(4)]),
          A(VIK_TEE, 1360, R=100, flip=True, pose='cheer', expr='grin', seed=3, acts=[act('hop', T('very merry', off=2 + k * 8), dur=8) for k in range(4)])])
C('very merry', '"VERY MERRY"', hold=1.6)
B('the English king has been racing', 'map', region='north_sea', icon='crown', until='Nobody warns', focus='York', zoom=1.5,
  highlight=('United Kingdom',), dy=-0.06 * H,
  stops=[('London', 'LONDON', T('racing north')), ('York', 'YORK', T('pushing his army'))])
C('40 miles a day', '40 MILES A DAY', hold=1.6)
HO('Nobody warns the Norwegians', framing='CU', expr='nervous', pose='cheeks')
B("Harald's men are chilling", 'scene', bg='stamford_river', until='a cloud of dust',
  fx_under=[dict(kind='rays', x=300, y=120, r=900)],
  actors=[A(VIK_TEE, 700, R=104, pose='hips', expr='smile'), A(VIK_TEE2, 1220, R=104, flip=True, pose='idle', expr='grin')],
  tags=[tagp('T-SHIRTS', 960, 470, T('t-shirts'))])
B('a cloud of dust rises', 'scene', bg='stamford_river', zoom=1.35, focus=(0.55, 0.4), until='So what does',
  fx=[dict(kind='dust', x=1250, y=520, w=900, at=T('cloud of dust')), dict(kind='glints', x=1250, y=560, w=700, n=22, at=T('the shine'))],
  actors=[A(VIK_TEE, 560, R=104, expr=[(None, 'smile'), (T('the shine'), 'shock')], look=(0.3, 0.0))])
C('the shine of a whole lot of armor', 'ARMOR. LOTS OF ARMOR.', hold=1.8)
HO('the scariest Viking alive', pose='chin', expr='skeptic')
B('left his armor in the car', 'scene', bg='yorkshire_field', until='For that, we have',
  actors=[A(HARALD, 700, R=106, pose='cheeks', expr='shock')],
  props=[P('car', 1300, 840, 190, enter=pop(T('in the car')))],
  tags=[tagp('ARMOR', 1300, 640, T('car', off=4))])
HO('For that, we have to go', pose='inspect', expr='talk')
B('Harald rides out to inspect', 'photo', img='stamford_arbo', mode='full', until='and his horse stumbles')
B('and his horse stumbles', 'scene', bg='stamford_river', until='He jumps right back',
  actors=[A(HARALD, 820, R=106, expr=[(None, 'talk'), (T('throws him'), 'ko')], acts=[act('fall', T('throws him'), dur=8)]),
          A(VIK_TEE, 1320, R=96, flip=True, expr=[(None, 'smile'), (T('in front of'), 'shock')]),
          A(VIK_TEE2, 1600, R=96, flip=True, expr=[(None, 'grin'), (T('everybody'), 'shock')])],
  fx=[dict(kind='dust', x=600, y=930, w=420, at=T('to the ground'))], cam=[('shake', T('to the ground'), 12)])
B('He jumps right back up', 'scene', bg='stamford_river', until='Which is the most',
  actors=[A(HARALD, 820, R=110, pose='hips', expr='smug', enter=dict(kind='rise', at=T('jumps'), dur=10))],
  says=[say('"A FALL IS LUCKY FOR A TRAVELLER."', 960, 420, T('A fall is lucky'), T('Which is the most', cut=True))])
HO('cover for eating dirt', framing='CU', expr='grin', pose='point')
B('The English king sees all this', 'scene', bg='yorkshire_field', until='the one who just fell',
  actors=[A(GODWINSON, 760, R=108, pose=[(None, 'chin'), (T('asks who'), 'point')], expr=[(None, 'skeptic'), (T('asks who'), 'talk')],
            enter=walk(T('sees all this'), -260, 24))],
  tags=[tagp('KING OF ENGLAND', 760, 455, T('English king'))],
  says=[say('"WHO\'S THE BIG MAN IN BLUE?"', 1180, 420, T('asks who'), T('the one who just fell', cut=True))])
B('the one who just fell off', 'scene', bg='stamford_river', until='They tell him',
  actors=[A(HARALD, 900, R=106, lie=True, expr='ko')], fx=[dict(kind='dust', x=700, y=930, w=420, at=T('just fell', off=-10))],
  tags=[tagp('BIG MAN IN BLUE', 760, 760, T('fell off'))])
B("They tell him it's the King", 'scene', bg='yorkshire_field', until='And he says, roughly',
  actors=[A(GODWINSON, 760, R=108, pose='idle', expr='shock'), A(ENG, 1240, R=100, flip=True, expr='talk', enter=pop(T('They tell')))],
  says=[say('"THAT\'S THE KING OF NORWAY."', 1240, 420, T('King of Norway'), T('And he says', cut=True))])
B('a great man, and a stately', 'quote', text='A great man, and a stately one, but I think his luck has left him.',
  quote_at='a great man', who='Harold Godwinson, in the saga', bg='bayeux_harold_crown', until='Then twenty English')
B('Then twenty English riders', 'scene', bg='yorkshire_field', until='One of them offers',
  actors=[A(ENG, 300 + 170 * k, R=78, expr='deadpan', seed=k, enter=walk(T('riders', off=2 * k), 2300 + 140 * k, 30)) for k in range(6)])
C('twenty English riders', '20 RIDERS', hold=1.6)
B('offers Harald\'s ally', 'map', region='north_sea', highlight=('United Kingdom',), focus='York', zoom=1.4, until='And when he\'s asked',
  labels=[('A HUGE CHUNK OF ENGLAND', (0.5, 0.2), T('huge chunk'))])
HO("And when he's asked", pose='shrug', expr='talk')
B('seven feet of English ground', 'scene', bg='yorkshire_field', until='Translation',
  props=[P('tombstone', 960, 720, 200, enter=drop(T('seven feet')), kw=dict())],
  tags=[tagp('+ A BIT MORE', 960, 400, T('a bit more'))], cam=[('shake', T('seven feet', off=7), 8)])
C('seven feet', '7 FEET OF ENGLISH GROUND', hold=2.6)
HO('Translation', expr='deadpan', pose='hips')
HO('Oh, and that rider', framing='CU', expr='skeptic', pose='chin')
B('it was the English king himself', 'scene', bg='yorkshire_field', until='Harald chooses',
  actors=[A(GODWINSON, 960, R=130, pose='hips', expr='smug', enter=pop(T('English king')))],
  tags=[tagp('THE RIDER = THE KING', 960, 330, T('king himself'))], cam=[('punch', T('king himself'), 0.04)])
B('Harald chooses violence', 'text', anim='slam', hold=1.6, lines=[('HARALD HAS CHOSEN', 'white', 0.085 * H),
                                                                  ('VIOLENCE', 'red', 0.16 * H, T('violence'))],
  cam=[('shake', T('violence'), 14)])
B('he charged out ahead', 'scene', bg='stamford_arbo', blur=5.0, gain=0.5, until='And then an arrow',
  actors=[A(HARALD, 820, R=112, pose=[(None, 'run'), (T('swinging'), 'swing')], expr='angry', enter=run(T('charged'), -300, 18))],
  props=[P('sword', 760, 470, 70, rot=-30, enter=pop(T('both hands'))), P('sword', 880, 470, 70, rot=30, flip=True, enter=pop(T('both hands')))])
B('And then an arrow hits him', 'scene', bg='stamford_arbo', blur=5.0, gain=0.5, until="That's it",
  actors=[A(HARALD, 820, R=112, expr=[(None, 'angry'), (T('windpipe'), 'ko')], acts=[act('die', T('windpipe', off=3), dur=10, back=True)])],
  props=[P('arrow', 840, 520, 70, rot=180, enter=dict(kind='fly', at=T('arrow hits', off=-6), frm=(2100, 470), dur=7), z=3)],
  fx=[dict(kind='flash', at=T('windpipe'), dur=4, color='#FF2020', amp=0.35)], cam=[('shake', T('windpipe'), 16)])
HO("That's it", framing='ECU', expr='deadpan', pose='idle')
B('The last great Viking king dies', 'photo', img='stamford_arbo', mode='full', push=1, until='And the English have')
STAMP('dies on an English field', 'DEATH #1', sub='ARROW TO THE THROAT', y=0.55 * H, hold=2.2)
C('armor was optional', 'ARMOR: "OPTIONAL"', hold=1.6)
HO('the English have their own', pose='point', expr='talk')
B('Anglo-Saxon Chronicle decades later', 'photo', img='anglo_saxon_chronicle', mode='doc', focus=(0.5, 0.3),
  caption='ANGLO-SAXON CHRONICLE', cap_at=T('Chronicle'), until="so it's not exactly")
B("so it's not exactly bodycam", 'photo', img='stamford_arbo', mode='full', zoom=1.3, focus=(0.45, 0.5), until='But it says',
  fx=[dict(kind='bodycam')])
B('a single Norwegian held the bridge', 'scene', bg='stamford_river', until='A later historian',
  props=[P('bridge', 1060, 900, 240, z=0)],
  actors=[A(VIK_ARMOR, 1060, y=760, R=104, pose='hips', expr='angry', z=1, enter=drop(T('a single Norwegian'), 600)),
          A(ENG, 380, R=86, expr='nervous', seed=1, acts=[act('shake', T("couldn't cross"))]),
          A(ENG, 560, R=86, expr='shock', seed=2, acts=[act('shake', T("couldn't cross", off=3))])],
  tags=[tagp('1 VIKING', 1060, 380, T('single Norwegian')), tagp('THE ENTIRE ENGLISH ARMY', 470, 560, T('the whole English'))])
B('A later historian claims', 'count', to=40, prefix='~', label='MEN', until='He only went down', dur=30,
  bg='stamford_river')
B('He only went down when', 'scene', bg='stamford_river', until='Later retellings',
  props=[P('bridge', 960, 760, 260, z=1)],
  actors=[A(VIK_ARMOR, 960, y=640, R=96, z=0, expr=[(None, 'smug'), (T('stabbed up'), 'ko')], acts=[act('die', T('the gap'), dur=10)]),
          A(ENG, 960, y=1060, R=78, z=2, expr='evil', enter=dict(kind='rise', at=T('underneath'), dur=10))],
  props_extra=None,
  fx=[dict(kind='flash', at=T('stabbed up'), dur=3, color='#FFFFFF', amp=0.4)], cam=[('shake', T('stabbed up'), 12)])
B('put that guy in a floating barrel', 'scene', bg='stamford_river', until='It gets worse',
  actors=[A(ENG, 960, y=880, R=82, z=1, expr='smug', acts=[act('bob', 0)])],
  props=[P('barrel', 960, 880, 120, z=2, enter=pop(T('floating barrel')), acts=[act('bob', 0, amp=0.05, hz=0.8)])],
  tags=[tagp('BARREL GUY', 960, 560, T('barrel', off=4))])
HO('It gets worse for Norway', framing='CU', expr='grimace', pose='cheeks')
B('Reinforcements sprint over', 'scene', bg='yorkshire_field', until='The Norwegians had',
  fx_under=[dict(kind='rays', x=1600, y=100, r=900)],
  actors=[A(VIK_ARMOR, 520 + 380 * k, R=96, seed=k, expr=[(None, 'angry'), (T('so exhausted'), 'nervous')],
            pose=[(None, 'idle'), (T('so exhausted'), 'shrug')], enter=run(T('sprint', off=4 * k), -300 - 200 * k, 26),
            acts=[act('shake', T('barely fight', off=k))]) for k in range(3)],
  tags=[tagp('FULL ARMOR. IN THE HEAT.', 960, 460, T('in the heat'))])
B('had shown up with around 300', 'ships', n=60, n2=5, ship='longship', change=T('They needed 24'), label=('300 SHIPS', '24 SHIPS HOME'),
  until="But here's the craziest")
HO("But here's the craziest part", framing='ECU', expr='shock', pose='cheeks')
B('William of Normandy lands', 'map', region='north_sea', icon='longship', until='Harold Godwinson has to', focus='London', zoom=1.5,
  highlight=('United Kingdom', 'France'),
  stops=[('Normandy', 'NORMANDY', T('William of Normandy')), ('Pevensey', 'THE SOUTH', T('lands in the south'))])
C('Three days later', '3 DAYS LATER', hold=1.6)
B('has to drag his exhausted', 'map', region='north_sea', icon='crown', until='he dies at the Battle', focus='London', zoom=1.4,
  highlight=('United Kingdom',),
  stops=[('York', 'YORK', T('drag his')), ('London', 'LONDON', T('all the way back')), ('Hastings', 'HASTINGS', T('nineteen days'))])
C('nineteen days after', '19 DAYS LATER', hold=1.8)
B('he dies at the Battle of Hastings', 'photo', img='bayeux_harold', mode='frame', caption='BATTLE OF HASTINGS', cap_at=T('Hastings'),
  until="So Harald's death is")
B("So Harald's death is often used", 'text', until='and it helped set up', bg='stamford_arbo',
  lines=[('THE END OF THE', 'silver', 0.07 * H), ('VIKING AGE', 'red', 0.14 * H, T('Viking Age'))])
B('set up the Norman Conquest', 'photo', img='bayeux_harold', mode='full', zoom=1.4, focus=(0.4, 0.5), until='which is a big reason',
  caption='THE NORMAN CONQUEST', cap_at=T('Norman Conquest'))
B('English is full of French', 'list', title='ENGLISH, BUT FRENCH', mark='dot', until='Not bad for a guy', items=[
    dict(text='BEEF (BOEUF)', at=T('English is full')), dict(text='PORK (PORC)', at=T('full of French')),
    dict(text='JUSTICE, JURY, COURT', at=T('French words')), dict(text='ROYAL, CROWN, GOVERNMENT', at=T('words today'))])
B('lost to the weather', 'scene', bg='stamford_river', until='Attila the Hun.',
  fx_under=[dict(kind='rays', x=960, y=300, r=1000)],
  props=[P('sun', 960, 480, 200, enter=pop(T('lost to')), acts=[act('spin', 0, speed=0.8)])])
C('lost to the weather', 'WINNER: THE WEATHER', hold=1.8)


# ===================================== #2 ATTILA THE HUN =====================================
B('Attila the Hun.', 'title', num=2, name=['ATTILA', 'THE HUN'], img='leo_attila', focus=(0.53, 0.47), zoom=2.4, hold=1.7)
HO("Here's the thing about Attila", pose='chin', expr='skeptic')
B('written by people who hated him', 'scene', bg='rome_model', focus=(0.5, 0.5), blur=4.0, gain=0.6, until='Our best source',
  actors=[A(PRISCUS, 700, R=104, expr='angry', pose='hold'), A(ROMAN_EMP, 1220, R=104, flip=True, expr='angry', pose='point')],
  props=[P('book', 960, 700, 60, enter=pop(T('written by'))), P('icon', 700, 380, 50, kw=dict(kind='bang'), enter=pop(T('hated')))],
  tags=[tagp('ROMAN WRITERS', 960, 420, T('people who'))])
B('a Roman diplomat named Priscus', 'stage', until='and had dinner',
  actors=[A(PRISCUS, 960, R=130, expr='smile', pose='wave', enter=pop(T('a Roman diplomat')))],
  tags=[tagp('PRISCUS', 960, 300, T('Priscus'))])
C('in 449', '449 AD', hold=1.6)
B('and had dinner with him', 'photo', img='feast_attila', mode='full', focus=(0.5, 0.35), until='Which is a sentence',
  marks=[('ring', 0.47, 0.25, 0.07, 0.10, T('dinner')), ('label', 'ATTILA', 0.47, 0.11, T('dinner', off=4))])
HO('Which is a sentence I need you', framing='CU', pose='point', expr='smug')
B('they were horse archers', 'photo', img='hun_archer', mode='full', focus=(0.4, 0.55), until='who rode into Europe',
  caption='HORSE ARCHERS', cap_at=T('horse archers'))
B('who rode into Europe', 'map', region='europe_huns', until='and scared the Roman', highlight=('Hungary',),
  stops=[('Steppe', 'THE STEPPE', T('who rode')), ('Pannonia', 'EUROPE', T('into Europe'))])
B('and scared the Roman Empire', 'scene', bg='rome_model', focus=(0.5, 0.5), blur=4.0, gain=0.6, until='Under Attila',
  actors=[A(ROMAN_EMP, 700, R=104, expr=[(None, 'nervous'), (T('paying them'), 'grimace')], pose=[(None, 'cheeks'), (T('paying them'), 'hold')],
            acts=[act('shake', T('so badly'))]),
          A(HUN, 1240, R=104, flip=True, expr='smug', pose='hips')],
  props=[P('coin', 940 + 30 * k, 640 - 40 * k, 32, enter=dict(kind='fly', at=T('paying them', off=2 * k), frm=(720, 620), dur=10))
         for k in range(4)],
  tags=[tagp('PLEASE GO AWAY', 700, 455, T('go away'))])
B('Under Attila, the bill hit', 'count', to=2100, label='POUNDS OF GOLD', bg='solidus', until='Per year', dur=34)
B('Per year.', 'text', anim='slam', until="He wasn't conquering", lines=[('PER.', 'white', 0.13 * H), ('YEAR.', 'red', 0.16 * H, T('year'))],
  cam=[('shake', T('year'), 10)])
B("He wasn't conquering Rome", 'sub', price='2,100 LBS OF GOLD', until='He started out', btn_at=10 ** 9, button='CANCEL?',
  plan='PREMIUM · NO HUNS AT YOUR GATES')
B('He started out sharing the throne', 'scene', bg='puszta', focus=(0.5, 0.45), until='After that, he invaded',
  actors=[A(ATTILA, 700, R=106, expr=[(None, 'smile'), (T('treachery'), 'evil')], pose=[(None, 'idle'), (T('treachery'), 'hips')]),
          A(BLEDA, 1220, R=106, flip=True, expr=[(None, 'smile'), (T('Bleda died'), 'ko')], acts=[act('die', T('Bleda died'), dur=9, back=True)])],
  tags=[tagp('ATTILA', 700, 455, T('sharing the throne')), tagp('BLEDA', 1220, 455, T('Bleda'))],
  fx=[dict(kind='vignette_red', at=T('treachery'))])
C("Attila's treachery", 'TREACHERY?', hold=1.6)
B("he invaded what's now France", 'map', region='europe_huns', icon='crown', until='He even had a legendary', highlight=('France', 'Italy'),
  stops=[('Pannonia', 'HUN EMPIRE', T("invaded what's")), ('Gaul', 'FRANCE', T('France')), ('Pannonia', '', T('invaded Italy')),
         ('Italy', 'ITALY', T('Italy'))])
C('most feared man in Europe', 'MOST FEARED MAN IN EUROPE', hold=2.0)
HO('He even had a legendary weapon', framing='CU', pose='point', expr='grin')
B('a herdsman noticed one of his cows', 'scene', bg='grey_cattle', focus=(0.5, 0.55), until='Attila decided it was',
  actors=[A(HERDSMAN, 640, R=104, expr=[(None, 'neutral'), (T('limping'), 'skeptic'), (T('found a sword'), 'shock')],
            enter=walk(T('a herdsman'), -260, 30), acts=[act('hop', T('found a sword'), dur=9, h=0.3)])],
  props=[P('sword', 1180, 860, 110, rot=180, enter=dict(kind='drop', at=T('found a sword'), height=-260, dur=10)),],
  fx=[dict(kind='glints', x=1180, y=760, w=120, n=6, at=T('found a sword'))],
  tags=[tagp('THE COW (LIMPING)', 1300, 420, T('cows limping'))])
B('Attila decided it was the sword', 'stage', until='And yet, according',
  fx_under=[dict(kind='rays', x=960, y=300, r=900, at=T('war god'))],
  actors=[A(ATTILA, 760, R=118, pose='cheer', expr='evil')],
  props=[P('sword', 1300, 640, 150, rot=-8, kw=dict(glow=True), enter=pop(T('the sword')), acts=[act('bob', 0, amp=0.03, hz=0.7)])],
  tags=[tagp('THE SWORD OF THE WAR GOD', 1300, 400, T('war god'))])
C('destined to rule the world', 'DESTINED TO RULE THE WORLD', hold=1.6)
B('the guests ate off silver plates', 'versus', until='Final boss energy',
  left=dict(img='silver_dish', lines=[('GUESTS:', 'white'), ('SILVER & GOLD', 'gold')], at=T('guests ate')),
  right=dict(img='wooden_bowl', lines=[('ATTILA:', 'white'), ('A WOODEN PLATE', 'red')], at=T('while Attila')))
B('Final boss energy', 'text', until='So why is a list', lines=[('FINAL BOSS ENERGY', 'red', 0.1 * H),
                                                              ('STARTER-GEAR EQUIPMENT', 'silver', 0.07 * H, T('starter-gear'))])
HO('So why is a list of epic deaths', pose='shrug', expr='skeptic')
C('died of a nosebleed', 'DIED OF A... NOSEBLEED', hold=2.0)
HO("Because, yes, that's how", framing='CU', expr='deadpan', pose='hips')
C('In 453', '453 AD', hold=1.6)
B('he married a young woman named Ildico', 'scene', bg='feast_attila', blur=6.0, gain=0.45, until="He'd had a lot of wives",
  actors=[A(ATTILA, 720, R=106, expr='smile', enter=walk(T('he married'), -260, 24)),
          A(ILDICO, 1200, R=104, flip=True, expr='smile', enter=walk(T('a young woman'), 2200, 24))],
  props=[P('icon', 960, 420, 60, kw=dict(kind='heart'), enter=pop(T('Ildico')), acts=[act('bob', 0, amp=0.08, hz=1.2)])],
  tags=[tagp('ILDICO', 1200, 455, T('Ildico'))])
B("He'd had a lot of wives", 'text', until='He partied hard', lines=[('A LOT OF WIVES.', 'silver', 0.06 * H),
                                                                  ('ANOTHER WEDDING?', 'white', 0.08 * H, T('so for him')),
                                                                  ('JUST A TUESDAY.', 'red', 0.11 * H, T('Tuesday'))])
B('He partied hard at the wedding', 'photo', img='feast_attila', mode='full', focus=(0.5, 0.4), until='went to bed drunk',
  push=-1)
B('went to bed drunk', 'stage', until='During the night',
  props=[P('bed', 960, 800, 200)],
  actors=[A(ATTILA, 960, y=760, R=80, lie=True, expr='sleep', no_shadow=True)],
  tags=[tagp('ON HIS BACK', 960, 560, T('lay on his back'))], fx=[dict(kind='text', t='Z', x=1150, y=560, at=T('drunk'), cap=60)])
B('During the night, his nose', 'photo', img='attila_death', mode='full', focus=(0.55, 0.45), until='The next morning',
  marks=[('ring', 0.64, 0.50, 0.10, 0.14, T('nose started'))], fx=[])
B('his attendants got suspicious', 'scene', bg='old_door', focus=(0.5, 0.5), until='and found the most feared',
  props=[P('door', 960, 560, 230, exit=dict(kind='fly', at=T('broke down the door'), to=(2400, 200), dur=12))],
  actors=[A(HUN, 520, R=100, expr=[(None, 'skeptic'), (T('broke down'), 'angry')], enter=walk(T('attendants'), -260, 24)),
          A(HUN, 1400, R=100, flip=True, expr=[(None, 'skeptic'), (T('broke down'), 'angry')], enter=walk(T('got suspicious'), 2200, 24))],
  cam=[('shake', T('broke down the door', off=3), 18)])
B('and found the most feared man', 'photo', img='attila_death', mode='full', focus=(0.6, 0.45), zoom=1.3, until='Some later writers',
  marks=[('label', 'NO WOUNDS', 0.5, 0.25, T('without a single wound'))])
STAMP('dead without a single wound', 'DEATH #2', sub='A NOSEBLEED', y=0.60 * H, hold=2.4)
B('Some later writers claimed', 'versus', until="So that's the death", left=dict(lines=[('LATER WRITERS:', 'white'), ('"SHE DID IT"', 'red')], at=T('Some later')),
  right=dict(lines=[('EARLIEST ACCOUNT:', 'white'), ('THE NOSEBLEED', 'red')], at=T('our earliest')))
HO("So that's the death", pose='hips', expr='talk')
HO('Embarrassing', framing='ECU', expr='grimace', pose='cheeks')
HO('But the funeral', pose='point', expr='smug')
HO('The funeral is why', framing='CU', expr='grin', pose='hips')
B('According to the historian Jordanes', 'stage', until="Attila's warriors cut",
  actors=[A(SCRIBE, 960, R=128, expr='talk', pose='hold', enter=pop(T('Jordanes')))],
  props=[P('book', 960, 760, 70, enter=pop(T('working from')))],
  tags=[tagp('JORDANES', 960, 300, T('Jordanes')), tagp('(COPYING PRISCUS)', 960, 395, T('working from Priscus'))])
B("Attila's warriors cut off their hair", 'scene', bg='puszta', gain=0.42, sat=0.6, until='mourned not with tears',
  actors=[A(HUN_BALD, 560, R=98, expr='sad', seed=1), A(HUN_BALD, 960, R=98, expr='cry', seed=2), A(HUN_BALD, 1360, R=98, flip=True, expr='sad', seed=3)],
  tags=[tagp('HAIR: GONE', 960, 440, T('cut off their hair'))])
B('mourned not with tears', 'quote', text='Mourned not with tears, but with the blood of men.', quote_at='mourned not with tears',
  who='Jordanes', bg='feast_attila', until='Then they sealed')
B('Then they sealed his body', 'stage', until='They buried him at night',
  props=[P('coffin', 560, 600, 165, kw=dict(c='#E8B83A'), enter=pop(T('one of gold'))),
         P('coffin', 960, 600, 165, kw=dict(c='#C9CED3'), enter=pop(T('one of silver'))),
         P('coffin', 1360, 600, 165, kw=dict(c='#5E6469'), enter=pop(T('one of iron')))],
  tags=[tagp('GOLD', 560, 330, T('one of gold')), tagp('SILVER', 960, 330, T('one of silver')), tagp('IRON', 1360, 330, T('one of iron')),
        tagp('THE RICHES HE TOOK', 760, 940, T('riches he took'), fixed=True), tagp('THE NATIONS HE CRUSHED', 1360, 1010, T('nations he crushed'), fixed=True)])
B('They buried him at night', 'scene', bg='puszta', gain=0.32, sat=0.5, until='And it worked',
  props=[P('gold_pile', 1150, 900, 120, enter=pop(T('treasure'))), P('sword', 1420, 860, 80, rot=80, enter=pop(T('weapons'))),
         P('shovel', 600, 820, 140, rot=20)],
  actors=[A(HUN, 520, R=92, expr=[(None, 'neutral'), (T('they killed'), 'ko')], acts=[act('die', T('killed the men'), dur=9)]),
          A(HUN, 820, R=92, expr=[(None, 'neutral'), (T('they killed'), 'ko')], acts=[act('die', T('the men who dug'), dur=9)])],
  fx=[dict(kind='vignette_red', at=T('they killed'))])
HO('And it worked', framing='CU', expr='smug', pose='hips')
B('More than fifteen hundred years', 'map', region='europe_huns', focus='Pannonia', zoom=1.9, until='Within about a year',
  highlight=('Hungary',), pins=[('Pannonia', "ATTILA'S TOMB: ???", T("nobody has found"))])
C('fifteen hundred years', '1,500+ YEARS. STILL LOST.', hold=2.2)
B('the peoples he\'d conquered rose up', 'scene', bg='puszta', until='So Attila had the least',
  actors=[A(HUN, 700, R=100, expr='shock', exit=exit_('run', T('fell apart'), -400)), A(HUN, 1100, R=100, expr='nervous', exit=exit_('run', T('fell apart', off=3), 2400))]
  + [A(ENG, 200 + 120 * k, R=78, expr='angry', seed=k, enter=run(T('rose up', off=2 * k), -300 - 80 * k, 20)) for k in range(3)],
  tags=[tagp('EMPIRE: GONE', 960, 420, T('fell apart'))], cam=[('shake', T('fell apart'), 12)])
B('the least epic death in history', 'versus', until='He walked so',
  left=dict(img='attila_death', focus=(0.6, 0.45), lines=[('LEAST EPIC', 'white'), ('DEATH', 'red')], at=T('least epic')),
  right=dict(img='feast_attila', focus=(0.5, 0.3), lines=[('MOST EPIC', 'white'), ('FUNERAL', 'red')], at=T('most epic funeral')))
B('He walked so every heavy metal', 'album', img='attila_death', focus=(0.6, 0.45), band='ATTILA', title='THREE COFFINS',
  sticker='PARENTAL ADVISORY', until='Marcus Licinius Crassus.')


# ===================================== #3 MARCUS LICINIUS CRASSUS =====================================
B('Marcus Licinius Crassus.', 'title', num=3, name=['MARCUS', 'LICINIUS', 'CRASSUS'], img='crassus_bust', focus=(0.5, 0.35), zoom=1.1,
  hold=1.75, name_scale=0.92)
B('No, not "crass,"', 'band', text='NOT "CRASS"', until='Although, fun fact',
  actors=[A(UNCLE, 960, y=0.95 * H, R=112, pose='point', expr='grin', enter=pop(T('your uncle')))],
  says=None)
B('Although, fun fact', 'list', title='CRASSUS (LATIN)', mark='dot', until='Which is a wild last name', items=[
    dict(text='= FAT', at=T('fat')), dict(text='= THICK', at=T('thick'))])
B('Which is a wild last name', 'photo', img='crassus_bust', mode='frame', focus=(0.5, 0.4), until="And that's exactly",
  caption='RICHEST MAN IN ROME', cap_at=T('richest man'))
HO("And that's exactly who this was", pose='hips', expr='smug')
HO('How rich', framing='ECU', expr='skeptic', pose='chin')
B('According to the Greek biographer Plutarch', 'scene', bg='rome_model', blur=6.0, gain=0.5, until='Crassus noticed that',
  actors=[A(SCRIBE, 960, R=124, pose='hold', expr='talk', enter=pop(T('biographer')))],
  props=[P('book', 960, 760, 66, enter=pop(T('Plutarch')))],
  tags=[tagp('PLUTARCH', 960, 330, T('Plutarch'))])
B('Crassus noticed that Roman buildings', 'photo', img='fire_rome', mode='full', focus=(0.5, 0.5), until='So he bought more',
  marks=[('label', 'FIRE', 0.5, 0.42, T('catching fire')), ('label', 'COLLAPSE', 0.75, 0.62, T('collapsing'))])
B('So he bought more than 500', 'count', to=500, fmt='{:,}+', label='ENSLAVED BUILDERS & ARCHITECTS', bg='rome_model',
  until='Then, whenever a house', dur=26, label_style='silver')
B('Then, whenever a house went up', 'scene', bg='fire_rome', blur=5.0, gain=0.5, until="That's how he ended up",
  props=[P('house', 560, 760, 140, kw=dict(burning=True), enter=pop(T('house went up'))),
         P('house', 960, 740, 150, kw=dict(burning=True), enter=pop(T('the houses next'))),
         P('house', 1360, 760, 140, kw=dict(burning=True), enter=pop(T('next to it')))],
  actors=[A(CRASSUS, 1640, R=96, flip=True, expr='smug', pose='hips', enter=walk(T("he'd show up"), 2300, 22)),
          A(PRISCUS, 300, R=90, expr='nervous', pose='cheeks', enter=pop(T('owners')), acts=[act('shake', T('panicking'), dur=20)])],
  says=[say('"I\'LL TAKE IT. CHEAP."', 1300, 400, T('offer to buy'), T("That's how he ended up", cut=True))])
B("That's how he ended up owning", 'photo', img='rome_model', mode='full', focus=(0.5, 0.5), until="Rome's richest man got",
  marks=[('ring', 0.42, 0.55, 0.22, 0.25, T('huge chunk')), ('label', "CRASSUS'S", 0.42, 0.28, T('chunk of the city'))])
C('buying your house while', 'BUYING YOUR HOUSE WHILE IT BURNS', hold=2.6)
B("If you've heard of Spartacus", 'photo', img='spartacus_statue', mode='frame', focus=(0.5, 0.3), until='Crassus is the general',
  caption='SPARTACUS', cap_at=T('Spartacus'))
B('Crassus is the general who crushed', 'stage', until='Afterward, around six',
  actors=[A(LEGIONARY, 560, R=100, expr='angry', enter=pop(T('crushed'))), A(CRASSUS, 960, R=124, expr='evil', pose='hips'),
          A(LEGIONARY, 1360, R=100, flip=True, expr='angry', enter=pop(T('crushed it')))],
  tags=[tagp('CRASSUS', 960, 330, T('Crassus is'))])
B('Afterward, around six thousand', 'photo', img='appian_way', mode='full', focus=(0.5, 0.55), until="That's who we're",
  caption='THE ROAD TO ROME', cap_at=T('road to Rome'))
C('six thousand captured', '~6,000 REBELS', hold=2.0)
HO("That's who we're dealing with", framing='CU', expr='grimace', pose='cheeks')
HO('But Crassus had a problem', pose='chin', expr='skeptic')
B('He had money', 'list', mark='check', until='His two political', items=[
    dict(text='MONEY', at=T('He had money'), style='gold'), dict(text='GLORY', mark='x', style='red', at=T('glory'))])
B('His two political partners', 'trio', until='So at around sixty',
  people=[dict(img='pompey_bust', name=['POMPEY'], at=T('His two'), lit=T('Pompey'), focus=(0.5, 0.35)),
          dict(img='caesar_bust', name=['JULIUS', 'CAESAR'], at=T('His two', off=3), lit=T('Julius Caesar'), focus=(0.5, 0.35)),
          dict(img='crassus_bust', name=['CRASSUS'], at=T('His two', off=6), lit=T('he could not stand'), focus=(0.5, 0.35),
               sub='= THE BANK ACCOUNT', sub_at=T('bank account'))])
B('So at around sixty years old', 'stage', until='Crassus decided his',
  props=[P('chariot', 960, 760, 200, enter=dict(kind='slide', at=T('sports chariot'), frm=-400, dur=12))],
  actors=[A(CRASSUS, 900, y=640, R=80, expr='grin', z=1, enter=dict(kind='slide', at=T('sports chariot'), frm=-460, dur=12))],
  tags=[tagp('AGE: ~60', 960, 330, T('sixty years old')), tagp('"SPORTS CHARIOT"', 960, 1030, T('sports chariot', off=6), fixed=True)])
B('Crassus decided his midlife crisis', 'text', until='a superpower that ruled', bg='crassus_bust',
  lines=[('MIDLIFE CRISIS:', 'silver', 0.07 * H, T('midlife crisis')), ('INVADE PARTHIA', 'red', 0.12 * H, T('invading'))])
B('a superpower that ruled', 'map', region='rome_parthia', highlight=('Iran', 'Iraq'), until='It did not go well',
  pins=[('Ctesiphon', 'PARTHIAN EMPIRE', T('superpower'))],
  labels=[('IRAN + IRAQ', (0.5, 0.2), T('Iran and Iraq'))])
HO('It did not go well', framing='CU', expr='grimace', pose='cheeks')
HO('At all', framing='ECU', expr='deadpan', pose='idle')
C('In 53 BC', '53 BC', hold=1.6)
B('In 53 BC, near a town called', 'map', region='rome_parthia', focus='Carrhae', zoom=2.1, until='his army ran into',
  highlight=('Turkey', 'Syria'), pins=[('Carrhae', 'CARRHAE', T('Carrhae'))])
B('his army ran into Parthian', 'photo', img='parthian_archer', mode='frame', focus=(0.5, 0.45), until='Picture this',
  caption='PARTHIAN HORSE ARCHERS', cap_at=T('horse archers'))
B('Picture this', 'photo', img='legion_reenact', mode='full', focus=(0.4, 0.45), until='in a tight formation',
  caption='A ROMAN LEGIONARY', cap_at=T('Roman legionary'))
B('in a tight formation behind', 'scene', bg='carrhae', focus=(0.5, 0.55), until="That's the plan",
  actors=[A(LEGIONARY, 560, R=100, expr='nervous', seed=1), A(LEGIONARY, 960, R=100, expr='nervous', seed=2),
          A(LEGIONARY, 1360, R=100, expr='nervous', seed=3)],
  props=[P('shield', 600, 760, 90, kw=dict(c='#B03A2E', c2='#E8C27A'), z=2, enter=pop(T('behind your shield'))),
         P('shield', 1000, 760, 90, kw=dict(c='#B03A2E', c2='#E8C27A'), z=2, enter=pop(T('your shield', off=2))),
         P('shield', 1400, 760, 90, kw=dict(c='#B03A2E', c2='#E8C27A'), z=2, enter=pop(T('shield', off=4)))]
  + [P('arrow', 700 + 260 * k, 600 + 60 * (k % 2), 56, rot=200, z=3, enter=dict(kind='fly', at=T('run out of arrows', off=3 * k), frm=(2200, 300), dur=8))
     for k in range(4)],
  tags=[tagp('THE PLAN: WAIT', 960, 440, T('waiting for the enemy'))])
HO("That's the plan", framing='CU', expr='deadpan', pose='hips')
HO("That's the entire plan", framing='M', expr='deadpan', pose='shrug')
if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'picked', 'camel.jpg')):
    B('the Romans spotted camels', 'photo', img='camel', mode='full', focus=(0.5, 0.5), until='The arrows were never',
      caption='AMMO DELIVERY', cap_at=T('camels loaded'))
else:
    B('the Romans spotted camels', 'scene', bg='carrhae', focus=(0.5, 0.5), until='The arrows were never',
      props=[P('arrow', 1500 - 140 * k, 420 + 70 * (k % 3), 60, rot=180, enter=dict(kind='fly', at=T('fresh arrows', off=2 * k), frm=(2300, 300), dur=9))
             for k in range(6)],
      actors=[A(LEGIONARY, 600, R=104, expr=[(None, 'skeptic'), (T('fresh arrows'), 'shock')])],
      tags=[tagp('CAMELS = ARROW REFILLS', 1200, 300, T('camels loaded'))])
B('The arrows were never going', 'text', until='The Parthians would even', lines=[('ARROWS:', 'white', 0.08 * H), ('UNLIMITED', 'red', 0.13 * H, T('never'))])
B('The Parthians would even fake', 'photo', img='parthian_archer', mode='frame', focus=(0.5, 0.45), until='That move became',
  marks=[('arrow', 0.15, 0.85, 0.42, 0.40, T('twist around')), ('label', 'FIRING BACKWARD', 0.5, 0.95, T('fire backward'))])
B('That move became known', 'text', until="Crassus's son led", lines=[
    ('PARTHIAN SHOT', 'white', 0.11 * H, T('Parthian shot'), T('parting shot', off=-3)),
    ('PARTING SHOT', 'red', 0.11 * H, T('parting shot'))])
B("Crassus's son led a charge", 'scene', bg='carrhae', until='The Parthians came back',
  actors=[A(LEGIONARY, 900, R=108, pose='point', expr='angry', enter=run(T('led a charge'), -300, 16))],
  tags=[tagp("CRASSUS'S SON", 900, 440, T("son led"))])
HO('The Parthians came back carrying', framing='CU', expr='grimace', pose='cheeks')
B('Eventually Crassus was lured', 'scene', bg='carrhae', until='Plutarch says about',
  actors=[A(CRASSUS, 720, R=104, expr=[(None, 'nervous'), (T('he was killed'), 'ko')], acts=[act('die', T('he was killed'), dur=9)]),
          A(PARTHIAN, 1220, R=104, flip=True, expr=[(None, 'smug'), (T('scuffle'), 'angry')])],
  tags=[tagp('PEACE TALKS', 960, 440, T('peace talks'))],
  fx=[dict(kind='dust', x=960, y=930, w=520, at=T('scuffle'))], cam=[('shake', T('scuffle'), 12)])
STAMP('and he was killed', 'DEATH #3', sub="AT THE 'PEACE TALKS'", y=0.55 * H, off=8, hold=1.9)
B('Plutarch says about twenty thousand', 'list', until='Rome even lost', items=[
    dict(text='20,000 ROMANS DEAD', at=T('twenty thousand'), mark='x', style='white'),
    dict(text='10,000 CAPTURED', at=T('ten thousand'), mark='x', style='white')])
B('Rome even lost its sacred', 'photo', img='aquila', mode='frame', focus=(0.5, 0.35), until='and it took more than',
  caption='THE EAGLE STANDARDS', cap_at=T('eagle standards'))
C('thirty years of diplomacy', '30+ YEARS OF DIPLOMACY', hold=1.8)
HO("And that's not even the wild part", framing='CU', expr='smug', pose='point')
B('The Parthians cut off his head', 'scene', bg='greek_theater', blur=5.0, gain=0.5, until='who was at a royal',
  actors=[A(PARTHIAN_KING, 960, R=124, pose='hips', expr=[(None, 'smug'), (T('sent them'), 'grin')], enter=pop(T('cut off his head')))],
  tags=[tagp('THE PARTHIAN KING', 960, 330, T('their king'))])
B('who was at a royal wedding feast', 'photo', img='greek_theater', mode='full', focus=(0.5, 0.5), until='The next scene',
  caption='A GREEK TRAGEDY: THE BACCHAE', cap_at=T('Greek tragedy'))
B('The next scene features', 'photo', img='theater_masks', mode='frame', focus=(0.4, 0.5), until='So the lead actor',
  caption='TRAGEDY', cap_at=T('severed head'))
B('So the lead actor grabs', 'scene', bg='greek_theater', blur=4.0, gain=0.5, until='Then the Parthian who killed',
  actors=[A(ACTOR, 960, R=112, pose='cheer', expr='talk', enter=pop(T('lead actor')))],
  fx=[dict(kind='head', pal=CRASSUS, x=960, y=515, R=52, expr='ko', at=T('actual head'))],
  tags=[tagp('THE "PROP"', 960, 230, T('as the prop'))])
B('Then the Parthian who killed', 'scene', bg='greek_theater', blur=4.0, gain=0.5, until='The king loved it',
  actors=[A(ACTOR, 700, R=104, pose='cheeks', expr=[(None, 'talk'), (T('snatches'), 'shock')]),
          A(PARTHIAN, 1260, R=106, flip=True, expr='angry', pose='cheer', enter=dict(kind='rise', at=T('jumps up'), dur=9))],
  fx=[dict(kind='head', pal=CRASSUS, x=700, y=600, R=48, expr='ko', moves=[(T('snatches the head'), 1260, 520, 8)])],
  says=[say('"I DID IT! MY LINE!"', 1100, 260, T('insists'), T('The king loved', cut=True))])
B('The king loved it so much', 'stage', until='The richest man in Rome ended',
  actors=[A(PARTHIAN_KING, 700, R=110, expr='grin', pose='cheer'), A(ACTOR, 1240, R=104, flip=True, expr='shock')],
  props=[P('gold_pile', 1240, 940, 110, enter=pop(T('a fortune')))], fx=[dict(kind='rain_gold', x=1240, at=T('gave the actor'))])
HO('The richest man in Rome ended up', pose='hips', expr='grin')
C('ended up as a stage prop', "ROME'S RICHEST MAN: STAGE PROP", hold=2.2)
B('threw a fake Roman victory parade', 'scene', bg='carrhae', until='Oh, and another historian',
  actors=[A(PARTHIAN, 420, R=96, expr='grin', enter=walk(T('fake Roman'), -300, 30), seed=1),
          A(CRASSUS_FAKE, 960, R=100, expr='deadpan', enter=walk(T('starring a captive'), -300, 30), seed=2),
          A(PARTHIAN, 1500, R=96, flip=True, expr='grin', seed=3, acts=[act('hop', T('victory parade', off=k * 9), dur=8) for k in range(3)])],
  tags=[tagp('"CRASSUS"', 960, 440, T('looked like Crassus'))],
  says=[say('"...YES. I AM CRASSUS."', 960, 300, T("answer to Crassus's"), T('Oh, and another', cut=True))])
HO('Oh, and another historian', pose='point', expr='talk')
C('250 years later', '250+ YEARS LATER', hold=1.8)
B('poured molten gold into his mouth', 'stage', until='Even Dio only says',
  props=[P('cup', 1110, 300, 150, rot=125, kw=dict(c='#E8B83A'), enter=pop(T('poured')))],
  fx=[dict(kind='pour', x=1020, y=370, len=230, at=T('molten gold')), dict(kind='head', pal=CRASSUS, x=980, y=720, R=120, expr='ko_o')],
  tags=[tagp('TO MOCK HIS GREED', 960, 1010, T('to mock'), fixed=True)])
B('Even Dio only says', 'text', until='Either way, the moral', lines=[('"SOME SAY..."', 'white', 0.11 * H), ('(MAYBE A LEGEND)', 'red', 0.06 * H, T('might be legend'))])
HO('Either way, the moral', pose='hips', expr='talk')
B('Crassus spent his whole life chasing', 'stage', until='he finally got more',
  actors=[A(CRASSUS, 760, R=106, pose='walk', expr='grin', acts=[act('move', T('chasing gold'), to=(1100, 965), dur=40)])],
  props=[P('coin', 1150, 640, 50, acts=[act('move', T('chasing gold'), to=(1600, 600), dur=40), act('spin', 0, speed=6)])])
HO('he finally got more than', framing='CU', expr='grin', pose='point')


# ===================================== #4 ARRICHION OF PHIGALIA =====================================
B('Arrichion of Phigalia.', 'title', num=4, name=['ARRICHION', 'OF PHIGALIA'], img='pankration_vase', focus=(0.5, 0.42), zoom=1.0,
  hold=1.75)
B('If Harald going into battle', 'stage', until='Because unlike everyone',
  actors=[A(VIK_TEE, 640, R=104, pose='hips', expr=[(None, 'smug'), (T('look cautious'), 'nervous')], seed=1),
          A(ARRICHION, 1280, R=104, flip=True, pose='hips', expr='smug', enter=pop(T('this guy')))],
  tags=[tagp('NO ARMOR', 640, 455, T('without armor')), tagp('NO CLOTHES', 1280, 455, T('makes him'))])
B('Arrichion wasn\'t a king or a general', 'list', until='He was an athlete', items=[
    dict(text='KING', mark='x', at=T('a king')), dict(text='GENERAL', mark='x', at=T('a general'))])
B('He was an athlete', 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='And not in a normal',
  actors=[A(ARRICHION, 960, R=120, pose='cheer', expr='grin', enter=pop(T('athlete')))],
  tags=[tagp('ATHLETE', 960, 360, T('athlete'))])
HO('And not in a normal sport', framing='CU', expr='smug', pose='point')
B('He competed in pankration', 'photo', img='pankration_vase', mode='frame', focus=(0.5, 0.45), until='It had been part',
  caption='PANKRATION', cap_at=T('pankration'))
B('It had been part of the Games', 'photo', img='olympia_stadium', mode='full', focus=(0.5, 0.55), until='Pankration champions',
  caption='OLYMPIA', cap_at=T('the Games'))
C('since 648 BC', 'SINCE 648 BC', hold=2.0)
B('Pankration champions were the superstars', 'photo', img='boxer_rest', mode='frame', focus=(0.5, 0.35), until='If pankration is new',
  caption='ANCIENT GREEK FIGHTING STAR', cap_at=T('superstars'))
B('If pankration is new to you', 'text', until="Here's what was illegal", lines=[
    ('PANKRATION', 'white', 0.1 * H), ('= MMA', 'red', 0.12 * H, T('think MMA')), ('BUT NO LAWYERS', 'silver', 0.07 * H, T('lawsuits'))])
B("Here's what was illegal", 'list', title='ILLEGAL', mark='x', until="Here's what was legal", items=[
    dict(text='BITING', at=T('biting')), dict(text='EYE GOUGING', at=T('gouging'))],
  stamp_at=None)
STAMP("That's the whole list", "THAT'S IT.", y=0.82 * H, hold=1.0, cap=64)
B("Here's what was legal", 'list', title='LEGAL', title_style='white', mark='check', until='One famous champion', items=[
    dict(text='PUNCHING', at=T('punching')), dict(text='KICKING', at=T('kicking, choking')), dict(text='CHOKING', at=T('choking')),
    dict(text='JOINT LOCKS', at=T('joint locks')), dict(text='STOMACH KICKS', at=T('in the stomach')),
    dict(text='FINGER SNAPPING', at=T('bending back'))])
HO('One famous champion won', framing='CU', expr='grimace', pose='cheeks')
B('And in Sparta', 'map', region='greece', focus='Sparta', zoom=1.4, until='No weight classes', highlight=('Greece',),
  pins=[('Sparta', 'SPARTA', T('in Sparta'))], labels=[('NO RULES. AT ALL.', (0.5, 0.18), T('banning'))])
B('No weight classes', 'list', title='ALSO', mark='x', until='You won when', items=[
    dict(text='NO WEIGHT CLASSES', at=T('weight classes')), dict(text='NO ROUNDS', at=T('No rounds')), dict(text='NO TIME LIMIT', at=T('time limit'))])
HO('You won when the other guy', pose='shrug', expr='talk')
B('And the prize', 'text', until='A wreath of olive', lines=[('THE PRIZE?', 'white', 0.09 * H),
                                                           ('NOT GOLD', 'silver', 0.07 * H, T('Not gold')),
                                                           ('NOT MONEY', 'silver', 0.07 * H, T('Not money'))])
B('A wreath of olive leaves', 'photo', img='olive_wreath', mode='frame', focus=(0.5, 0.5), until='In my completely',
  caption='THE PRIZE', cap_at=T('olive leaves'))
HO('In my completely unqualified opinion', framing='CU', expr='smug', pose='chin')
C('most dangerous sport ever', 'MOST DANGEROUS SPORT EVER', hold=2.0)
B("And Arrichion wasn't just good", 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='He won the Olympic',
  actors=[A(ARRICHION_WREATH, 960, R=124, pose='hips', expr='smug', enter=pop(T('good at it')))],
  tags=[tagp('THE GUY', 960, 330, T('He was the guy'))])
B('He won the Olympic pankration', 'list', title='ARRICHION', mark='check', until='He fights his way', items=[
    dict(text='572 BC: CHAMPION', at=T('572')), dict(text='568 BC: CHAMPION', at=T('again in 568')),
    dict(text='564 BC: GOING FOR 3', at=T('in 564'), style='red')])
B('He fights his way through', 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='And in the final, it all',
  actors=[A(ARRICHION, 700, R=104, expr='angry', pose='hips'), A(OPPONENT, 1220, R=104, flip=True, expr='angry', enter=pop(T('the final')))],
  tags=[tagp('ARRICHION', 700, 455, T('He fights')), tagp('OPPONENT', 1220, 455, T('the final', off=3))])
HO('it all goes wrong', framing='ECU', expr='shock', pose='cheeks')
B('His opponent gets a grip first', 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='And this is where',
  actors=[A(OPPONENT, 880, R=110, rot=-22, expr='angry', z=0, acts=[act('shake', T('squeezes'), dur=40)]),
          A(ARRICHION, 1030, R=112, expr=[(None, 'shock'), (T('fading'), 'sad'), (T('black out'), 'sleep')], z=1,
            acts=[act('shake', T('squeezes'), dur=40)])],
  tags=[tagp('LEGS LOCKED', 960, 430, T('wraps his legs')), tagp('NECK: SQUEEZED', 960, 330, T('squeezes his neck'))],
  fx=[dict(kind='blackout', at=T('fading'), dur=70, amp=0.8)])
B('his trainer, a man named Eryxias', 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='Quote',
  actors=[A(ERYXIAS, 960, R=124, pose='point', expr='angry', enter=pop(T('his trainer')))],
  tags=[tagp('ERYXIAS (HIS COACH)', 960, 330, T('Eryxias'))])
B('What a noble epitaph', 'quote', text='What a noble epitaph: He was never defeated at Olympia.', quote_at='What a noble epitaph',
  who='Eryxias, via Philostratus', bg='olympia_stadium', until='An epitaph is the line')
B('An epitaph is the line', 'scene', bg='gravestone', focus=(0.5, 0.5), until='So his coach is basically',
  props=[P('tombstone', 960, 700, 250, enter=drop(T('An epitaph')), text=['NEVER', 'DEFEATED'], tcap=50, ty=0.05)],
  tags=[tagp('EPITAPH = GRAVESTONE LINE', 960, 300, T('carve on your'))], cam=[('shake', T('An epitaph', off=8), 8)])
B('So his coach is basically yelling', 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='Respectfully',
  actors=[A(ERYXIAS, 640, R=112, pose='cheer', expr='grin')],
  props=[P('tombstone', 1360, 740, 220, text=['NEVER', 'DEFEATED'], tcap=46, ty=0.05, enter=pop(T('your tombstone')))],
  says=[say('"YOUR TOMBSTONE WILL LOOK AMAZING!"', 900, 380, T('if you die'), T('Respectfully', cut=True))])
HO('Respectfully', framing='ECU', expr='shock', pose='cheeks')
HO('Your fighter is being strangled', pose='shrug', expr='skeptic')
HO("That's not coaching", framing='CU', expr='deadpan', pose='hips')
HO("That's a threat", framing='M', expr='grimace', pose='point')
HO('But it worked', framing='CU', expr='grin', pose='hips')
B('With the last strength he had', 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='The sources disagree',
  actors=[A(OPPONENT, 880, R=110, rot=-22, expr=[(None, 'angry'), (T('wrenched'), 'cry')], z=0),
          A(ARRICHION, 1030, R=112, expr=[(None, 'sleep'), (T('last strength'), 'angry')], z=1, acts=[act('shake', T('wrenched'), dur=16)])],
  props=[P('icon', 700, 560, 80, kw=dict(kind='bang'), enter=pop(T("opponent's foot")))],
  fx=[dict(kind='flash', at=T('wrenched'), dur=4, color='#FFFFFF', amp=0.45)], cam=[('shake', T('wrenched'), 16)])
B('The sources disagree', 'versus', until='but the pain was so bad',
  left=dict(lines=[('A TOE?', 'white')], at=T('a toe'), cap=0.1 * H), right=dict(lines=[('AN ANKLE?', 'white')], at=T('an ankle'), cap=0.1 * H))
C('the opponent gave up', 'THE OPPONENT GAVE UP', hold=1.6)
B('And at that same moment', 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='Which left the judges',
  actors=[A(ARRICHION, 960, R=112, expr=[(None, 'sad'), (T('died from'), 'ko')], acts=[act('die', T('died from'), dur=10)])])
STAMP('Arrichion died from the chokehold', 'DEATH #4', sub='THE CHOKEHOLD', y=0.50 * H, off=6, hold=2.0)
B('Which left the judges', 'scene', bg='olympia_stadium', focus=(0.5, 0.6), until='The winner was dead',
  actors=[A(JUDGE, 760, R=104, expr='nervous', pose='chin'), A(JUDGE, 1160, R=104, flip=True, expr='nervous', pose='shrug')],
  tags=[tagp('THE JUDGES', 960, 440, T('the judges'))])
B('The winner was dead', 'scene', bg='olympia_stadium', focus=(0.5, 0.55), until='History didn\'t even save',
  actors=[A(ARRICHION, 860, y=GROUND - 10, R=100, lie=True, expr='ko', z=1),
          A(OPPONENT, 1450, R=100, flip=True, expr='cry', pose='cheeks',
            acts=[act('hop', T('The loser', off=k * 14), dur=10, h=0.35) for k in range(6)])],
  tags=[tagp('WINNER', 600, 640, T('winner')), tagp('LOSER', 1450, 500, T('loser'))])
C("save the loser's name", 'LOSER: [NAME NOT FOUND]', hold=2.0)
B('a Greek travel writer named Pausanias', 'stage', until='So the judges did',
  actors=[A(PAUSANIAS, 960, R=124, expr='smug', pose='chin', enter=pop(T('travel writer')))],
  tags=[tagp('PAUSANIAS', 960, 330, T('Pausanias'))],
  says=[say('"...WHOEVER HE WAS."', 960, 220, T('whoever he was'), T('So the judges did', cut=True))])
HO('So the judges did the only fair', pose='shrug', expr='talk')
B('They crowned the corpse', 'scene', bg='olympia_stadium', focus=(0.5, 0.55), until='Pausanias says the win',
  actors=[A(ARRICHION, 860, y=GROUND - 10, R=100, lie=True, expr='ko', z=1),
          A(JUDGE, 1350, R=98, flip=True, expr='nervous', pose='point')],
  props=[P('wreath', 452, 862, 58, rot=90, enter=dict(kind='fly', at=T('They crowned', off=-6), until=T('the corpse'), frm=(452, 220)), z=2)],
  tags=[tagp('OLYMPIC CHAMPION (x3)', 600, 620, T('third time'))], cam=[('punch', T('corpse'), 0.035)])
C('They crowned the corpse', 'THEY CROWNED THE CORPSE', hold=2.2)
B('Pausanias says the win came', 'list', until='About seven hundred', items=[
    dict(text='FAIR JUDGES', mark='check', at=T('fairness of the judges')), dict(text='PURE COURAGE', mark='check', at=T('own courage'))])
B('About seven hundred years', 'map', region='greece', focus='Phigalia', zoom=1.5, until='A statue many believe', highlight=('Greece',),
  pins=[('Phigalia', 'PHIGALIA', T("hometown"))])
C('seven hundred years after', '~700 YEARS LATER', hold=1.8)
B('A statue many believe', 'stage', until='As far as we know',
  props=[P('pedestal', 960, 860, 230)],
  actors=[A(ARRICHION_STATUE, 960, y=760, R=96, pose='hips', expr='neutral', no_shadow=True, enter=pop(T('A statue')))],
  tags=[tagp('"PROBABLY" ARRICHION', 960, 300, T('many believe')), tagp('MUSEUM AT OLYMPIA', 960, 1040, T('museum at Olympia'), fixed=True)])
B('As far as we know', 'text', until='Which sounds impossible', bg='olympia_stadium', lines=[
    ('THE ONLY ATHLETE TO WIN', 'white', 0.075 * H), ('AN OLYMPIC FINAL', 'white', 0.075 * H), ('AFTER DYING', 'red', 0.13 * H, T('after dying'))])
HO('Which sounds impossible to top', pose='hips', expr='smug')
HO('But our last guy', framing='CU', expr='grin', pose='point')
B('He pulled it off with an entire fleet', 'ships', n=13, ship='turtle_ship', label=('AN ENTIRE FLEET',), until='Okay, quick pause')

# ===================================== MID-ROLL =====================================
HO('Okay, quick pause', framing='CU', expr='nervous', pose='chin')
B('This video was supposed to have ten', 'text', until='It got way too long', lines=[
    ('10 DEATHS', 'white', 0.12 * H, None, T('not five')), ('5 DEATHS', 'red', 0.12 * H, T('not five'))])
HO('It got way too long', pose='shrug', expr='grimace')
HO('And the five that got cut', framing='CU', expr='grin', pose='point')
B("We're talking about a Viking", 'stage', until='and one of the greatest generals',
  actors=[A(VIK_ARMOR, 960, R=120, expr='shock', pose='cheeks', enter=pop(T('a Viking')))],
  props=[P('icon', 1260, 360, 70, kw=dict(kind='question'), enter=pop(T('already beheaded')))],
  tags=[tagp('KILLED BY A MAN HE BEHEADED', 960, 330, T('already beheaded'))])
B('one of the greatest generals', 'photo', img='pyrrhus', mode='frame', focus=(0.5, 0.35), until='by an old woman',
  caption='PYRRHUS', cap_at=T('generals'))
B('by an old woman with a roof tile', 'stage', until='Some of them sound',
  actors=[A(OLD_WOMAN, 760, R=110, pose='cheer', expr='evil', enter=pop(T('old woman')))],
  props=[P('tile', 1250, 420, 130, rot=-30, enter=dict(kind='fly', at=T('roof tile'), frm=(820, 520), dur=10), acts=[act('spin', T('roof tile'), speed=14)])])
HO('Some of them sound fake', pose='chin', expr='skeptic')
HO("They're not", framing='ECU', expr='smug', pose='hips')
HO('Part two is already mapped', pose='point', expr='talk')
B('drop a comment that says', 'comment', text='PART TWO', until='And if we get this video')
B('And if we get this video to 25,000', 'count', to=25000, label='LIKES = PART TWO', until='Alright', dur=36)
HO('Alright', framing='CU', expr='smile', pose='wave')
HO('Well, the final entry', pose='hips', expr='grin')


# ===================================== #5 YI SUN-SIN =====================================
B('Yi Sun-sin.', 'title', num=5, name=['YI', 'SUN-SIN'], img='hundred_won', focus=(0.235, 0.5), zoom=1.9, hold=1.7)
HO('Quick question', pose='chin', expr='skeptic')
HO("Who's the greatest admiral", framing='CU', expr='talk', pose='point')
B('If you said Horatio Nelson', 'photo', img='nelson', mode='frame', focus=(0.5, 0.3), until='If you said Captain',
  caption='HORATIO NELSON', cap_at=T('Nelson'))
B('If you said Captain Hook', 'stage', until='please leave',
  actors=[A(HOOK, 960, R=124, pose='hips', expr='smug', enter=pop(T('Captain Hook')))],
  tags=[tagp('CAPTAIN HOOK', 960, 330, T('Hook'))])
HO('please leave', framing='ECU', expr='deadpan', pose='point')
HO("But there's a name a lot of", pose='chin', expr='talk')
B('most people outside Korea', 'map', region='korea', highlight=('South Korea', 'North Korea'), until='And his death is',
  labels=[('KOREA', (0.32, 0.30), T('outside Korea'))])
HO('And his death is, in my opinion', framing='CU', expr='talk', pose='point')
C('the most epic death in recorded', 'THE MOST EPIC DEATH IN HISTORY', hold=2.0)
C('In 1592', '1592', hold=1.4)
B('Japan invades Korea with', 'map', region='korea', icon='jp_ship', until='On land', highlight=('South Korea', 'North Korea', 'Japan'),
  stops=[('Japan', 'JAPAN', T('Japan invades')), ('Busan', 'BUSAN', T('invades Korea'))])
C('150,000 soldiers', '150,000+ SOLDIERS', hold=1.8)
B("On land, it's a disaster", 'photo', img='busanjin', mode='full', focus=(0.5, 0.5), until='The capital, Seoul',
  caption='1592: THE INVASION', cap_at=T('disaster'))
B('The capital, Seoul, falls', 'map', region='korea', until='But at sea', highlight=('South Korea', 'North Korea'),
  stops=[('Busan', 'BUSAN', T('The capital')), ('Seoul', 'SEOUL: FALLEN', T('falls in'))])
C('three weeks', '~3 WEEKS', hold=1.4)
B('But at sea, one Korean admiral', 'scene', bg='seoul_gwanghwamun', focus=(0.5, 0.5), blur=4.0, gain=0.5, until='He brings out ships',
  actors=[A(YI, 960, R=126, pose='hips', expr='smug', enter=pop(T('one Korean admiral')))],
  tags=[tagp('YI SUN-SIN', 960, 330, T('admiral starts'))],
  fx=[dict(kind='text', t='WIN', x=560, y=420, at=T('starts winning'), cap=0.075 * H, style='red', stroke=10),
      dict(kind='text', t='WIN', x=1380, y=520, at=T('keeps winning'), cap=0.075 * H, style='red', stroke=10),
      dict(kind='text', t='WIN', x=600, y=700, at=T('keeps winning', off=5), cap=0.075 * H, style='red', stroke=10),
      dict(kind='text', t='WIN', x=1330, y=820, at=T('keeps winning', off=10), cap=0.075 * H, style='red', stroke=10)])
B('He brings out ships the Japanese', 'photo', img='turtle_ship', mode='full', focus=(0.45, 0.5), until='covered decks studded',
  caption='TURTLE SHIPS', cap_at=T('turtle ships'))
B('covered decks studded with iron', 'photo', img='turtle_ship', mode='frame', focus=(0.45, 0.5), until='At Hansan Island',
  marks=[('label', 'IRON SPIKES', 0.55, 0.30, T('iron spikes')), ('arrow', 0.55, 0.30, 0.55, 0.38, T('iron spikes')),
         ('label', 'CANNONS', 0.45, 0.80, T('cannons')), ('arrow', 0.45, 0.80, 0.48, 0.62, T('cannons')),
         ('label', 'DRAGON HEAD', 0.17, 0.12, T("dragon's head")), ('ring', 0.12, 0.27, 0.07, 0.12, T("dragon's head"))])
B('At Hansan Island', 'map', region='korea', focus='Hansan', zoom=1.9, until='he lured a Japanese', highlight=('South Korea',),
  pins=[('Hansan', 'HANSAN ISLAND', T('Hansan'))])
B('he lured a Japanese fleet', 'formation', bg='night_sea', until='His wins cut', wrap=T('wrapped his ships'), wipe=T('wiped most'))
B("His wins cut Japan's supply", 'map', region='korea', until='By most counts', highlight=('South Korea', 'Japan'),
  stops=[('Japan', 'JAPAN', T('His wins')), ('Busan', 'SUPPLY LINES', T('supply lines'))],
  labels=[('CUT.', (0.62, 0.42), T('by sea'))])
B('By most counts, Yi fought', 'count', to=23, prefix='~', label='NAVAL BATTLES', until='And as a reward', dur=24)
C('never losing a single one', 'LOSSES: 0', hold=1.8)
B('his own government arrested him', 'scene', bg='gyeongbokgung', focus=(0.5, 0.55), until='Earlier in his career',
  actors=[A(YI, 960, R=112, expr=[(None, 'shock'), (T('Again'), 'deadpan')])],
  props=[P('jail', 960, 660, 320, z=5, enter=drop(T('arrested him'), 800))], cam=[('shake', T('arrested him', off=10), 10)])
C('arrested him | Again', 'AGAIN.', hold=1.2)
B("he'd already been falsely accused", 'list', until='In 1597', items=[
    dict(text='FALSELY ACCUSED', mark='x', at=T('falsely accused')), dict(text='STRIPPED OF RANK', mark='x', at=T('stripped of his rank')),
    dict(text='COMMON SOLDIER', mark='x', at=T('common soldier'))])
C('In 1597', '1597', hold=1.4)
B('thanks to court politics', 'scene', bg='gyeongbokgung', focus=(0.5, 0.55), until='So he was hauled',
  actors=[A(YI, 760, R=110, pose='chin', expr='skeptic')],
  props=[P('icon', 1150, 450, 70, kw=dict(kind='question'), enter=pop(T('enemy tip')))],
  tags=[tagp('"IT\'S A TRAP."', 1150, 330, T('a trap')), tagp('ORDER: IGNORED', 760, 455, T("didn't follow"))])
B('So he was hauled to the capital', 'list', until='While he was on his way', items=[
    dict(text='HAULED TO THE CAPITAL', mark='x', at=T('hauled')), dict(text='TORTURED', mark='x', at=T('tortured')),
    dict(text='NEARLY EXECUTED', mark='x', at=T('nearly executed')), dict(text='DEMOTED (AGAIN)', mark='x', style='red', at=T('demoted'))])
B('While he was on his way', 'scene', bg='seoul_gwanghwamun', blur=5.0, gain=0.45, until='Meanwhile, his replacement',
  actors=[A(YI_SOLDIER, 960, R=110, pose='walk', expr=[(None, 'sad'), (T('his mother died'), 'cry')], enter=walk(T('on his way'), -300, 40))],
  tags=[tagp('NO TIME TO MOURN', 960, 440, T('keep going'))])
B('his replacement sailed almost', 'stage', until='Out of a fleet',
  props=[P('turtle_ship', 200 + 210 * k, 560 + 140 * (k % 2), 105, acts=[act('move', T('straight into'), to=(700 + 210 * k, 560 + 140 * (k % 2)), dur=40)])
         for k in range(3)]
  + [P('jp_ship', 1480 + 150 * (k % 2), 380 + 170 * k, 100, flip=True, enter=pop(T('Japanese ambush', off=2 * k))) for k in range(4)],
  tags=[tagp('AMBUSH', 1560, 300, T('ambush'))])
B('Out of a fleet that had grown', 'ships', n=160, n2=12, ship='turtle_ship', change=T('about a dozen'), label=('160 WARSHIPS', '12 ESCAPED'),
  until='So the king, out of')
B('So the king, out of options', 'scene', bg='gyeongbokgung', focus=(0.5, 0.55), until='Yi wrote back',
  actors=[A(JOSEON_KING, 700, R=108, expr=[(None, 'nervous'), (T('giving up'), 'grimace')], pose='shrug'),
          A(YI, 1220, R=108, flip=True, expr='smug', enter=walk(T('his old job'), 2300, 24))],
  tags=[tagp('THE KING', 700, 455, T('So the king'))],
  says=[say('"MAYBE... NO NAVY?"', 700, 330, T('giving up'), T('Yi wrote back', cut=True))])
HO('Yi wrote back with one', pose='point', expr='talk')
B('Your servant still has twelve', 'quote', text='Your servant still has twelve ships.', quote_at='Your servant', who='Yi Sun-sin, 1597',
  bg='yi_statue', until='Twelve. Plus one')
B('Twelve. Plus one more', 'ships', n=12, ship='turtle_ship', label=('12 SHIPS',), until='Thirteen ships, against')
B('Thirteen ships, against', 'ships', n=13, ship='turtle_ship', label=('13 SHIPS VS. A NAVY',), until='At the Battle of Myeongnyang')
B('At the Battle of Myeongnyang', 'map', region='korea', focus='Myeongnyang', zoom=2.0, until='he faced at least', highlight=('South Korea',),
  pins=[('Myeongnyang', 'MYEONGNYANG', T('Myeongnyang'))])
B('he faced at least 133', 'versus', until='Before the battle',
  left=dict(lines=[('YI:', 'white'), ('13 SHIPS', 'red')], at=T('he faced'), cap=0.085 * H),
  right=dict(lines=[('JAPAN:', 'white'), ('133 WARSHIPS', 'red'), ('+ ~200 SUPPORT', 'silver')], at=T('133 Japanese'), cap=0.085 * H))
B('Those who seek death', 'quote', text='Those who seek death shall live, and those who seek life shall die.', quote_at='Those who seek death',
  who='Yi Sun-sin', bg='yi_statue', until='He picked his battlefield')
B('He picked his battlefield', 'photo', img='myeongnyang', mode='full', focus=(0.6, 0.5), until="And here's the part that gets me",
  caption='THE MYEONGNYANG STRAIT', cap_at=T('narrow strait'),
  marks=[('arrow', 0.30, 0.35, 0.70, 0.30, T('fiercest tidal')), ('arrow', 0.75, 0.55, 0.40, 0.62, T('tidal currents'))])
HO("And here's the part that gets me", framing='CU', expr='talk', pose='point')
B('most of his captains hung back', 'stage', until='So for a while',
  props=[P('turtle_ship', 1250 + 230 * k, 520 + 170 * k, 100, flip=True, acts=[act('bob', 0)]) for k in range(3)],
  actors=[A(YI_SOLDIER, 600, R=110, expr='nervous', acts=[act('shake', T('terrified'), dur=20)])],
  tags=[tagp('HIS CAPTAINS: NOPE', 1480, 360, T('hung back'))])
B("Yi's flagship held off", 'stage', until='Then the tide turned',
  props=[P('turtle_ship', 520, 640, 160, acts=[act('bob', 0)])]
  + [P('jp_ship', 1160 + 150 * k, 330 + 150 * k, 105, flip=True, acts=[act('bob', 0)]) for k in range(5)]
  + [P('turtle_ship', 230, 330 + 560 * k, 95, enter=dict(kind='slide', at=T('found the nerve', off=3 * k), frm=-300, dur=14)) for k in range(2)],
  tags=[tagp('ALONE', 520, 460, T('pretty much alone'))])
B('Then the tide turned', 'text', anim='slam', until='The Japanese ships started', lines=[('THE TIDE TURNED', 'white', 0.11 * H),
                                                                                       ('(LITERALLY)', 'red', 0.07 * H, T('turned', off=6))])
B('The Japanese ships started drifting', 'stage', until='When it was over',
  props=[P('jp_ship', 1000 + 200 * k, 380 + 150 * k, 110, flip=True,
           acts=[act('move', T('drifting backward'), to=(1180 + 200 * k, 420 + 130 * k), dur=40), act('shake', T('crashing'), dur=20)]) for k in range(4)]
  + [P('turtle_ship', 260 + 120 * k, 420 + 190 * k, 100, acts=[act('move', T('tore into'), to=(720 + 120 * k, 440 + 170 * k), dur=26)]) for k in range(3)],
  fx=[dict(kind='fire', x=1250, y=420, size=60, at=T('crashing')), dict(kind='fire', x=1450, y=560, size=50, at=T('each other'))],
  cam=[('shake', T('crashing into'), 12)])
B('When it was over, 31', 'list', until='Weeks later', items=[
    dict(text='JAPANESE SHIPS WRECKED: 31', at=T('31 Japanese'), mark='check'),
    dict(text='KOREAN SHIPS LOST: 0', at=T("Yi didn't lose"), mark='check', style='red')])
HO('Weeks later, Japanese troops', pose='idle', expr='sad')
B('In his war diary', 'photo', img='nanjung_ilgi', mode='doc', focus=(0.5, 0.5), until='And then he kept fighting',
  caption="YI'S WAR DIARY", cap_at=T('war diary'))
HO('And then he kept fighting anyway', framing='CU', expr='angry', pose='hips')
C('Which brings us to 1598', '1598', hold=1.4)
B("Japan's ruler has died", 'photo', img='hideyoshi', mode='frame', focus=(0.5, 0.3), until='Plenty of commanders',
  caption='TOYOTOMI HIDEYOSHI (DIED 1598)', cap_at=T('ruler'))
HO('Plenty of commanders would', pose='shrug', expr='talk')
HO("Yi didn't", framing='ECU', expr='angry', pose='hips')
C('On December 16th', 'DECEMBER 16, 2 AM', hold=2.0)
B('hit the Japanese fleet in the Noryang', 'map', region='korea', focus='Noryang', zoom=2.0, until='The fighting raged', highlight=('South Korea',),
  pins=[('Noryang', 'NORYANG STRAIT', T('Noryang'))])
B('The fighting raged until daylight', 'scene', bg='night_sea', gain=0.5, until='And as the Japanese ships',
  props=[P('jp_ship', 1300, 620, 150, flip=True, acts=[act('bob', 0)]), P('turtle_ship', 600, 700, 170, acts=[act('bob', 0)])],
  fx=[dict(kind='fire', x=1250, y=600, size=60), dict(kind='flash', at=T('raged', off=4), dur=4, amp=0.3, color='#FFB060')])
B('a bullet struck Yi in the chest', 'scene', bg='night_sea', gain=0.45, until='He knew right away',
  actors=[A(YI, 960, R=124, expr=[(None, 'angry'), (T('struck'), 'shock')], pose=[(None, 'point'), (T('struck'), 'cheeks')])],
  fx=[dict(kind='flash', at=T('bullet'), dur=4, color='#FFFFFF', amp=0.6), dict(kind='vignette_red', at=T('in the chest'))],
  cam=[('shake', T('bullet'), 18)])
HO('He knew right away', framing='CU', expr='sad', pose='idle')
B('The battle is at its height', 'quote', text='The battle is at its height. Do not announce my death.', quote_at='The battle is at its',
  who='Yi Sun-sin, 1598', bg='yi_statue', until='He was fifty-three')
STAMP('He was fifty-three', 'DEATH #5', sub='AGE 53, MID-BATTLE', y=0.52 * H, hold=2.2)
HO('His son and his nephew carried', pose='idle', expr='sad')
B('Then his nephew picked up the war drum', 'scene', bg='turtle_ship', focus=(0.22, 0.48), zoom=1.15, gain=0.95, sat=0.7, night=True,
  blur=0.8, until='Nobody knew',
  props=[P('drum', 1560, 820, 128, z=2, kw=dict(hit=False))],
  actors=[A(NEPHEW, 1250, R=104, pose='drum', expr='angry', z=3)],
  fx_under=[dict(kind='glow', x=1500, y=900, r=760, a=150), dict(kind='glow', x=250, y=980, r=520, a=110)],
  fx=[dict(kind='fire', x=180, y=960, size=74), dict(kind='fire', x=520, y=990, size=56), dict(kind='embers', x0=0, x1=W, n=50)],
  tags=[tagp('HIS NEPHEW', 1250, 440, T('his nephew'))], drum=True)
B('Nobody knew', 'scene', bg='turtle_ship', focus=(0.22, 0.48), zoom=1.15, gain=0.95, sat=0.7, night=True, blur=0.8,
  until='The fleet fought on',
  props=[P('drum', 1560, 820, 128, z=2, kw=dict(hit=False))],
  actors=[A(NEPHEW, 1250, R=104, pose='drum', expr='angry', z=3)],
  fx_under=[dict(kind='glow', x=1500, y=900, r=760, a=150)],
  fx=[dict(kind='fire', x=180, y=960, size=74), dict(kind='embers', x0=0, x1=W, n=50)],
  tags=[tagp('HIS SAILORS: NO IDEA', 560, 300, T('Not his sailors')), tagp('THE ENEMY: NO IDEA', 1300, 200, T('Not the enemy'))], drum=True)
B('The fleet fought on and won', 'text', anim='slam', until='Korean records claim', lines=[('THE FLEET', 'white', 0.1 * H),
                                                                                          ('WON.', 'red', 0.16 * H, T('and won'))],
  cam=[('shake', T('and won'), 12)])
HO('Korean records claim hundreds', pose='point', expr='talk')
C('hundreds of Japanese ships', 'HUNDREDS OF SHIPS DESTROYED', hold=2.0)
B('It was the last major battle', 'text', until='Afterward, the Chinese admiral', bg='yi_statue',
  lines=[('THE LAST BIG BATTLE', 'white', 0.08 * H), ('OF A 7-YEAR WAR', 'red', 0.1 * H, T('seven-year'))])
B('Afterward, the Chinese admiral Chen Lin', 'stage', until='When they told him',
  actors=[A(CHEN_LIN, 960, R=124, expr='smile', pose='wave', enter=walk(T('Chen Lin'), 2300, 26))],
  tags=[tagp('CHEN LIN (CHINA)', 960, 330, T('Chen Lin'))])
B('When they told him Yi was dead', 'stage', until='Think about that',
  actors=[A(CHEN_LIN, 960, R=124, expr=[(None, 'shock'), (T('fell to the deck'), 'cry')],
            acts=[act('fall', T('three times'), dur=6), act('hop', T('beating his chest'), dur=10), act('pose', T('beating'), pose='cheeks')])],
  tags=[tagp('x3', 1240, 420, T('three times'))])
HO('Think about that', framing='CU', expr='talk', pose='chin')
B('Arrichion won one fight after he died', 'versus', until='Korea gave him',
  left=dict(img='olympia_stadium', lines=[('ARRICHION:', 'white'), ('WON 1 FIGHT', 'red')], at=T('Arrichion won')),
  right=dict(img='turtle_ship', focus=(0.3, 0.5), lines=[('YI SUN-SIN:', 'white'), ('WON A WAR', 'red')], at=T('Yi Sun-sin won')))
B('Korea gave him the title', 'text', until='One of the most-watched', bg='yi_statue',
  lines=[('CHUNGMUGONG', 'white', 0.11 * H, T('Chungmugong')), ('"LORD OF LOYALTY AND WARFARE"', 'red', 0.055 * H, T('Lord of Loyalty'))])
HO('One of the most-watched movies', pose='point', expr='grin')
C('about his thirteen ships', 'A HIT MOVIE ABOUT 13 SHIPS', hold=2.0)
B('His face is on the 100-won coin', 'photo', img='hundred_won', mode='frame', focus=(0.28, 0.5), until='and his statue stands',
  caption='100-WON COIN', cap_at=T('100-won coin'))
B('and his statue stands in the heart', 'photo', img='yi_statue', mode='full', focus=(0.5, 0.45), until='He earned all of it',
  caption='CENTRAL SEOUL', cap_at=T('heart of Seoul'))
HO('He earned all of it', framing='CU', expr='smile', pose='hips')

# ===================================== OUTRO =====================================
HO("So, that's part one", pose='wave', expr='smile')
B('Five deaths', 'gallery', until='If you already knew', people=[
    dict(img='harald_portrait', focus=(0.62, 0.42), zoom=1.2, label=['NO ARMOR', 'DAY'], at=T('A Viking king')),
    dict(img='leo_attila', focus=(0.53, 0.47), zoom=2.4, label=['A', 'NOSEBLEED'], at=T('A warlord')),
    dict(img='crassus_bust', focus=(0.5, 0.35), label=['THEATER', 'PROP'], at=T("Rome's richest")),
    dict(img='pankration_vase', focus=(0.5, 0.42), label=['CROWNED', 'CORPSE'], at=T('An Olympic champion')),
    dict(img='hundred_won', focus=(0.235, 0.5), zoom=1.9, label=['WON AFTER', 'DEATH'], at=T('And an admiral'))])
HO('If you already knew all five', pose='point', expr='grin')
HO("If you didn't, good news", framing='CU', expr='smile', pose='wave')
C('part two is mapped out', 'PART TWO: COMING', hold=1.8)
HO('Now, a quick recap of the life', pose='hips', expr='talk')
B("If you're invading England", 'text', bg='stamford_arbo', until="I don't care how nice",
  lines=[('LIFE LESSON #1', 'silver', 0.05 * H), ('WEAR THE ARMOR.', 'red', 0.12 * H, T('wear the armor'))])
HO("I don't care how nice", framing='CU', expr='smug', pose='hips')
B("If you're the most feared man on Earth", 'text', bg='feast_attila', until="If you're already the richest",
  lines=[('LIFE LESSON #2', 'silver', 0.05 * H), ('PACE YOURSELF.', 'red', 0.12 * H, T('pace yourself'))])
HO("If you're already the richest guy", pose='point', expr='talk')
B('Just buy a boat', 'text', bg='carrhae', until='If your coach starts',
  lines=[('LIFE LESSON #3', 'silver', 0.05 * H), ('JUST BUY A BOAT.', 'red', 0.12 * H, T('buy a boat'))])
B('If your coach starts talking', 'text', bg='olympia_stadium', until='And if anybody ever tells',
  lines=[('LIFE LESSON #4', 'silver', 0.05 * H), ('FIND A NEW COACH.', 'red', 0.12 * H, T('find a new coach'))])
HO('And if anybody ever tells you', pose='chin', expr='talk')
B('find a narrow strait and prove', 'text', bg='myeongnyang', until='Sources: a pile',
  lines=[('LIFE LESSON #5', 'silver', 0.05 * H), ('12 SHIPS IS ENOUGH.', 'red', 0.12 * H, T('prove them wrong'))])
B('Sources: a pile of ancient', 'band', text='SOURCES:', until='Ever.',
  photos=[('heimskringla', 0.2 * W, 0.62 * H, 0.22 * W, T('a pile'), None, (0.5, 0.4)),
          ('anglo_saxon_chronicle', 0.5 * W, 0.62 * H, 0.22 * W, T('ancient historians'), None, (0.5, 0.3)),
          ('snorri', 0.8 * W, 0.62 * H, 0.22 * W, T('definitely never'), None, (0.5, 0.3))],
  label_y=0.965 * H, label_w=0.22 * W,
  photo_labels=[('TRUST ME', 0.2 * W, T('never exaggerated')), ('TRUST ME', 0.5 * W, T('exaggerated')), ('TRUST ME', 0.8 * W, T('anything'))])
HO('exaggerated anything | Ever', framing='ECU', expr='deadpan', pose='idle')
B("And if it's two in the morning", 'end', exprs=[(0, 'smile')], slot_at=T('the video on your screen'))
